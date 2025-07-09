import numpy as np
import pandas as pd
from typing import Callable, List

class EnsemblePredictor:
    """Combine multiple prediction models by averaging their outputs."""

    def __init__(self):
        self._models: List[Callable[[str, pd.DataFrame, int], pd.DataFrame]] = []

    def add_model(self, model_fn: Callable[[str, pd.DataFrame, int], pd.DataFrame]):
        """Register a prediction function.
        The function must accept (ticker, historical_data, days_ahead)
        and return a DataFrame with a 'predicted_close' column indexed by date.
        """
        self._models.append(model_fn)

    def predict(self, ticker: str, historical_data: pd.DataFrame, days_ahead: int = 5) -> pd.DataFrame:
        if not self._models:
            raise ValueError("No prediction models registered")

        predictions = []
        for model_fn in self._models:
            try:
                df = model_fn(ticker, historical_data, days_ahead)
                predictions.append(df['predicted_close'].values)
            except Exception:
                # Skip models that fail
                continue

        if not predictions:
            raise ValueError("All prediction models failed")

        avg_prediction = np.mean(predictions, axis=0)
        dates = pd.date_range(start=historical_data.index[-1], periods=days_ahead+1)[1:]
        return pd.DataFrame({'date': dates, 'predicted_close': avg_prediction}).set_index('date')


def linear_regression_predict(ticker: str, historical_data: pd.DataFrame, days_ahead: int = 5) -> pd.DataFrame:
    """Simple linear regression predictor used as a fallback model."""
    from sklearn.linear_model import LinearRegression

    df = historical_data.dropna()
    if len(df) < 2:
        raise ValueError("Not enough data for regression")

    X = np.arange(len(df)).reshape(-1, 1)
    y = df['adjusted_close'].values
    model = LinearRegression().fit(X, y)

    future_index = np.arange(len(df), len(df) + days_ahead).reshape(-1, 1)
    preds = model.predict(future_index)
    dates = pd.date_range(start=df.index[-1], periods=days_ahead+1)[1:]
    return pd.DataFrame({'date': dates, 'predicted_close': preds}).set_index('date')
