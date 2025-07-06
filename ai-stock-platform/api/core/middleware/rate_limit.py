"""
Rate Limiting Middleware
Created: 2025-01-09
Author: AI Assistant
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict, Callable
from collections import defaultdict

from ..exceptions import RateLimitError
from ..responses import create_rate_limit_response

logger = logging.getLogger("api")


class InMemoryRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 10, "window": 60},      # 10 auth requests per minute
            "high_volume": {"requests": 1000, "window": 60}  # 1000 requests per minute for high volume endpoints
        }
    
    def is_rate_limited(self, client_id: str, endpoint_type: str = "default") -> bool:
        """Check if client is rate limited"""
        now = time.time()
        limit_config = self.rate_limits.get(endpoint_type, self.rate_limits["default"])
        window = limit_config["window"]
        max_requests = limit_config["requests"]
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if now - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= max_requests:
            return True
        
        # Add current request
        self.requests[client_id].append(now)
        return False
    
    def get_rate_limit_info(self, client_id: str, endpoint_type: str = "default") -> Dict[str, int]:
        """Get rate limit info for client"""
        now = time.time()
        limit_config = self.rate_limits.get(endpoint_type, self.rate_limits["default"])
        window = limit_config["window"]
        max_requests = limit_config["requests"]
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if now - req_time < window
        ]
        
        current_requests = len(self.requests[client_id])
        remaining = max(0, max_requests - current_requests)
        
        return {
            "limit": max_requests,
            "remaining": remaining,
            "used": current_requests,
            "window": window
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, rate_limiter: InMemoryRateLimiter = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or InMemoryRateLimiter()
        self.exempt_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier"""
        # Use X-Forwarded-For header if available, otherwise use client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Include user agent for better identification
        user_agent = request.headers.get("User-Agent", "unknown")
        return f"{client_ip}:{hash(user_agent) % 10000}"
    
    def get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if path.startswith("/api/v1/auth/"):
            return "auth"
        elif path.startswith("/api/v1/analytics/"):
            return "high_volume"
        else:
            return "default"
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for exempt paths
        path = request.url.path
        if any(path.startswith(exempt_path) for exempt_path in self.exempt_paths):
            return await call_next(request)
        
        # Get client ID and endpoint type
        client_id = self.get_client_id(request)
        endpoint_type = self.get_endpoint_type(path)
        
        # Check rate limit
        if self.rate_limiter.is_rate_limited(client_id, endpoint_type):
            logger.warning(f"Rate limit exceeded for client {client_id} on {path}")
            
            # Get rate limit info
            rate_info = self.rate_limiter.get_rate_limit_info(client_id, endpoint_type)
            
            error_response = create_rate_limit_response(
                message=f"Rate limit exceeded. Try again in {rate_info['window']} seconds.",
                request_id=getattr(request.state, 'request_id', None)
            )
            
            headers = {
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": str(rate_info["remaining"]),
                "X-RateLimit-Used": str(rate_info["used"]),
                "X-RateLimit-Window": str(rate_info["window"]),
                "Retry-After": str(rate_info["window"])
            }
            
            return JSONResponse(
                status_code=429,
                content=error_response,
                headers=headers
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        rate_info = self.rate_limiter.get_rate_limit_info(client_id, endpoint_type)
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Used"] = str(rate_info["used"])
        response.headers["X-RateLimit-Window"] = str(rate_info["window"])
        
        return response