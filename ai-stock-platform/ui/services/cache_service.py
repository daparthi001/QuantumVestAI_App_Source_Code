from functools import wraps
from cachetools import TTLCache
import hashlib
import json
from typing import Any, Callable, Dict, Optional, List

from .api_client import APIClient

# Cache with a 5-minute TTL and max of 1000 items
cache = TTLCache(maxsize=1000, ttl=300)

class CacheService:
    """Service for handling data caching and retrieval"""
    
    def __init__(self, api_client=None):
        """Initialize the cache service with an optional API client"""
        self.api_client = api_client or APIClient()
    
    def clear_cache(self):
        """Clear all caches"""
        cache.clear()

    def get_stock_info(self, ticker: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get stock information with caching using the class instance method"""
        return get_stock_info(ticker, token=token)

    def get_stock_history(self, ticker: str, period: str = "1y", token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get stock price history with caching"""
        # This would typically use a cache decorator, but we're calling the module function for now
        client = self.api_client if self.api_client else APIClient(token=token)
        return client.get(f"/stocks/{ticker}/history", params={"period": period})

def cached(key_prefix: str):
    """
    Decorator for caching API responses
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip cache if token is provided (personalized data)
            if "token" in kwargs and kwargs["token"]:
                return func(*args, **kwargs)
            
            # Generate cache key
            key_parts = [key_prefix, str(args)]
            
            # Add non-token kwargs to key
            kwargs_for_key = {k: v for k, v in kwargs.items() if k != "token"}
            key_parts.append(json.dumps(kwargs_for_key, sort_keys=True))
            
            cache_key = hashlib.md5("_".join(key_parts).encode()).hexdigest()
            
            # Check cache
            if cache_key in cache:
                return cache[cache_key]
            
            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache[cache_key] = result
            
            return result
        
        return wrapper
    
    return decorator

# Apply cache to service functions
@cached("stock_info")
def get_stock_info(ticker: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = APIClient(token=token)
    return client.get(f"/stocks/{ticker}")
