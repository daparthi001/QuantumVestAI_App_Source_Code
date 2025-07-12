"""
HTTP Client Configuration for QuantumVestAI UI
Centralized httpx client with proper configuration, connection pooling,
error handling, and performance optimizations.

Last updated: 2025-01-18
Updated by: daparthi001
"""

import httpx
import logging
import asyncio
import os
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import time
import random

# Setup logging
logger = logging.getLogger(__name__)

class HTTPClientConfig:
    """Configuration class for HTTP client settings."""
    
    def __init__(self):
        # Connection and timeout settings
        self.timeout = httpx.Timeout(
            connect=float(os.getenv("HTTPX_CONNECT_TIMEOUT", "5.0")),
            read=float(os.getenv("HTTPX_READ_TIMEOUT", "30.0")),
            write=float(os.getenv("HTTPX_WRITE_TIMEOUT", "10.0")),
            pool=float(os.getenv("HTTPX_POOL_TIMEOUT", "10.0"))
        )
        
        # Connection pool limits
        self.limits = httpx.Limits(
            max_keepalive_connections=int(os.getenv("HTTPX_MAX_KEEPALIVE", "20")),
            max_connections=int(os.getenv("HTTPX_MAX_CONNECTIONS", "100")),
            keepalive_expiry=float(os.getenv("HTTPX_KEEPALIVE_EXPIRY", "30.0"))
        )
        
        # Retry configuration
        self.max_retries = int(os.getenv("HTTPX_MAX_RETRIES", "3"))
        self.retry_delay_base = float(os.getenv("HTTPX_RETRY_DELAY_BASE", "1.0"))
        self.retry_delay_max = float(os.getenv("HTTPX_RETRY_DELAY_MAX", "60.0"))
        
        # SSL/TLS configuration
        self.verify_ssl = os.getenv("HTTPX_VERIFY_SSL", "true").lower() == "true"
        
        # Default headers
        self.default_headers = {
            "User-Agent": f"QuantumVestAI-UI/{os.getenv('APP_VERSION', '1.0.0')}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Client-Version": os.getenv("APP_VERSION", "1.0.0"),
            "X-Client-Platform": "web"
        }

class RetryableHTTPError(Exception):
    """Exception for retryable HTTP errors."""
    pass

class NonRetryableHTTPError(Exception):
    """Exception for non-retryable HTTP errors."""
    pass

class HTTPClient:
    """Enhanced HTTP client with connection pooling, retry logic, and proper error handling."""
    
    def __init__(self, config: Optional[HTTPClientConfig] = None):
        self.config = config or HTTPClientConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._session_created = False
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def _ensure_client(self):
        """Ensure HTTP client is created and ready."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=self.config.limits,
                verify=self.config.verify_ssl,
                headers=self.config.default_headers,
                follow_redirects=True
            )
            self._session_created = True
            logger.debug("HTTP client created with connection pooling")
    
    async def close(self):
        """Close the HTTP client and cleanup resources."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._session_created = False
            logger.debug("HTTP client closed")
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        delay = min(
            self.config.retry_delay_base * (2 ** attempt),
            self.config.retry_delay_max
        )
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.1, 0.5)
        return delay + jitter
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        if isinstance(error, httpx.RequestError):
            # Network errors, connection errors, timeouts are retryable
            return True
        elif isinstance(error, httpx.HTTPStatusError):
            # Retry on server errors (5xx) and rate limiting (429)
            return error.response.status_code in [429, 500, 502, 503, 504]
        return False
    
    def _get_retry_after_delay(self, response: httpx.Response) -> Optional[float]:
        """Get retry delay from Retry-After header."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                # Could be a date format, but we'll use default delay
                pass
        return None
    
    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        await self._ensure_client()
        
        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    **kwargs
                )
                
                # Check if we should retry based on status code
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < self.config.max_retries:
                        # Handle rate limiting with Retry-After header
                        if response.status_code == 429:
                            retry_delay = self._get_retry_after_delay(response)
                            if retry_delay:
                                logger.warning(
                                    f"Rate limited. Retrying after {retry_delay}s (attempt {attempt + 1}/{self.config.max_retries + 1})"
                                )
                                await asyncio.sleep(retry_delay)
                                continue
                        
                        # Calculate standard retry delay
                        retry_delay = self._calculate_retry_delay(attempt)
                        logger.warning(
                            f"HTTP {response.status_code} error. Retrying after {retry_delay:.2f}s (attempt {attempt + 1}/{self.config.max_retries + 1})"
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        # Max retries exceeded
                        raise httpx.HTTPStatusError(
                            f"HTTP {response.status_code} error after {self.config.max_retries} retries",
                            request=response.request,
                            response=response
                        )
                
                return response
                
            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.config.max_retries and self._is_retryable_error(e):
                    retry_delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        f"Request error: {str(e)}. Retrying after {retry_delay:.2f}s (attempt {attempt + 1}/{self.config.max_retries + 1})"
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    raise
            
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error during request: {str(e)}")
                raise
        
        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        
        raise Exception("Request failed after all retries")
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Make GET request with retry logic."""
        if auth_token:
            headers = headers or {}
            headers["Authorization"] = f"Bearer {auth_token}"
        
        return await self._make_request_with_retry(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            **kwargs
        )
    
    async def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], bytes, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Make POST request with retry logic."""
        if auth_token:
            headers = headers or {}
            headers["Authorization"] = f"Bearer {auth_token}"
        
        return await self._make_request_with_retry(
            method="POST",
            url=url,
            data=data,
            json=json,
            headers=headers,
            **kwargs
        )
    
    async def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], bytes, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Make PUT request with retry logic."""
        if auth_token:
            headers = headers or {}
            headers["Authorization"] = f"Bearer {auth_token}"
        
        return await self._make_request_with_retry(
            method="PUT",
            url=url,
            data=data,
            json=json,
            headers=headers,
            **kwargs
        )
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Make DELETE request with retry logic."""
        if auth_token:
            headers = headers or {}
            headers["Authorization"] = f"Bearer {auth_token}"
        
        return await self._make_request_with_retry(
            method="DELETE",
            url=url,
            headers=headers,
            **kwargs
        )

# Global HTTP client instance
_global_client: Optional[HTTPClient] = None

@asynccontextmanager
async def get_http_client():
    """Get a global HTTP client instance with proper lifecycle management."""
    global _global_client
    
    if _global_client is None:
        _global_client = HTTPClient()
    
    await _global_client._ensure_client()
    
    try:
        yield _global_client
    finally:
        # Don't close the global client, let it be reused
        pass

async def create_http_client() -> HTTPClient:
    """Create a new HTTP client instance."""
    return HTTPClient()

# Utility functions for common HTTP operations
async def safe_get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
    default: Any = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Safely make a GET request and return JSON response.
    Returns default value if request fails.
    """
    try:
        async with get_http_client() as client:
            response = await client.get(
                url=url,
                params=params,
                headers=headers,
                auth_token=auth_token
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JSON from {url}: {str(e)}")
        return default

async def safe_post_json(
    url: str,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
    default: Any = None
) -> Any:
    """
    Safely make a POST request and return JSON response.
    Returns default value if request fails.
    """
    try:
        async with get_http_client() as client:
            response = await client.post(
                url=url,
                json=json_data,
                headers=headers,
                auth_token=auth_token
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Failed to post JSON to {url}: {str(e)}")
        return default

# Cleanup function to be called on application shutdown
async def cleanup_http_clients():
    """Cleanup all HTTP clients on application shutdown."""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None
    logger.info("HTTP clients cleaned up")
