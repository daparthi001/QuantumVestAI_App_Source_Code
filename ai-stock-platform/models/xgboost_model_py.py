import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def run_xgboost(df: pd.DataFrame, forecast_days: int = 7):
    """
    Train XGBoost model on the provided dataframe and forecast future prices.
    
    Args:
        df: DataFrame with historical price data
        forecast_days: Number of days to forecast
        
    Returns:
        DataFrame with forecast results including dates and predictions
    """
    # Ensure we have the required columns with consistent naming
    df_copy = df.copy()
    
    # Check and standardize column names
    if 'Close' in df_copy.columns and 'close' not in df_copy.columns:
        df_copy['close'] = df_copy['Close']
    if 'Open' in df_copy.columns and 'open' not in df_copy.columns:
        df_copy['open'] = df_copy['Open']
    if 'High' in df_copy.columns and 'high' not in df_copy.columns:
        df_copy['high'] = df_copy['High']
    if 'Low' in df_copy.columns and 'low' not in df_copy.columns:
        df_copy['low'] = df_copy['Low']
    if 'Volume' in df_copy.columns and 'volume' not in df_copy.columns:
        df_copy['volume'] = df_copy['Volume']
    if 'Date' in df_copy.columns and 'date' not in df_copy.columns:
        df_copy['date'] = df_copy['Date']
        
    # Check if we have the necessary columns after standardization
    required_cols = ['close', 'open', 'high', 'low', 'volume', 'date']
    missing_cols = [col for col in required_cols if col not in df_copy.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    # Feature engineering
    df_copy['return'] = df_copy['close'].pct_change().fillna(0)
    df_copy['target'] = df_copy['return'].shift(-forecast_days).fillna(0)

    # Prepare features
    features = ['open', 'high', 'low', 'close', 'volume']
    X = df_copy[features]
    y = df_copy['target']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X[:-forecast_days], y[:-forecast_days], test_size=0.2, shuffle=False
    )
    
    # Train model
    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)

    # Generate predictions
    future_df = X[-forecast_days:]
    return_preds = model.predict(future_df)
    
    # Convert returns to prices
    last_price = df_copy['close'].iloc[-forecast_days]
    price_preds = []
    current_price = last_price
    
    for ret in return_preds:
        new_price = current_price * (1 + ret)
        price_preds.append(new_price)
        current_price = new_price

    # Create result dataframe
    dates = df_copy['date'][-forecast_days:].values
    return pd.DataFrame({'ds': dates, 'yhat': price_preds})
