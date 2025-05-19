"""
Core Middleware Implementation
Created: 2025-05-19 03:43:23
Author: daparthi001
"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from typing import Callable, Awaitable
import asyncio
from datetime import datetime

from api.core.exceptions import RateLimitError
from api.core.config import settings
from api.core.cache import cache

logger = logging.getLogger("api")

async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Add unique request ID to each request"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.exception(
            f"Error processing request: {str(e)}",
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id
            }
        )

async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Rate limiting middleware"""
    if request.url.path in ["/health", "/metrics", "/docs", "/redoc"]:
        return await call_next(request)

    # Get client identifier
    client_id = request.headers.get("X-API-Key") or request.client.host
    
    # Rate limit key
    rate_limit_key = f"ratelimit:{client_id}:{request.url.path}"
    
    if cache:
        try:
            # Check rate limit
            requests = int(cache.get(rate_limit_key) or 0)
            if requests >= settings.RATE_LIMIT_MAX_REQUESTS:
                raise RateLimitError()
            
            # Increment request count
            cache.set(
                rate_limit_key,
                str(requests + 1),
                ttl_seconds=settings.RATE_LIMIT_WINDOW_SECONDS
            )
        except RateLimitError:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "retry_after": settings.RATE_LIMIT_WINDOW_SECONDS
                }
            )
        except Exception as e:
            logger.error(f"Rate limit error: {str(e)}")
    
    return await call_next(request)

async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Collect metrics for each request"""
    start_time = time.time()
    
    # Get client info
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    method = request.method
    path = request.url.path
    
    try:
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # Log metrics
        logger.info(
            "Request processed",
            extra={
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "status_code": status_code,
                "process_time": process_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        
        logger.exception(
            f"Request failed: {str(e)}",
            extra={
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "process_time": process_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )