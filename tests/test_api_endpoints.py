#!/usr/bin/env python3
"""
Test script to verify the API endpoints are working by making HTTP requests
This can be used to test the running API server
"""

import asyncio
import json
import sys
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


def test_endpoint(url, expected_status=200):
    """Test a single endpoint"""
    try:
        print(f"Testing: {url}")
        response = urlopen(url, timeout=10)
        
        if response.getcode() == expected_status:
            # Try to parse JSON response
            try:
                data = json.loads(response.read().decode('utf-8'))
                print(f"✓ {url} - Status: {response.getcode()}")
                if isinstance(data, list):
                    print(f"  Returns {len(data)} items")
                elif isinstance(data, dict):
                    print(f"  Returns dict with keys: {list(data.keys())}")
                return True
            except json.JSONDecodeError:
                print(f"✓ {url} - Status: {response.getcode()} (non-JSON response)")
                return True
        else:
            print(f"✗ {url} - Unexpected status: {response.getcode()}")
            return False
            
    except HTTPError as e:
        print(f"✗ {url} - HTTP Error: {e.code} {e.reason}")
        return False
    except URLError as e:
        print(f"✗ {url} - URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"✗ {url} - Error: {e}")
        return False


def main():
    """Test all the endpoints that were previously returning 404"""
    
    # Base URL - adjust this based on where the API server is running
    base_url = "http://localhost:8000"
    
    # Test cases based on the original problem statement
    test_cases = [
        # Content API endpoints
        f"{base_url}/api/content/market-movers",
        f"{base_url}/api/content/ai-recommendations", 
        f"{base_url}/api/content/news",
        f"{base_url}/api/content/trending",
        
        # AI API endpoints  
        f"{base_url}/api/ai/market-data/AAPL",
        f"{base_url}/api/ai/market-data/GOOGL",
        f"{base_url}/api/ai/market-data/MSFT", 
        f"{base_url}/api/ai/market-data/TSLA",
        f"{base_url}/api/ai/market-data/AMZN",
        
        # Health check
        f"{base_url}/health",
    ]
    
    print("Testing API endpoints that were previously returning 404 errors...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(test_cases)
    
    for url in test_cases:
        if test_endpoint(url):
            success_count += 1
        print()  # Empty line for readability
    
    print("=" * 60)
    print(f"Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All endpoints are now working!")
        return True
    else:
        print(f"⚠️  {total_count - success_count} endpoints still have issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)