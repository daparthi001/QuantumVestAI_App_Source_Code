from models.lstm_model import run_lstm
from models.prophet_model import run_prophet
import pandas as pd
import numpy as np

def run_ensemble(df, forecast_days=7):
    """
    Run both LSTM and Prophet models and combine their forecasts.
    
    Args:
        df: DataFrame with at minimum 'date' and 'close' columns
        forecast_days: Number of days to forecast
        
    Returns:
        DataFrame with combined forecast results
    """
    # Ensure column names are consistent
    df_copy = df.copy()
    if 'Close' in df_copy.columns and 'close' not in df_copy.columns:
        df_copy['close'] = df_copy['Close']
    if 'Date' in df_copy.columns and 'date' not in df_copy.columns:
        df_copy['date'] = df_copy['Date']
    
    # Run individual models
    lstm_forecast = run_lstm(df_copy, forecast_days=forecast_days)
    prophet_forecast = run_prophet(df_copy, forecast_days=forecast_days)
    
    # Get the dates from prophet forecast for the forecast period
    forecast_dates = prophet_forecast.tail(forecast_days)['ds'].values
    
    # Simple average ensemble
    prophet_values = prophet_forecast.tail(forecast_days)['yhat'].values
    ensemble_values = (lstm_forecast + prophet_values) / 2
    
    # Create result dataframe
    result = pd.DataFrame({
        'ds': forecast_dates,
        'yhat': ensemble_values,
        'lstm_forecast': lstm_forecast,
        'prophet_forecast': prophet_values
    })
    
    return result
