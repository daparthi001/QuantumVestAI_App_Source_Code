def run_ensemble(lstm_forecast, prophet_forecast):
    """
    Combine forecasts from LSTM and Prophet using a simple average.
    """
    if len(lstm_forecast) != len(prophet_forecast):
        raise ValueError("Forecast lengths must match.")
    
    # Prophet forecast expects dataframe with 'ds' and 'yhat'
    prophet_values = prophet_forecast.tail(len(lstm_forecast))['yhat'].values

    # Simple average ensemble
    ensemble_forecast = (lstm_forecast + prophet_values) / 2

    return ensemble_forecast
