from prophet import Prophet
import pandas as pd

def run_prophet(df, forecast_days=7):
    """
    Forecast future prices using Facebook Prophet.
    
    Args:
        df: DataFrame with historical price data
        forecast_days: Number of days to forecast
        
    Returns:
        DataFrame with forecast results including dates and predictions
    """
    # Check for date column
    date_col = None
    if 'date' in df.columns:
        date_col = 'date'
    elif 'Date' in df.columns:
        date_col = 'Date'
    else:
        raise ValueError("Input dataframe must have 'date' or 'Date' column.")
    
    # Check for close column
    close_col = None
    if 'close' in df.columns:
        close_col = 'close'
    elif 'Close' in df.columns:
        close_col = 'Close'
    else:
        raise ValueError("Input dataframe must have 'close' or 'Close' column.")
    
    # Prepare data for Prophet
    prophet_df = df[[date_col, close_col]].rename(columns={date_col: 'ds', close_col: 'y'})

    # Fit model
    model = Prophet()
    model.fit(prophet_df)

    # Create future dataframe and predict
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]