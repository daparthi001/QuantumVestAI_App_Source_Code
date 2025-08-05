import os
import importlib.util
from datetime import datetime

import pytest

spec = importlib.util.spec_from_file_location(
    "trending_stocks_service",
    os.path.join(os.path.dirname(__file__), "..", "services", "trending_stocks_service.py"),
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TrendingStocksService = module.TrendingStocksService


@pytest.mark.asyncio
async def test_get_trending_stocks_returns_data(monkeypatch):
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test")
    service = TrendingStocksService()

    async def mock_fetch_yahoo_trending_symbols(self, retries=3, delay: float = 2.0):
        return ["AAPL", "MSFT"]

    async def mock_fetch_stock_quote(self, session, symbol: str):
        return {
            "symbol": symbol,
            "name": f"{symbol} Corp.",
            "price": 100.0,
            "change": 0.0,
            "change_percent": 0.0,
            "volume": 0,
            "last_updated": datetime.utcnow().isoformat(),
        }

    monkeypatch.setattr(TrendingStocksService, "_fetch_yahoo_trending_symbols", mock_fetch_yahoo_trending_symbols)
    monkeypatch.setattr(TrendingStocksService, "_fetch_stock_quote", mock_fetch_stock_quote)

    result = await service.get_trending_stocks(limit=2)
    assert isinstance(result["stocks"], list)
    assert len(result["stocks"]) == 2
