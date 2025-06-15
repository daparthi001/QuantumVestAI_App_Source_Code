from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting basic metrics on requests.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add metrics to response headers for debugging
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log metrics data (can be extended to push to a metrics system)
        logger.debug(
            f"Request: {request.method} {request.url.path} - "
            f"Time: {process_time:.4f}s - "
            f"Status: {response.status_code}"
        )
        
        return response