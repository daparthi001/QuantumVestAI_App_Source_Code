from prophet import Prophet

def run_prophet(df, forecast_days=7):
    """
    Forecast future prices using Facebook Prophet.
    Dataframe must have 'date' and 'close' columns.
    """
    if 'date' not in df.columns or 'close' not in df.columns:
        raise ValueError("Input dataframe must have 'date' and 'close' columns.")
    
    prophet_df = df[['date', 'close']].rename(columns={'date': 'ds', 'close': 'y'})

    model = Prophet()
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]