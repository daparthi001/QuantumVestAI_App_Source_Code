"""
LSTM Model for Stock Price Prediction
Created: 2025-06-19 03:09:13
Author: daparthi001
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential, load_model

logger = logging.getLogger("api.ml")

class LSTMStockModel:
    """LSTM model for stock price prediction"""
    
    def __init__(
        self,
        model_id: str,
        sequence_length: int = 60,
        prediction_days: int = 30,
        features: Optional[List[str]] = None
    ):
        self.model_id = model_id
        self.sequence_length = sequence_length
        self.prediction_days = prediction_days
        self.features = features or ['close', 'volume', 'open', 'high', 'low']
        self.model = None
        self.scaler = None
        self.model_path = f"models/lstm_{model_id}.h5"
        self.scaler_path = f"models/scaler_{model_id}.pkl"
        
    def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess data for LSTM model"""
        # Extract features
        dataset = data[self.features].values
        
        # Scale the data
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(dataset)
        
        # Create sequences
        x_train, y_train = [], []
        for i in range(self.sequence_length, len(scaled_data) - self.prediction_days):
            x_train.append(scaled_data[i - self.sequence_length:i])
            y_train.append(scaled_data[i:i + self.prediction_days, 0])  # Predict 'close' price
            
        return np.array(x_train), np.array(y_train)
    
    def build_model(self, input_shape: Tuple[int, int]) -> None:
        """Build LSTM model architecture"""
        self.model = Sequential()
        
        # LSTM layers
        self.model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        self.model.add(Dropout(0.2))
        
        self.model.add(LSTM(units=50, return_sequences=True))
        self.model.add(Dropout(0.2))
        
        self.model.add(LSTM(units=50))
        self.model.add(Dropout(0.2))
        
        # Output layer
        self.model.add(Dense(units=self.prediction_days))
        
        # Compile model
        self.model.compile(optimizer='adam', loss='mean_squared_error')
    
    def train(
        self, 
        data: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """Train the LSTM model"""
        # Preprocess data
        x_train, y_train = self.preprocess_data(data)
        
        # Build model if not already built
        if self.model is None:
            self.build_model((x_train.shape[1], x_train.shape[2]))
        
        # Early stopping and model checkpoint
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ModelCheckpoint(
                filepath=self.model_path,
                save_best_only=True,
                monitor='val_loss',
                mode='min'
            )
        ]
        
        # Train model
        history = self.model.fit(
            x_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=verbose
        )
        
        # Save scaler
        os.makedirs(os.path.dirname(self.scaler_path), exist_ok=True)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Return training history
        return {
            "model_id": self.model_id,
            "epochs": len(history.history['loss']),
            "final_loss": history.history['loss'][-1],
            "final_val_loss": history.history['val_loss'][-1],
            "training_complete": True
        }
    
    def load(self) -> bool:
        """Load saved model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = load_model(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                return True
            else:
                logger.warning(f"Model files not found: {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def predict(
        self, 
        data: pd.DataFrame, 
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """Make predictions for future stock prices"""
        if self.model is None:
            success = self.load()
            if not success:
                raise ValueError(f"Model {self.model_id} not found or could not be loaded")
        
        # Ensure we have enough data
        if len(data) < self.sequence_length:
            raise ValueError(f"Not enough data for prediction. Need at least {self.sequence_length} data points.")
        
        # Prepare data for prediction
        input_data = data[self.features].values
        scaled_data = self.scaler.transform(input_data)
        
        # Create sequence for prediction
        x_test = []
        x_test.append(scaled_data[-self.sequence_length:])
        x_test = np.array(x_test)
        
        # Make prediction
        scaled_prediction = self.model.predict(x_test)
        
        # Prepare the full input for inverse transform
        # We need to create a matrix with all features, but we're only changing the first column (close price)
        prediction_dates = []
        prediction_prices = []
        
        last_sequence = scaled_data[-self.sequence_length:].copy()
        current_date = datetime.strptime(data.index[-1], '%Y-%m-%d') if isinstance(data.index[-1], str) else data.index[-1]
        
        for i in range(min(days_ahead, self.prediction_days)):
            # Update the date
            current_date = current_date + timedelta(days=1)
            # Skip weekends
            while current_date.weekday() >= 5:  # 5: Saturday, 6: Sunday
                current_date = current_date + timedelta(days=1)
                
            prediction_dates.append(current_date.strftime('%Y-%m-%d'))
            
            # Get the predicted value
            pred_value = scaled_prediction[0][i]
            
            # Create a new row with the previous day's values but update the close price
            next_data_point = last_sequence[-1].copy()
            next_data_point[0] = pred_value
            
            # Append to the sequence
            last_sequence = np.vstack([last_sequence[1:], next_data_point])
            
            # Inverse transform to get the actual price
            actual_pred = self.scaler.inverse_transform(next_data_point.reshape(1, -1))[0][0]
            prediction_prices.append(actual_pred)
        
        # Calculate confidence (lower for more distant predictions)
        confidence_levels = [max(0.95 - (i * 0.01), 0.7) for i in range(len(prediction_prices))]
        
        # Calculate upper and lower bounds
        upper_bounds = [price * (1 + (1 - conf) * 0.2) for price, conf in zip(prediction_prices, confidence_levels)]
        lower_bounds = [price * (1 - (1 - conf) * 0.2) for price, conf in zip(prediction_prices, confidence_levels)]
        
        return {
            "model_id": self.model_id,
            "dates": prediction_dates,
            "predicted_prices": prediction_prices,
            "upper_bounds": upper_bounds,
            "lower_bounds": lower_bounds,
            "confidence_levels": confidence_levels        }
