"""
Cache Implementation
Created: 2025-05-19 03:40:27
Author: daparthi001
"""
import json
import hashlib
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar, cast
import logging
import redis
from datetime import timedelta

from core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

class CacheBackend:
    """Interface for cache backends."""
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL."""
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        raise NotImplementedError
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        raise NotImplementedError

    def clear(self) -> None:
        """Clear all cache entries."""
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
    
    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
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

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self.client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

# Initialize Redis client
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        redis_client.ping()
        logger.info("Redis cache initialized successfully")
    except redis.RedisError as e:
        logger.error(f"Failed to initialize Redis cache: {e}")
        redis_client = None

# Create cache instance
cache = RedisCache(redis_client) if redis_client else None
