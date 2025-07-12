"""
Test module for HTTP client functionality
Tests connection pooling, retry logic, error handling, and performance optimizations.

Last updated: 2025-01-18
Updated by: daparthi001
"""

import os
import sys
import asyncio
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "ai-stock-platform"))
sys.path.append(os.path.join(ROOT, "ai-stock-platform", "api"))
pytest.importorskip("httpx")
import httpx
import time
from unittest.mock import AsyncMock, patch, MagicMock
from core.http_client import (
    HTTPClient, 
    HTTPClientConfig,
    get_http_client,
    safe_get_json,
    safe_post_json,
    cleanup_http_clients
)

class TestHTTPClientConfig:
    """Test HTTP client configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = HTTPClientConfig()
        
        # Check timeout configuration
        assert config.timeout.connect == 5.0
        assert config.timeout.read == 30.0
        assert config.timeout.write == 10.0
        assert config.timeout.pool == 10.0
        
        # Check connection limits
        assert config.limits.max_keepalive_connections == 20
        assert config.limits.max_connections == 100
        assert config.limits.keepalive_expiry == 30.0
        
        # Check retry configuration
        assert config.max_retries == 3
        assert config.retry_delay_base == 1.0
        assert config.retry_delay_max == 60.0
        
        # Check SSL configuration
        assert config.verify_ssl is True
        
        # Check default headers
        assert "User-Agent" in config.default_headers
        assert "Accept" in config.default_headers
        assert "Content-Type" in config.default_headers

class TestHTTPClient:
    """Test HTTP client functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return HTTPClientConfig()
    
    @pytest.fixture
    def client(self, config):
        """Create test HTTP client."""
        return HTTPClient(config)
    
    @pytest.mark.asyncio
    async def test_client_creation(self, client):
        """Test HTTP client creation and resource management."""
        async with client as c:
            assert c._client is not None
            assert not c._client.is_closed
        
        # Client should be closed after context manager exit
        assert client._client.is_closed
    
    @pytest.mark.asyncio
    async def test_retry_delay_calculation(self, client):
        """Test retry delay calculation with exponential backoff."""
        # Test exponential backoff
        delay1 = client._calculate_retry_delay(0)
        delay2 = client._calculate_retry_delay(1)
        delay3 = client._calculate_retry_delay(2)
        
        assert delay1 < delay2 < delay3
        assert delay1 >= 1.0  # Base delay + jitter
        assert delay3 <= 60.0  # Max delay
    
    @pytest.mark.asyncio
    async def test_retryable_error_detection(self, client):
        """Test retryable error detection logic."""
        # Request errors should be retryable
        request_error = httpx.RequestError("Connection failed")
        assert client._is_retryable_error(request_error)
        
        # Server errors should be retryable
        mock_response = MagicMock()
        mock_response.status_code = 500
        server_error = httpx.HTTPStatusError("Server error", request=MagicMock(), response=mock_response)
        assert client._is_retryable_error(server_error)
        
        # Rate limiting should be retryable
        mock_response.status_code = 429
        rate_limit_error = httpx.HTTPStatusError("Rate limited", request=MagicMock(), response=mock_response)
        assert client._is_retryable_error(rate_limit_error)
        
        # Client errors should not be retryable
        mock_response.status_code = 400
        client_error = httpx.HTTPStatusError("Bad request", request=MagicMock(), response=mock_response)
        assert not client._is_retryable_error(client_error)
    
    @pytest.mark.asyncio
    async def test_get_request_with_auth(self, client):
        """Test GET request with authentication."""
        with patch.object(client, '_make_request_with_retry') as mock_request:
            mock_response = MagicMock()
            mock_request.return_value = mock_response
            
            await client.get(
                url="https://api.example.com/data",
                auth_token="test_token"
            )
            
            # Verify request was made with auth header
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['headers']['Authorization'] == 'Bearer test_token'
    
    @pytest.mark.asyncio
    async def test_post_request_with_json(self, client):
        """Test POST request with JSON data."""
        with patch.object(client, '_make_request_with_retry') as mock_request:
            mock_response = MagicMock()
            mock_request.return_value = mock_response
            
            test_data = {"key": "value"}
            await client.post(
                url="https://api.example.com/data",
                json=test_data,
                auth_token="test_token"
            )
            
            # Verify request was made with JSON data and auth header
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['json'] == test_data
            assert call_args[1]['headers']['Authorization'] == 'Bearer test_token'

class TestGlobalHTTPClient:
    """Test global HTTP client functionality."""
    
    @pytest.mark.asyncio
    async def test_global_client_reuse(self):
        """Test that global client is reused across requests."""
        client1 = None
        client2 = None
        
        async with get_http_client() as client:
            client1 = client
        
        async with get_http_client() as client:
            client2 = client
        
        # Should be the same instance
        assert client1 is client2
    
    @pytest.mark.asyncio
    async def test_cleanup_global_client(self):
        """Test global client cleanup."""
        # Create global client
        async with get_http_client() as client:
            assert client is not None
        
        # Cleanup should close the client
        await cleanup_http_clients()
        
        # Note: We can't easily test if the client is closed without 
        # exposing internal state, but we can verify no exceptions are raised

class TestUtilityFunctions:
    """Test utility functions for common HTTP operations."""
    
    @pytest.mark.asyncio
    async def test_safe_get_json_success(self):
        """Test successful JSON GET request."""
        expected_data = {"key": "value"}
        
        with patch('core.http_client.get_http_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = expected_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            
            # Setup async context manager
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None
            
            result = await safe_get_json(
                url="https://api.example.com/data",
                auth_token="test_token"
            )
            
            assert result == expected_data
    
    @pytest.mark.asyncio
    async def test_safe_get_json_failure(self):
        """Test JSON GET request failure with default value."""
        default_value = {"error": "default"}
        
        with patch('core.http_client.get_http_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.RequestError("Connection failed")
            
            # Setup async context manager
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None
            
            result = await safe_get_json(
                url="https://api.example.com/data",
                default=default_value
            )
            
            assert result == default_value
    
    @pytest.mark.asyncio
    async def test_safe_post_json_success(self):
        """Test successful JSON POST request."""
        expected_data = {"result": "success"}
        post_data = {"input": "test"}
        
        with patch('core.http_client.get_http_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = expected_data
            mock_response.raise_for_status.return_value = None
            mock_client.post.return_value = mock_response
            
            # Setup async context manager
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None
            
            result = await safe_post_json(
                url="https://api.example.com/data",
                json_data=post_data,
                auth_token="test_token"
            )
            
            assert result == expected_data
    
    @pytest.mark.asyncio
    async def test_safe_post_json_failure(self):
        """Test JSON POST request failure with default value."""
        default_value = {"error": "default"}
        post_data = {"input": "test"}
        
        with patch('core.http_client.get_http_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.HTTPStatusError(
                "Server error", 
                request=MagicMock(), 
                response=MagicMock()
            )
            
            # Setup async context manager
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None
            
            result = await safe_post_json(
                url="https://api.example.com/data",
                json_data=post_data,
                default=default_value
            )
            
            assert result == default_value

class TestPerformanceOptimizations:
    """Test performance optimizations like connection pooling."""
    
    @pytest.mark.asyncio
    async def test_connection_reuse(self):
        """Test that connections are reused properly."""
        config = HTTPClientConfig()
        
        # Verify connection pool settings
        assert config.limits.max_keepalive_connections > 0
        assert config.limits.max_connections > 0
        assert config.limits.keepalive_expiry > 0
        
        # Test client creation with these settings
        client = HTTPClient(config)
        async with client as c:
            assert c._client.limits.max_keepalive_connections == config.limits.max_keepalive_connections
            assert c._client.limits.max_connections == config.limits.max_connections

class TestErrorHandling:
    """Test comprehensive error handling."""
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout error handling."""
        client = HTTPClient()
        
        with patch.object(client, '_client') as mock_client:
            mock_client.request.side_effect = httpx.TimeoutException("Request timed out")
            
            # Should retry on timeout
            with pytest.raises(httpx.TimeoutException):
                await client._make_request_with_retry("GET", "https://api.example.com/data")
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test connection error handling."""
        client = HTTPClient()
        
        with patch.object(client, '_client') as mock_client:
            mock_client.request.side_effect = httpx.ConnectError("Connection failed")
            
            # Should retry on connection error
            with pytest.raises(httpx.ConnectError):
                await client._make_request_with_retry("GET", "https://api.example.com/data")
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test rate limit handling with Retry-After header."""
        client = HTTPClient()
        
        with patch.object(client, '_client') as mock_client:
            # Mock rate limit response
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "2"}
            mock_client.request.return_value = mock_response
            
            # Should handle rate limiting
            with patch('asyncio.sleep') as mock_sleep:
                try:
                    await client._make_request_with_retry("GET", "https://api.example.com/data")
                except httpx.HTTPStatusError:
                    pass  # Expected after retries
                
                # Should have called sleep with retry delay
                mock_sleep.assert_called()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
