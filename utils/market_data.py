"""Placeholder market data utilities used for tests."""

from typing import Any, Dict

def get_market_data(symbol: str, interval: str = "1min", **kwargs) -> Dict[str, Any]:
    """Return mock market data for testing."""
    return {"symbol": symbol, "interval": interval, "data": []}

class MarketDataClient:
    """Simple mock market data client."""
    def get_data(self, symbol: str, interval: str = "1min", **kwargs) -> Dict[str, Any]:
        return get_market_data(symbol, interval, **kwargs)
