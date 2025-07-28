"""Placeholder market data utilities used for tests."""

import os
from typing import Any, Dict

# Re-export the API key used by legacy modules
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")


def get_market_data(symbol: str, interval: str = "1min", **kwargs) -> Dict[str, Any]:
    """Return mock market data for testing."""
    return {"symbol": symbol, "interval": interval, "data": []}


class MarketDataClient:
    """Simple mock market data client."""

    def get_data(self, symbol: str, interval: str = "1min", **kwargs) -> Dict[str, Any]:
        return get_market_data(symbol, interval, **kwargs)
