import os
import importlib.util

import pytest

spec = importlib.util.spec_from_file_location(
    "trending_stocks_service",
    os.path.join(os.path.dirname(__file__), "..", "services", "trending_stocks_service.py"),
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TrendingStocksService = module.TrendingStocksService


@pytest.mark.asyncio
async def test_fetch_yahoo_trending_symbols_fallback_returns_list(monkeypatch):
    # Ensure API key is set to avoid runtime error in service initialization
    monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test")
    service = TrendingStocksService()

    symbols = await service._fetch_yahoo_trending_symbols(retries=0)

    assert isinstance(symbols, list)
    assert "AAPL" in symbols
    assert len(symbols) >= 5
