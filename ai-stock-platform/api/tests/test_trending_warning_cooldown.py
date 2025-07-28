import asyncio
import os
import importlib.util
import pytest
from datetime import datetime

spec = importlib.util.spec_from_file_location(
    "trending_stocks_service",
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "services",
        "trending_stocks_service.py",
    ),
)
trending_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trending_module)
TrendingStocksService = trending_module.TrendingStocksService


@pytest.mark.asyncio
async def test_failure_warning_cooldown(caplog):
    os.environ["ENABLE_REAL_DATA"] = "true"
    os.environ["ALPHA_VANTAGE_API_KEY"] = "testkey"
    service = TrendingStocksService()
    service.use_mock = False

    async def fake_fetch(session, symbol):
        return None

    service._fetch_stock_quote = fake_fetch  # type: ignore
    caplog.set_level("WARNING")

    await service.get_trending_stocks()
    first_warning = service._last_failure_warning
    assert first_warning is not None
    assert "falling back to mock data" in caplog.text

    caplog.clear()
    await service.get_trending_stocks()
    # Should not log again within cooldown
    assert "falling back to mock data" not in caplog.text
    assert service._last_failure_warning == first_warning
