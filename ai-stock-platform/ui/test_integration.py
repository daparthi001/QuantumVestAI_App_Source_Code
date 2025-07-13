"""
Integration test for httpx fixes in QuantumVestAI application
Tests the integration between the new HTTP client and existing components.

Last updated: 2025-01-18
Updated by: daparthi001
"""

import asyncio
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_http_client_integration():
    """Test the HTTP client integration with existing components."""
    print("Testing HTTP client integration...")
    
    # Test 1: HTTP client creation and configuration
    try:
        from core.http_client import (HTTPClient, HTTPClientConfig,
                                      get_http_client)
        
        config = HTTPClientConfig()
        client = HTTPClient(config)
        
        print("✓ HTTP client configuration and creation successful")
        
        # Test connection pooling settings
        assert config.limits.max_connections > 0
        assert config.limits.max_keepalive_connections > 0
        print("✓ Connection pooling configured correctly")
        
        # Test timeout settings  
        assert config.timeout.connect > 0
        assert config.timeout.read > 0
        print("✓ Timeout settings configured correctly")
        
        # Test retry settings
        assert config.max_retries > 0
        assert config.retry_delay_base > 0
        print("✓ Retry settings configured correctly")
        
        # Test SSL/TLS configuration
        assert isinstance(config.verify_ssl, bool)
        print("✓ SSL/TLS configuration set")
        
        # Test default headers
        assert "User-Agent" in config.default_headers
        assert "Accept" in config.default_headers
        print("✓ Default headers configured correctly")
        
        await client.close()
        print("✓ HTTP client cleanup successful")
        
    except Exception as e:
        print(f"✗ HTTP client test failed: {e}")
        return False
    
    # Test 2: Global HTTP client management
    try:
        from core.http_client import cleanup_http_clients, get_http_client

        # Test global client access
        async with get_http_client() as client:
            assert client is not None
            print("✓ Global HTTP client access successful")
        
        # Test cleanup
        await cleanup_http_clients()
        print("✓ Global HTTP client cleanup successful")
        
    except Exception as e:
        print(f"✗ Global HTTP client test failed: {e}")
        return False
    
    # Test 3: Utility functions
    try:
        from core.http_client import safe_get_json, safe_post_json

        # Test safe_get_json with default value
        result = await safe_get_json(
            url="https://invalid-url-for-testing.com",
            default={"test": "default"}
        )
        
        assert result == {"test": "default"}
        print("✓ safe_get_json with default value works correctly")
        
        # Test safe_post_json with default value
        result = await safe_post_json(
            url="https://invalid-url-for-testing.com",
            json_data={"test": "data"},
            default={"test": "default"}
        )
        
        assert result == {"test": "default"}
        print("✓ safe_post_json with default value works correctly")
        
    except Exception as e:
        print(f"✗ Utility functions test failed: {e}")
        return False
    
    # Test 4: Error handling and retry logic
    try:
        client = HTTPClient()
        
        # Test retry delay calculation
        delay1 = client._calculate_retry_delay(0)
        delay2 = client._calculate_retry_delay(1)
        delay3 = client._calculate_retry_delay(2)
        
        assert delay1 < delay2 < delay3
        print("✓ Retry delay calculation works correctly")
        
        # Test retryable error detection
        from unittest.mock import MagicMock

        import httpx

        # Request errors should be retryable
        request_error = httpx.RequestError("Connection failed")
        assert client._is_retryable_error(request_error)
        print("✓ Request error detection works correctly")
        
        # Server errors should be retryable
        mock_response = MagicMock()
        mock_response.status_code = 500
        server_error = httpx.HTTPStatusError("Server error", request=MagicMock(), response=mock_response)
        assert client._is_retryable_error(server_error)
        print("✓ Server error detection works correctly")
        
        # Client errors should not be retryable
        mock_response.status_code = 400
        client_error = httpx.HTTPStatusError("Bad request", request=MagicMock(), response=mock_response)
        assert not client._is_retryable_error(client_error)
        print("✓ Client error detection works correctly")
        
        await client.close()
        print("✓ Error handling and retry logic tests passed")
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False
    
    print("\n🎉 All integration tests passed!")
    return True

async def test_existing_code_compatibility():
    """Test that existing code patterns still work with the new HTTP client."""
    print("\nTesting existing code compatibility...")
    
    try:
        # Test that the new HTTP client doesn't break existing imports
        import httpx

        # Test that basic httpx functionality still works
        async with httpx.AsyncClient() as client:
            # This should work without our custom client
            pass
        
        print("✓ Basic httpx functionality preserved")
        
        # Test that our custom client works alongside httpx
        from core.http_client import HTTPClient
        
        custom_client = HTTPClient()
        await custom_client.close()
        
        print("✓ Custom HTTP client works alongside httpx")
        
    except Exception as e:
        print(f"✗ Compatibility test failed: {e}")
        return False
    
    print("✓ Existing code compatibility maintained")
    return True

def test_configuration_validation():
    """Test configuration validation and environment variable handling."""
    print("\nTesting configuration validation...")
    
    try:
        from core.http_client import HTTPClientConfig

        # Test default configuration
        config = HTTPClientConfig()
        
        # Validate timeout settings
        assert config.timeout.connect > 0
        assert config.timeout.read > 0
        assert config.timeout.write > 0
        assert config.timeout.pool > 0
        print("✓ Timeout configuration validated")
        
        # Validate connection limits
        assert config.limits.max_connections > 0
        assert config.limits.max_keepalive_connections > 0
        assert config.limits.keepalive_expiry > 0
        print("✓ Connection limits validated")
        
        # Validate retry settings
        assert config.max_retries >= 0
        assert config.retry_delay_base > 0
        assert config.retry_delay_max > config.retry_delay_base
        print("✓ Retry settings validated")
        
        # Validate headers
        assert isinstance(config.default_headers, dict)
        assert len(config.default_headers) > 0
        print("✓ Default headers validated")
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return False
    
    print("✓ Configuration validation passed")
    return True

async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("QuantumVestAI HTTP Client Integration Tests")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("HTTP Client Integration", test_http_client_integration()),
        ("Existing Code Compatibility", test_existing_code_compatibility()),
        ("Configuration Validation", test_configuration_validation()),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_coro in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            
            if result:
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! HTTP client fixes are working correctly.")
    else:
        print("❌ Some tests failed. Please review the implementation.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
