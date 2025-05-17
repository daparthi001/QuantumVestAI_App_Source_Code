from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from typing import Callable, Awaitable

from api.core.exceptions import RateLimitError

logger = logging.getLogger("api")

async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Middleware for rate limiting requests.
    
    This is a simplified version. In production, you'd typically use Redis
    to track request counts and implement proper rate limiting algorithms
    like token bucket or sliding window.
    """
    # Skip rate limiting for certain paths
    if any(request.url.path.startswith(path) for path in ["/api/docs", "/api/openapi.json", "/health"]):
        return await call_next(request)
    
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    
    # In a real implementation, check rate limit in Redis
    # For now, just pass through all requests
    
    try:
        # Continue with the request
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(
            f"Error in rate limit middleware: {str(e)}",
            extra={
                "client_ip": client_ip,
                "path": request.url.path,
            }
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware for collecting metrics on API requests."""
    start_time = time.time()
    
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    
    # Track metrics
    method = request.method
    path = request.url.path
    
    try:
        # Process request
        response = await call_next(request)
        
        # Record response time and status
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # In a real implementation, you'd store these metrics
        # in Prometheus or another metrics system
        
        # Add timing header to response
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        
        logger.exception(
            f"Error in metrics middleware: {str(e)}",
            extra={
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "process_time": process_time,
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )