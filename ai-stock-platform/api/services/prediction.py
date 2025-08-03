"""Price forecasting helpers.

A small wrapper around the `prophet` library is provided when available.  In
environments where Prophet cannot be installed the service falls back to a
naive prediction that simply repeats the last observed price.  The goal is to
provide a stable API for tests without introducing heavy dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

try:  # pragma: no cover - only executed when Prophet is installed
    from prophet import Prophet  # type: ignore
    _PROPHET_AVAILABLE = True
except Exception:  # pragma: no cover - default path in tests
    Prophet = None  # type: ignore
    _PROPHET_AVAILABLE = False


@dataclass
class ForecastPoint:
    ds: pd.Timestamp
    yhat: float


class PredictionService:
    """Generate simple price forecasts."""

    def forecast(self, history: pd.DataFrame, days: int = 1) -> List[ForecastPoint]:
        """Forecast prices based on ``history``.

        Parameters
        ----------
        history: pd.DataFrame
            Historical price data containing ``ds`` (datetime) and ``y`` (price)
            columns.
        days: int
            Number of periods to forecast into the future.
        """

        if {"ds", "y"} - set(history.columns):
            raise ValueError("history must contain 'ds' and 'y' columns")

        if _PROPHET_AVAILABLE:  # pragma: no cover - heavy dependency path
            model = Prophet()
            model.fit(history[["ds", "y"]])
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future).tail(days)
            return [
                ForecastPoint(row.ds, float(row.yhat))
                for _, row in forecast.iterrows()
            ]

        # Fallback: repeat the last observed value
        last_row = history.iloc[-1]
        return [
            ForecastPoint(last_row.ds + pd.Timedelta(days=i + 1), float(last_row.y))
            for i in range(days)
        ]
