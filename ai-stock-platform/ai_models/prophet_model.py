from prophet import Prophet
import pandas as pd

def run_prophet(df: pd.DataFrame, forecast_days: int = 7):
    model = Prophet(daily_seasonality=True)
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    model.fit(df)
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']]
