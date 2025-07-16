#!/usr/bin/env python3
"""
ML Model Training Script for QuantumVestAI.
This script handles the retraining of machine learning models using the latest data.
"""

import argparse
import datetime
import json
import logging
import os
import sys
import time
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from tensorflow import keras

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('model-training')

class ModelTrainer:
    """Main model training class that handles the retraining workflow."""
    
    def __init__(self, models_path='/app/models', s3_bucket=None):
        """Initialize the model trainer."""
        self.models_path = Path(models_path)
        self.models_path.mkdir(parents=True, exist_ok=True)
        self.s3_bucket = s3_bucket
        
        # Database connection
        self.db_user = os.environ.get('DB_USER', os.environ.get('POSTGRES_USER'))
        self.db_password = os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD'))
        self.db_host = os.environ.get('DB_HOST', os.environ.get('POSTGRES_SERVER', 'db'))
        self.db_port = os.environ.get('DB_PORT', os.environ.get('POSTGRES_PORT', '5432'))
        self.db_name = os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB'))
        
        # Connect to database
        self.db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.engine = create_engine(self.db_url)
        
        # AWS S3 client for model storage
        if self.s3_bucket:
            self.s3_client = boto3.client('s3')
    
    def load_data(self):
        """Load training data from the database."""
        logger.info("Loading stock price data from the database...")
        
        # Example query to get stock price data
        query = """
        SELECT 
            sp.stock_id, s.ticker, sp.date, sp.open, sp.high, sp.low, sp.close, sp.adjusted_close, sp.volume
        FROM 
            stock_prices sp
        JOIN
            stocks s ON sp.stock_id = s.id
        WHERE
            sp.date >= (CURRENT_DATE - INTERVAL '3 years')
        ORDER BY
            s.ticker, sp.date
        """
        
        try:
            # Read data from database
            df = pd.read_sql(query, self.engine)
            logger.info(f"Loaded {len(df)} stock price records for training")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def preprocess_data(self, df):
        """Preprocess the data for model training."""
        logger.info("Preprocessing data...")
        
        # Group by ticker and preprocess each stock's data
        stocks = []
        for ticker, group in df.groupby('ticker'):
            # Sort by date
            group = group.sort_values('date')
            
            # Calculate features (example)
            group['returns'] = group['adjusted_close'].pct_change()
            group['log_returns'] = np.log(group['adjusted_close'] / group['adjusted_close'].shift(1))
            group['ma_5'] = group['adjusted_close'].rolling(window=5).mean()
            group['ma_20'] = group['adjusted_close'].rolling(window=20).mean()
            group['ma_50'] = group['adjusted_close'].rolling(window=50).mean()
            group['volatility'] = group['returns'].rolling(window=20).std()
            
            # Drop NAs from feature calculation
            group = group.dropna()
            
            if len(group) > 60:  # Ensure we have enough data
                stocks.append((ticker, group))
        
        logger.info(f"Preprocessed data for {len(stocks)} stocks")
        return stocks
    
    def train_lstm_model(self, stock_data, ticker, lookback=60, epochs=50, batch_size=32):
        """Train an LSTM model for a specific stock."""
        logger.info(f"Training LSTM model for {ticker}...")
        
        # Prepare data for LSTM
        data = stock_data[['adjusted_close', 'returns', 'ma_5', 'ma_20', 'ma_50', 'volatility']].values
        
        # Normalize data
        mean = data.mean(axis=0)
        std = data.std(axis=0)
        data_normalized = (data - mean) / std
        
        # Create sequences
        X = []
        y = []
        
        for i in range(lookback, len(data_normalized)):
            X.append(data_normalized[i-lookback:i])
            y.append(data_normalized[i, 0])  # Predict normalized close price
        
        X = np.array(X)
        y = np.array(y)
        
        # Split into train and validation
        split = int(0.8 * len(X))
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        
        # Build LSTM model
        model = keras.Sequential([
            keras.layers.LSTM(50, return_sequences=True, input_shape=(lookback, data.shape[1])),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(50),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train model
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            verbose=1
        )
        
        # Save model
        model_path = self.models_path / f"lstm_{ticker}.h5"
        model.save(model_path)
        
        # Save normalization parameters
        params = {
            'mean': mean.tolist(),
            'std': std.tolist(),
            'lookback': lookback,
            'features': ['adjusted_close', 'returns', 'ma_5', 'ma_20', 'ma_50', 'volatility'],
            'training_date': datetime.datetime.now().isoformat(),
            'ticker': ticker
        }
        
        with open(self.models_path / f"lstm_{ticker}_params.json", 'w') as f:
            json.dump(params, f)
        
        # Upload to S3 if configured
        if self.s3_bucket:
            try:
                self.s3_client.upload_file(
                    str(model_path), 
                    self.s3_bucket, 
                    f"models/lstm_{ticker}.h5"
                )
                self.s3_client.upload_file(
                    str(self.models_path / f"lstm_{ticker}_params.json"), 
                    self.s3_bucket, 
                    f"models/lstm_{ticker}_params.json"
                )
                logger.info(f"Uploaded model for {ticker} to S3 bucket {self.s3_bucket}")
            except Exception as e:
                logger.error(f"Error uploading model to S3: {e}")
        
        return model, history
    
    def train_all_models(self, full_retrain=False):
        """Train models for all stocks."""
        logger.info("Starting training for all stocks...")
        start_time = time.time()
        
        # Load and preprocess data
        df = self.load_data()
        stocks_data = self.preprocess_data(df)
        
        # Train models for each stock
        models = {}
        for ticker, stock_data in stocks_data:
            try:
                # Check if we need to train this model
                model_path = self.models_path / f"lstm_{ticker}.h5"
                if not full_retrain and model_path.exists():
                    logger.info(f"Skipping {ticker}, model already exists (use --full-retrain to override)")
                    continue
                
                model, history = self.train_lstm_model(stock_data, ticker)
                models[ticker] = model
                logger.info(f"Successfully trained model for {ticker}")
            except Exception as e:
                logger.error(f"Error training model for {ticker}: {e}")
                continue
        
        # Record training completion
        training_record = {
            "completed_at": datetime.datetime.now().isoformat(),
            "duration_minutes": (time.time() - start_time) / 60,
            "models_trained": len(models),
            "total_stocks": len(stocks_data)
        }
        
        with open(self.models_path / "training_record.json", 'w') as f:
            json.dump(training_record, f)
        
        logger.info(f"Training completed in {training_record['duration_minutes']:.2f} minutes")
        logger.info(f"Successfully trained {len(models)} models out of {len(stocks_data)} stocks")
        
        return models


def main():
    """Main function for command line execution."""
    parser = argparse.ArgumentParser(description="Train machine learning models for stock prediction")
    parser.add_argument('--full-retrain', action='store_true', help='Retrain all models even if they exist')
    parser.add_argument('--all-models', action='store_true', help='Train all model types')
    parser.add_argument('--models-path', type=str, default=os.environ.get('MODELS_STORAGE_PATH', '/app/models'),
                       help='Path to save trained models')
    parser.add_argument('--s3-bucket', type=str, default=os.environ.get('S3_MODEL_BUCKET'),
                       help='S3 bucket to upload trained models')
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = ModelTrainer(models_path=args.models_path, s3_bucket=args.s3_bucket)
    
    # Train models
    try:
        trainer.train_all_models(full_retrain=args.full_retrain)
        logger.info("Model training completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
