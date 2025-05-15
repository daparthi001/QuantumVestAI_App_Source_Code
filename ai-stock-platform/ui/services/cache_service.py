# ui/services/cache_service.py
from functools import wraps
from cachetools import TTLCache
import hashlib
import json
from typing import Any, Callable

# Cache with a 5-minute TTL and max of 1000 items
cache = TTLCache(maxsize=1000, ttl=300)

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