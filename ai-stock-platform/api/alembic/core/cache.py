import json
import hashlib
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast
import logging
import redis
from datetime import timedelta

from core.config import settings

logger = logging.getLogger("api")

# Type variable for generic function return type
T = TypeVar("T")

# Initialize Redis client if URL is configured
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()  # Test connection
        logger.info("Redis cache initialized successfully")
    except redis.RedisError as e:
        logger.error(f"Failed to initialize Redis cache: {e}")
        redis_client = None

class CacheBackend:
    """Interface for cache backends."""
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        raise NotImplementedError
    
    def set(
        self, key: str, value: str, ttl_seconds: int = 300
    ) -> None:
        """Set value in cache with TTL."""
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError

class RedisCache(CacheBackend):
    """Redis cache implementation."""
    
    def __init__(self, client: redis.Redis):
        """Initialize with Redis client."""
        self.client = client
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        try:
            value = self.client.get(key)
            return value.decode("utf-8") if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(
        self, key: str, value: str, ttl_seconds: int = 300
    ) -> None:
        """Set value in Redis with TTL."""
        try:
            self.client.set(key, value, ex=ttl_seconds)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def delete(self, key: str) -> None:
        """Delete value from Redis."""
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

class InMemoryCache(CacheBackend):
    """Simple in-memory cache implementation."""
    
    def __init__(self):
        """Initialize in-memory cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get value from in-memory cache."""
        cache_entry = self.cache.get(key)
        if cache_entry and cache_entry["expires"] > time.time():
            return cache_entry["value"]
        elif cache_entry:
            # Entry expired, delete it
            del self.cache[key]
        return None
    
    def set(
        self, key: str, value: str, ttl_seconds: int = 300
    ) -> None:
        """Set value in in-memory cache with TTL."""
        expires = time.time() + ttl_seconds
        self.cache[key] = {
            "value": value,
            "expires": expires
        }
    
    def delete(self, key: str) -> None:
        """Delete value from in-memory cache."""
        if key in self.cache:
            del self.cache[key]
    
    def exists(self, key: str) -> bool:
        """Check if key exists in in-memory cache."""
        cache_entry = self.cache.get(key)
        if cache_entry and cache_entry["expires"] > time.time():
            return True
        elif cache_entry:
            # Entry expired, delete it
            del self.cache[key]
        return False

# Determine which cache backend to use
cache_backend: CacheBackend
if redis_client:
    cache_backend = RedisCache(redis_client)
    logger.info("Using Redis cache backend")
else:
    cache_backend = InMemoryCache()
    logger.info("Using in-memory cache backend")

def cache(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool, type(None))):
                    key_parts.append(str(arg))
            
            # Add kwargs to key, sorted by key name for consistency
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                if isinstance(v, (str, int, float, bool, type(None))):
                    key_parts.append(f"{k}:{v}")
            
            # Generate final key
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache_backend.get(cache_key)
            if cached_value:
                try:
                    return cast(T, json.loads(cached_value))
                except json.JSONDecodeError:
                    # If JSON parsing fails, delete invalid cache entry
                    cache_backend.delete(cache_key)
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Cache result if not None
            if result is not None:
                try:
                    cache_backend.set(
                        cache_key,
                        json.dumps(result),
                        ttl_seconds=ttl_seconds
                    )
                except (TypeError, OverflowError) as e:
                    logger.warning(f"Failed to cache result: {e}")
            
            return result
        
        return wrapper
    
    return decorator

def invalidate_cache(key_prefix: str) -> None:
    """
    Invalidate cache keys with the specified prefix.
    
    In a real implementation with Redis, you would use SCAN to find keys
    with the specified prefix and delete them.
    
    For the in-memory cache, this is a no-op since we can't efficiently
    search for keys by prefix.
    """
    if isinstance(cache_backend, RedisCache) and redis_client:
        try:
            # Find all keys with the specified prefix
            keys = []
            for key in redis_client.scan_iter(f"{key_prefix}*"):
                keys.append(key)
            
            # Delete the keys
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys with prefix {key_prefix}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
