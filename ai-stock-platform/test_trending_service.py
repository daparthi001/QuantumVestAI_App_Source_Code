#!/usr/bin/env python3

import sys
import os
import asyncio
import json

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.services.trending_stocks_service import TrendingStocksService

async def test_trending_stocks():
    print("Testing Trending Stocks Service...")
    
    # Create service instance
    service = TrendingStocksService()
    
    # Test getting trending stocks
    result = await service.get_trending_stocks()
    
    print("Result:")
    print(json.dumps(result, indent=2))
    
    # Test cache status
    cache_status = service.get_cache_status()
    print("\nCache Status:")
    print(json.dumps(cache_status, indent=2))
    
    return result

if __name__ == "__main__":
    asyncio.run(test_trending_stocks())