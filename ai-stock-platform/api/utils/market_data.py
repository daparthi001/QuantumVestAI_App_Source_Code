"""
Market Data Client
Created: 2025-07-22
Author: QuantumVestAI Auto-Fix
"""

import os
import requests
import json
from datetime import datetime, timedelta

# Expose the API key for other modules if needed. Do not fall back to the demo
# key so that a missing configuration fails fast and is easier to debug.
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

class MarketDataClient:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def get_data(self, symbol: str, interval: str = "1min", **kwargs):
        """
        Fetch market data for a given symbol and interval from Alpha Vantage.
        """
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key
        }
        params.update(kwargs)
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "symbol": symbol,
                "interval": interval,
                "data": data,
                "source": "alphavantage"
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "interval": interval,
                "data": [],
                "error": str(e),
                "source": "alphavantage"
            }

    def get_latest_price(self, symbol: str) -> float:
        """
        Return the latest price for a symbol from Alpha Vantage.
        """
        result = self.get_data(symbol)
        try:
            # Parse the latest price from the Alpha Vantage response
            time_series = result["data"].get("Time Series (1min)")
            if time_series:
                latest_timestamp = sorted(time_series.keys())[-1]
                return float(time_series[latest_timestamp]["4. close"])
        except Exception:
            pass
        return 0.0

    def get_historical(self, symbol: str, start: str, end: str) -> list:
        """
        Return historical data for a symbol between start and end dates from Alpha Vantage.
        """
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "apikey": self.api_key
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            time_series = data.get("Time Series (Daily)", {})
            # Filter by date range
            filtered = [
                {"date": k, **v}
                for k, v in time_series.items()
                if start <= k <= end
            ]
            return filtered
        except Exception as e:
            return []

def get_market_data(symbol: str, interval: str = "1min", **kwargs):
    """
    Fetch market data for a given symbol and interval (function version).
    """
    client = MarketDataClient()
    return client.get_data(symbol, interval, **kwargs)
