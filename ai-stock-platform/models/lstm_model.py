import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import datetime

def run_lstm(df, forecast_days=7, epochs=20, look_back=30):
    """
    Train an LSTM model on the provided dataframe's 'close' column and forecast future prices.
    
    Args:
        df: DataFrame with historical price data
        forecast_days: Number of days to forecast
        epochs: Number of training epochs
        look_back: Number of previous days to use for prediction
        
    Returns:
        numpy array of predicted values
    """
    # Ensure we have the 'close' column
    if 'close' not in df.columns and 'Close' in df.columns:
        df = df.copy()
        df['close'] = df['Close']
    
    if 'close' not in df.columns:
        raise ValueError("Input dataframe must have a 'close' or 'Close' column.")
    
    # Scale data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(df['close'].values.reshape(-1, 1))

    # Create sequences
    X, y = [], []
    for i in range(look_back, len(data)):
        X.append(data[i-look_back:i, 0])
        y.append(data[i, 0])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Build model
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)

    # Forecast
    last_sequence = data[-look_back:]
    forecast = []
    current_sequence = last_sequence.copy()
    for _ in range(forecast_days):
        pred = model.predict(current_sequence.reshape(1, look_back, 1), verbose=0)[0, 0]
        forecast.append(pred)
        current_sequence = np.append(current_sequence[1:], pred)

    # Inverse scale forecast
    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1)).flatten()
    return forecast