#!/usr/bin/env python3
"""
Test script for trending stocks functionality in QuantumVestAI
Helps diagnose issues with fetching and displaying trending stocks data
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime

# Add parent directory to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Alpha Vantage API key if not set
os.environ.setdefault('ALPHA_VANTAGE_API_KEY', 'ZS3BWXCFU22FINK5')

async def test_trending_stocks_endpoint(port=8001):
    """Test the trending stocks endpoint directly"""
    print("Testing trending stocks API endpoint...")
    url = f"http://127.0.0.1:{port}/api/v1/stocks/trending"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"Status code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Success! Response data: {json.dumps(data, indent=2)}")
                    return data
                else:
                    text = await response.text()
                    print(f"Failed. Response: {text}")
                    return None
    except Exception as e:
        print(f"Error testing trending stocks endpoint: {e}")
        return None

async def test_trending_stocks_service_directly():
    """Test the trending stocks service directly by importing it"""
    print("\nTesting trending stocks service directly...")
    
    try:
        # First try to import from the correct module path
        try:
            from ai_stock_platform.api.services.trending_stocks_service import TrendingStocksService
        except ImportError:
            try:
                from api.services.trending_stocks_service import TrendingStocksService
            except ImportError:
                from services.trending_stocks_service import TrendingStocksService
        
        service = TrendingStocksService()
        
        # Check API key
        print(f"API key set: {'Yes' if service.api_key else 'No'}")
        print(f"Using mock data: {service.use_mock}")
        
        # Check cache status
        cache_status = service.get_cache_status()
        print(f"Cache status: {cache_status}")
        
        # Get trending stocks
        result = await service.get_trending_stocks(page=1, limit=5)
        print(f"Got {len(result['stocks'])} trending stocks")
        
        # Display the first stock
        if result['stocks']:
            print("Sample stock data:", json.dumps(result['stocks'][0], indent=2))
        
        return result
    except Exception as e:
        print(f"Error testing service directly: {e}")
        import traceback
        print(traceback.format_exc())
        return None

async def main():
    """Run all tests"""
    print(f"=== QuantumVestAI Trending Stocks Test ({datetime.now().isoformat()}) ===\n")
    
    # Check environment
    print("Environment:")
    print(f"  ALPHA_VANTAGE_API_KEY: {'Set' if os.getenv('ALPHA_VANTAGE_API_KEY') else 'Not set'}")
    print(f"  CACHE_TTL_TRENDING_STOCKS: {os.getenv('CACHE_TTL_TRENDING_STOCKS', '(default)')}")
    print(f"  ALPHA_VANTAGE_REQUEST_INTERVAL: {os.getenv('ALPHA_VANTAGE_REQUEST_INTERVAL', '(default)')}")
    print()
    
    # Run tests
    endpoint_result = await test_trending_stocks_endpoint()
    service_result = await test_trending_stocks_service_directly()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Endpoint test: {'Passed' if endpoint_result else 'Failed'}")
    print(f"Service test: {'Passed' if service_result else 'Failed'}")
    
    if not endpoint_result and not service_result:
        print("\nBoth tests failed. Check that:")
        print("1. The API key is valid and properly set")
        print("2. The server is running and accessible")
        print("3. Network connectivity to Alpha Vantage is working")
    elif not endpoint_result:
        print("\nEndpoint test failed but service test passed.")
        print("This suggests an issue with the API endpoint configuration or server routing.")
    elif not service_result:
        print("\nService test failed but endpoint test passed.")
        print("This suggests the endpoint might be using cached data or a different implementation.")

if __name__ == "__main__":
    asyncio.run(main())
