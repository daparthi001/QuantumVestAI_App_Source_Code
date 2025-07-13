"""
Improved HTTPX client configuration with proper error handling, timeouts, and connection management.
Updated: 2025-07-06 19:11:39
Author: daparthi001
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import httpx
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

# Configure logging
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_CONNECTIONS = 100
DEFAULT_MAX_KEEPALIVE_CONNECTIONS = 20
DEFAULT_KEEPALIVE_EXPIRY = 30.0

class HTTPXClientManager:
    """Singleton HTTPX client manager with proper configuration and error handling"""
    
    _instance = None
    _client: Optional[httpx.AsyncClient] = None
    _sync_client: Optional[httpx.Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._setup_clients()
    
    def _setup_clients(self):
        """Setup both async and sync clients with proper configuration"""
        
        # Common configuration
        timeout = httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=30.0,
            pool=60.0
        )
        
        limits = httpx.Limits(
            max_connections=DEFAULT_MAX_CONNECTIONS,
            max_keepalive_connections=DEFAULT_MAX_KEEPALIVE_CONNECTIONS,
            keepalive_expiry=DEFAULT_KEEPALIVE_EXPIRY
        )
        
        headers = {
            'User-Agent': 'QuantumVestAI/1.0',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Setup async client
        self._client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            headers=headers,
            follow_redirects=True,
            verify=True,  # SSL verification
            http2=True   # Enable HTTP/2 support
        )
        
        # Setup sync client
        self._sync_client = httpx.Client(
            timeout=timeout,
            limits=limits,
            headers=headers,
            follow_redirects=True,
            verify=True,
            http2=True
        )
    
    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get the async client instance"""
        if self._client is None or self._client.is_closed:
            self._setup_clients()
        return self._client
    
    @property
    def sync_client(self) -> httpx.Client:
        """Get the sync client instance"""
        if self._sync_client is None or self._sync_client.is_closed:
            self._setup_clients()
        return self._sync_client
    
    async def close_async(self):
        """Close the async client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def close_sync(self):
        """Close the sync client"""
        if self._sync_client and not self._sync_client.is_closed:
            self._sync_client.close()
            self._sync_client = None
    
    async def __aenter__(self):
        return self.async_client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_async()

# Global client manager instance
client_manager = HTTPXClientManager()

class HTTPXService:
    """Enhanced HTTPX service with comprehensive error handling and retry logic"""
    
    def __init__(self, base_url: str = "", auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session_headers = {}
        
        if auth_token:
            self.session_headers['Authorization'] = f'Bearer {auth_token}'
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers with authentication and defaults"""
        final_headers = self.session_headers.copy()
        if headers:
            final_headers.update(headers)
        return final_headers
    
    def _prepare_url(self, url: str) -> str:
        """Prepare the full URL"""
        if url.startswith('http'):
            return url
        return f"{self.base_url}/{url.lstrip('/')}"
    
    @retry(
        stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
    )
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """Enhanced GET request with retry logic"""
        try:
            final_url = self._prepare_url(url)
            final_headers = self._prepare_headers(headers)
            
            logger.debug(f"Making GET request to: {final_url}")
            
            response = await client_manager.async_client.get(
                final_url,
                params=params,
                headers=final_headers,
                timeout=timeout or DEFAULT_TIMEOUT
            )
            
            response.raise_for_status()
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {str(e)}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in GET request: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException))
    )
    async def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """Enhanced POST request with retry logic"""
        try:
            final_url = self._prepare_url(url)
            final_headers = self._prepare_headers(headers)
            
            logger.debug(f"Making POST request to: {final_url}")
            
            kwargs = {
                'url': final_url,
                'headers': final_headers,
                'timeout': timeout or DEFAULT_TIMEOUT
            }
            
            if json_data is not None:
                kwargs['json'] = json_data
            elif data is not None:
                if isinstance(data, dict):
                    kwargs['data'] = data
                else:
                    kwargs['content'] = data
            
            response = await client_manager.async_client.post(**kwargs)
            response.raise_for_status()
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {str(e)}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in POST request: {str(e)}")
            raise
    
    async def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """Enhanced PUT request"""
        try:
            final_url = self._prepare_url(url)
            final_headers = self._prepare_headers(headers)
            
            kwargs = {
                'url': final_url,
                'headers': final_headers,
                'timeout': timeout or DEFAULT_TIMEOUT
            }
            
            if json_data is not None:
                kwargs['json'] = json_data
            elif data is not None:
                if isinstance(data, dict):
                    kwargs['data'] = data
                else:
                    kwargs['content'] = data
            
            response = await client_manager.async_client.put(**kwargs)
            response.raise_for_status()
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in PUT request: {str(e)}")
            raise
    
    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """Enhanced DELETE request"""
        try:
            final_url = self._prepare_url(url)
            final_headers = self._prepare_headers(headers)
            
            response = await client_manager.async_client.delete(
                final_url,
                headers=final_headers,
                timeout=timeout or DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in DELETE request: {str(e)}")
            raise

# Context manager for HTTPX client
@asynccontextmanager
async def httpx_client():
    """Context manager for HTTPX client with proper cleanup"""
    try:
        yield client_manager.async_client
    finally:
        # Client will be reused, no need to close here
        pass

# Utility functions
async def safe_request(
    method: str,
    url: str,
    **kwargs
) -> Optional[httpx.Response]:
    """Make a safe HTTP request with comprehensive error handling"""
    try:
        service = HTTPXService()
        
        if method.upper() == 'GET':
            return await service.get(url, **kwargs)
        elif method.upper() == 'POST':
            return await service.post(url, **kwargs)
        elif method.upper() == 'PUT':
            return await service.put(url, **kwargs)
        elif method.upper() == 'DELETE':
            return await service.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
    except Exception as e:
        logger.error(f"Safe request failed: {str(e)}")
        return None

def create_httpx_service(base_url: str = "", auth_token: Optional[str] = None) -> HTTPXService:
    """Factory function to create HTTPXService instance"""
    return HTTPXService(base_url=base_url, auth_token=auth_token)

# Cleanup function
async def cleanup_httpx_clients():
    """Cleanup HTTPX clients on application shutdown"""
    await client_manager.close_async()
    client_manager.close_sync()
