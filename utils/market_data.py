"""Placeholder market data utilities used for tests."""

import os
from typing import Any, Dict

# Re-export the API key used by legacy modules
# Require a valid API key - no fallback to demo
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("ALPHA_VANTAGE_API_KEY environment variable must be set")


def get_market_data(symbol: str, interval: str = "1min", **kwargs) -> Dict[str, Any]:
    """Get live market data from Alpha Vantage."""
    import requests
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY" if interval.endswith("min") else "TIME_SERIES_DAILY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "compact"
    }
    params.update(kwargs)
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


class MarketDataClient:
    """Live market data client using Alpha Vantage API."""

    def get_data(self, symbol: str, interval: str = "1min", **kwargs) -> Dict[str, Any]:
        return get_market_data(symbol, interval, **kwargs)
