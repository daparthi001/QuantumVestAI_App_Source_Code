#!/usr/bin/env python3
"""
Test script to verify live data configuration is working correctly.
Tests that the trending stocks service requires API keys and doesn't fall back to mock data.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent / "ai-stock-platform"
sys.path.insert(0, str(project_root))

def test_trending_stocks_service():
    """Test that TrendingStocksService requires API keys and doesn't use mock data."""
    try:
        # Clear API key environment variables to test error handling
        original_key = os.environ.pop('ALPHA_VANTAGE_API_KEY', None)
        
        from api.services.trending_stocks_service import TrendingStocksService
        
        print("Testing TrendingStocksService without API key...")
        
        # Should raise RuntimeError when no API key is provided
        try:
            service = TrendingStocksService()
            print("❌ ERROR: Service should have raised RuntimeError for missing API key")
            return False
        except RuntimeError as e:
            if "ALPHA_VANTAGE_API_KEY must be set" in str(e):
                print("✅ SUCCESS: Service correctly requires ALPHA_VANTAGE_API_KEY")
            else:
                print(f"❌ ERROR: Unexpected error message: {e}")
                return False
        
        # Test with API key
        os.environ['ALPHA_VANTAGE_API_KEY'] = 'test-key'
        service = TrendingStocksService()
        
        # Verify use_mock is False
        if hasattr(service, 'use_mock') and service.use_mock == False:
            print("✅ SUCCESS: Service configured to use live data (use_mock=False)")
        else:
            print("❌ ERROR: Service should have use_mock=False")
            return False
            
        # Restore original API key
        if original_key:
            os.environ['ALPHA_VANTAGE_API_KEY'] = original_key
        else:
            os.environ.pop('ALPHA_VANTAGE_API_KEY', None)
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR in test: {e}")
        return False

def test_settings():
    """Test that settings are configured correctly."""
    try:
        from api.core.config.settings import settings
        
        print("Testing settings configuration...")
        
        # Check ENABLE_REAL_DATA defaults to True
        if settings.ENABLE_REAL_DATA == True:
            print("✅ SUCCESS: ENABLE_REAL_DATA is True by default")
        else:
            print(f"❌ ERROR: ENABLE_REAL_DATA should be True, got {settings.ENABLE_REAL_DATA}")
            return False
            
        # Check API key settings exist
        if hasattr(settings, 'ALPHA_VANTAGE_API_KEY'):
            print("✅ SUCCESS: ALPHA_VANTAGE_API_KEY setting exists")
        else:
            print("❌ ERROR: ALPHA_VANTAGE_API_KEY setting missing")
            return False
            
        if hasattr(settings, 'RAPIDAPI_KEY'):
            print("✅ SUCCESS: RAPIDAPI_KEY setting exists")
        else:
            print("❌ ERROR: RAPIDAPI_KEY setting missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR in settings test: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING: Live Data Configuration")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    print("\n1. Testing TrendingStocksService...")
    if test_trending_stocks_service():
        tests_passed += 1
    
    print("\n2. Testing Settings...")
    if test_settings():
        tests_passed += 1
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if tests_passed == total_tests:
        print(f"✅ SUCCESS: All {tests_passed}/{total_tests} tests passed!")
        print("✅ Live data configuration is working correctly")
        return True
    else:
        print(f"❌ FAILED: {tests_passed}/{total_tests} tests passed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)