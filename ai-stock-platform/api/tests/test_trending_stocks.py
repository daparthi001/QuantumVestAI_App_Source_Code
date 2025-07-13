"""
Tests for Trending Stocks API

These tests verify that the trending stocks endpoint is working correctly,
providing real-time data with proper caching and fallback mechanisms.

Created: 2025-01-09
Author: AI Assistant
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Ensure API key is set for tests
os.environ.setdefault("ALPHA_VANTAGE_API_KEY", "test")

# Import the service directly
import importlib.util
import json
from datetime import datetime

import pytest

spec = importlib.util.spec_from_file_location(
    "trending_stocks_service",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "services", "trending_stocks_service.py")
)
trending_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trending_module)
TrendingStocksService = trending_module.TrendingStocksService

if not getattr(trending_module, "AIOHTTP_AVAILABLE", False):
    pytest.skip("aiohttp not available", allow_module_level=True)


def test_trending_stocks_service_initialization():
    """Test that the service initializes correctly."""
    service = TrendingStocksService()
    
    assert service.api_key is not None
    assert service.cache_ttl > 0
    assert len(service.trending_symbols) > 0
    assert "AAPL" in service.trending_symbols


@pytest.mark.asyncio
async def test_get_trending_stocks():
    """Test getting trending stocks data."""
    service = TrendingStocksService()
    
    result = await service.get_trending_stocks(page=1, limit=5)
    
    assert "stocks" in result
    assert "pagination" in result
    assert "metadata" in result
    
    # Check pagination
    assert result["pagination"]["page"] == 1
    assert result["pagination"]["limit"] == 5
    assert result["pagination"]["total"] >= 5
    
    # Check stocks data structure
    stocks = result["stocks"]
    assert len(stocks) <= 5
    
    for stock in stocks:
        assert "symbol" in stock
        assert "name" in stock
        assert "price" in stock
        assert "change_percent" in stock
        assert "volume" in stock
        assert "last_updated" in stock
        
        # Validate data types
        assert isinstance(stock["price"], (int, float))
        assert isinstance(stock["change_percent"], (int, float))
        assert isinstance(stock["volume"], int)
        assert isinstance(stock["last_updated"], str)


@pytest.mark.asyncio
async def test_trending_stocks_pagination():
    """Test pagination functionality."""
    service = TrendingStocksService()
    
    # Get first page
    page1 = await service.get_trending_stocks(page=1, limit=3)
    
    # Get second page
    page2 = await service.get_trending_stocks(page=2, limit=3)
    
    # Check that pages are different
    page1_symbols = [stock["symbol"] for stock in page1["stocks"]]
    page2_symbols = [stock["symbol"] for stock in page2["stocks"]]
    
    # No overlap between pages
    assert len(set(page1_symbols) & set(page2_symbols)) == 0
    
    # Check pagination metadata
    assert page1["pagination"]["has_next"] == True
    assert page1["pagination"]["has_prev"] == False
    assert page2["pagination"]["has_prev"] == True


@pytest.mark.asyncio
async def test_cache_functionality():
    """Test caching functionality."""
    service = TrendingStocksService()
    
    # Clear cache
    service.invalidate_cache()
    
    # Check empty cache status
    status = service.get_cache_status()
    assert status["status"] == "empty"
    
    # Get data (should populate cache)
    result1 = await service.get_trending_stocks()
    
    # Check cache is now populated
    status = service.get_cache_status()
    assert status["status"] == "valid"
    assert status["items_count"] > 0
    
    # Get data again (should come from cache)
    result2 = await service.get_trending_stocks()
    
    # Data should be identical (from cache)
    assert result1["metadata"]["last_updated"] == result2["metadata"]["last_updated"]


def test_cache_invalidation():
    """Test cache invalidation."""
    service = TrendingStocksService()
    
    # Manually set cache
    service._cache = {"stocks": [], "timestamp": datetime.now().isoformat()}
    service._cache_timestamp = datetime.now()
    
    # Verify cache exists
    assert service._is_cache_valid()
    
    # Invalidate cache
    service.invalidate_cache()
    
    # Verify cache is cleared
    assert not service._is_cache_valid()
    
    status = service.get_cache_status()
    assert status["status"] == "empty"


@pytest.mark.asyncio
async def test_data_consistency():
    """Test that returned data is consistent and properly formatted."""
    service = TrendingStocksService()
    
    result = await service.get_trending_stocks()
    
    # Check metadata
    metadata = result["metadata"]
    assert "data_source" in metadata
    assert "cache_ttl_seconds" in metadata
    assert "last_updated" in metadata
    
    # Validate timestamp format
    timestamp = metadata["last_updated"]
    assert datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    # Check that stocks data is present and valid
    stocks = result["stocks"]
    if len(stocks) > 1:
        # Just check that all stocks have valid change_percent values
        for stock in stocks:
            assert isinstance(stock["change_percent"], (int, float))
            assert -20 <= stock["change_percent"] <= 20  # Reasonable range




if __name__ == "__main__":
    # Run basic tests
    print("Running Trending Stocks Service Tests...")
    
    print("✓ Testing service initialization...")
    test_trending_stocks_service_initialization()
    
    print("✓ Testing cache invalidation...")
    test_cache_invalidation()
    
    
    print("✓ Running async tests...")
    async def run_async_tests():
        await test_get_trending_stocks()
        await test_trending_stocks_pagination()
        await test_cache_functionality()
        await test_data_consistency()
    
    asyncio.run(run_async_tests())
    print("All tests passed! ✅")

