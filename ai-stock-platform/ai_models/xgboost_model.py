import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def run_xgboost(df: pd.DataFrame, forecast_days: int = 7):
    df['return'] = df['Close'].pct_change().fillna(0)
    df['target'] = df['return'].shift(-forecast_days).fillna(0)

    features = ['Open', 'High', 'Low', 'Close', 'Volume']
    X = df[features]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X[:-forecast_days], y[:-forecast_days], test_size=0.2, shuffle=False)
    
    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)

    future_df = X[-forecast_days:]
    preds = model.predict(future_df)
    dates = df['Date'][-forecast_days:]
    return pd.DataFrame({'ds': dates, 'yhat': preds})
