"""
Module for accessing trained machine learning models.
"""

import json
import logging
import os
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
from tensorflow import keras

# Set up logging
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manager class for ML models.
    Handles loading, prediction and model metadata access.
    """
    
    def __init__(self, models_path='/app/models', s3_bucket=None):
        """Initialize the model manager."""
        self.models_path = Path(models_path)
        self.s3_bucket = s3_bucket
        self.models = {}
        self.model_params = {}
        
        # AWS S3 client for model storage
        if self.s3_bucket:
            self.s3_client = boto3.client('s3')
    
    def list_available_models(self):
        """List available models for all tickers."""
        # Check local models
        model_files = list(self.models_path.glob("lstm_*.h5"))
        available_models = {}
        
        for model_file in model_files:
            # Extract ticker from filename (lstm_AAPL.h5 -> AAPL)
            ticker = model_file.stem.split('_', 1)[1]
            
            # Load model parameters
            param_file = self.models_path / f"lstm_{ticker}_params.json"
            if param_file.exists():
                with open(param_file, 'r') as f:
                    params = json.load(f)
                    available_models[ticker] = {
                        "model_type": "lstm",
                        "training_date": params.get("training_date"),
                        "available_locally": True
                    }
        
        # Check S3 models if configured
        if self.s3_bucket:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix="models/lstm_"
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        key = obj['Key']
                        if key.endswith('.h5'):
                            # Extract ticker from key (models/lstm_AAPL.h5 -> AAPL)
                            ticker = key.split('_', 1)[1].split('.')[0]
                            
                            # Add to available models if not already there
                            if ticker not in available_models:
                                available_models[ticker] = {
                                    "model_type": "lstm",
                                    "last_modified": obj['LastModified'].isoformat(),
                                    "available_locally": False,
                                    "s3_path": key
                                }
            except Exception as e:
                logger.error(f"Error checking S3 for models: {e}")
        
        return available_models
    
    def load_model(self, ticker):
        """Load a model for a specific ticker."""
        if ticker in self.models:
            return self.models[ticker]
        
        # Check if model exists locally
        model_path = self.models_path / f"lstm_{ticker}.h5"
        param_path = self.models_path / f"lstm_{ticker}_params.json"
        
        # Download from S3 if needed
        if not model_path.exists() and self.s3_bucket:
            try:
                logger.info(f"Downloading model for {ticker} from S3...")
                self.s3_client.download_file(
                    self.s3_bucket,
                    f"models/lstm_{ticker}.h5",
                    str(model_path)
                )
                self.s3_client.download_file(
                    self.s3_bucket,
                    f"models/lstm_{ticker}_params.json",
                    str(param_path)
                )
            except Exception as e:
                logger.error(f"Error downloading model from S3: {e}")
                raise FileNotFoundError(f"Model for {ticker} not found locally or in S3")
        
        # If the model still doesn't exist, raise an error
        if not model_path.exists() or not param_path.exists():
            raise FileNotFoundError(f"Model for {ticker} not found")
        
        # Load model parameters
        with open(param_path, 'r') as f:
            params = json.load(f)
            self.model_params[ticker] = params
        
        # Load model
        self.models[ticker] = keras.models.load_model(model_path)
        logger.info(f"Loaded model for {ticker}")
        
        return self.models[ticker]
    
    def predict(self, ticker, historical_data, days_ahead=5):
        """
        Make predictions for a specific stock.
        
        Args:
            ticker: Stock ticker symbol
            historical_data: DataFrame with at least 60 days of historical data
            days_ahead: Number of days to forecast
            
        Returns:
            DataFrame with predicted prices
        """
        # Load model and parameters
        model = self.load_model(ticker)
        params = self.model_params[ticker]
        
        # Ensure we have the required columns
        required_features = params['features']
        missing_features = [f for f in required_features if f not in historical_data.columns]
        
        if missing_features:
            # Calculate missing features
            if 'returns' in missing_features and 'adjusted_close' in historical_data.columns:
                historical_data['returns'] = historical_data['adjusted_close'].pct_change()
            
            if 'log_returns' in missing_features and 'adjusted_close' in historical_data.columns:
                historical_data['log_returns'] = np.log(historical_data['adjusted_close'] / historical_data['adjusted_close'].shift(1))
            
            if 'ma_5' in missing_features and 'adjusted_close' in historical_data.columns:
                historical_data['ma_5'] = historical_data['adjusted_close'].rolling(window=5).mean()
                
            if 'ma_20' in missing_features and 'adjusted_close' in historical_data.columns:
                historical_data['ma_20'] = historical_data['adjusted_close'].rolling(window=20).mean()
                
            if 'ma_50' in missing_features and 'adjusted_close' in historical_data.columns:
                historical_data['ma_50'] = historical_data['adjusted_close'].rolling(window=50).mean()
                
            if 'volatility' in missing_features and 'returns' in historical_data.columns:
                historical_data['volatility'] = historical_data['returns'].rolling(window=20).std()
        
        # Drop NaNs
        historical_data = historical_data.dropna()
        
        # Get the lookback window size
        lookback = params['lookback']
        
        # Ensure we have enough data
        if len(historical_data) < lookback:
            raise ValueError(f"Not enough historical data. Need at least {lookback} rows.")
        
        # Extract the feature data
        data = historical_data[required_features].values
        
        # Normalize using saved parameters
        mean = np.array(params['mean'])
        std = np.array(params['std'])
        normalized_data = (data - mean) / std
        
        # Make predictions
        last_sequence = normalized_data[-lookback:]
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(days_ahead):
            # Reshape for model input (1 sample, lookback steps, features)
            X = current_sequence.reshape(1, lookback, len(required_features))
            
            # Predict next normalized price
            pred_normalized = model.predict(X, verbose=0)[0, 0]
            
            # Convert back to original scale
            pred_original = pred_normalized * std[0] + mean[0]
            predictions.append(pred_original)
            
            # Update sequence for next prediction
            # Create a new row with the predicted close price
            new_row = current_sequence[-1].copy()
            new_row[0] = pred_normalized  # Set normalized close price
            
            # Roll the window forward
            current_sequence = np.vstack([current_sequence[1:], new_row])
        
        # Create prediction DataFrame
        last_date = historical_data.index[-1]
        pred_dates = pd.date_range(start=last_date, periods=days_ahead+1)[1:]
        
        predictions_df = pd.DataFrame({
            'date': pred_dates,
            'predicted_close': predictions
        })
        
        predictions_df = predictions_df.set_index('date')        return predictions_df
