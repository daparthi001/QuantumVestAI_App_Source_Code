#!/usr/bin/env python3
"""
Test script for trending stocks functionality in QuantumVestAI
With SSL verification disabled for development environments
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
# Disable SSL verification to fix certificate errors
os.environ['DISABLE_SSL_VERIFY'] = 'true'

async def test_trending_stocks_endpoint(port=8001):
    """Test the trending stocks API endpoint directly"""
    print("Testing trending stocks API endpoint...")
    url = f"http://127.0.0.1:{port}/api/v1/stocks/trending"
    
    try:
        # Create SSL context that doesn't verify certificates
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
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
        print(f"SSL verification enabled: {service.ssl_verify}")
        
        # Check cache status
        cache_status = service.get_cache_status()
        print(f"Cache status: {cache_status}")
        
        # Get trending stocks
        result = await service.get_trending_stocks(page=1, limit=5)
        print(f"Got {len(result['stocks'])} trending stocks")
        print(f"Using mock data: {'is_mock_data' in result['stocks'][0] if result['stocks'] else 'N/A'}")
        
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
    print(f"  DISABLE_SSL_VERIFY: {os.getenv('DISABLE_SSL_VERIFY')}")
    print()
    
    # Run tests
    service_result = await test_trending_stocks_service_directly()
    endpoint_result = await test_trending_stocks_endpoint()
    
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
