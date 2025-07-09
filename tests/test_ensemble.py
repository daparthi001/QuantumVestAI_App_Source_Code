def test_ensemble_average():
    import pandas as pd
    from ai_stock_platform.api.ml.ensemble_model import EnsemblePredictor

    # Dummy historical data
    dates = pd.date_range(end='2024-01-10', periods=10)
    df = pd.DataFrame({'adjusted_close': range(10)}, index=dates)

    # Dummy model returning constant + 1 predictions
    def model_one(ticker, hist, days_ahead):
        future_dates = pd.date_range(start=hist.index[-1], periods=days_ahead+1)[1:]
        return pd.DataFrame({'date': future_dates, 'predicted_close': [1]*days_ahead}).set_index('date')

    # Dummy model returning constant + 3 predictions
    def model_two(ticker, hist, days_ahead):
        future_dates = pd.date_range(start=hist.index[-1], periods=days_ahead+1)[1:]
        return pd.DataFrame({'date': future_dates, 'predicted_close': [3]*days_ahead}).set_index('date')

    ens = EnsemblePredictor()
    ens.add_model(model_one)
    ens.add_model(model_two)

    result = ens.predict('TEST', df, days_ahead=2)
    assert list(result['predicted_close']) == [2.0, 2.0]
