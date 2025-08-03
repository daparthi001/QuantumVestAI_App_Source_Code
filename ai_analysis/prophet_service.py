from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import pandas as pd
import requests

try:  # pragma: no cover - optional dependency
    from prophet import Prophet  # type: ignore
    _PROPHET_AVAILABLE = True
except Exception:  # pragma: no cover - prophet not installed
    Prophet = None  # type: ignore
    _PROPHET_AVAILABLE = False


@dataclass
class ForecastPoint:
    """Single forecasted point."""

    ds: pd.Timestamp
    yhat: float


class ProphetService:
    """Fetch data and generate forecasts using Prophet when available."""

    ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

    def fetch_historical_data(self, symbol: str) -> pd.DataFrame:
        """Fetch daily historical data for ``symbol`` from Alpha Vantage.

        Parameters
        ----------
        symbol: str
            Stock ticker symbol.
        """

        api_key = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": api_key,
        }
        response = requests.get(self.ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("Time Series (Daily)", {})
        records = [
            {"ds": pd.to_datetime(date), "y": float(values["4. close"])}
            for date, values in sorted(data.items())
        ]
        return pd.DataFrame(records)

    def forecast(self, history: pd.DataFrame, days: int = 7) -> List[ForecastPoint]:
        """Generate a ``days`` day forecast from historical price ``history``."""

        if {"ds", "y"} - set(history.columns):
            raise ValueError("history must contain 'ds' and 'y' columns")

        if _PROPHET_AVAILABLE:  # pragma: no cover - heavy dependency path
            model = Prophet()
            model.fit(history)
            future = model.make_future_dataframe(periods=days)
            forecast_df = model.predict(future).tail(days)
            return [
                ForecastPoint(row.ds, float(row.yhat))
                for _, row in forecast_df.iterrows()
            ]

        # Fallback: repeat the last observed value
        last_row = history.iloc[-1]
        return [
            ForecastPoint(last_row.ds + pd.Timedelta(days=i + 1), float(last_row.y))
            for i in range(days)
        ]
