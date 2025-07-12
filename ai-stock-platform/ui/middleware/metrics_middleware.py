"""
Metrics Middleware
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 03:41:30 by daparthi001
"""
import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# Configure logging
logger = logging.getLogger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect metrics on request/response cycle
    """
    def __init__(self, app):
        super().__init__(app)
        logger.info("Metrics middleware initialized")
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Record start time
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log performance data
        logger.debug(f"Path: {request.url.path} | Method: {request.method} | Time: {process_time:.4f}s")
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
