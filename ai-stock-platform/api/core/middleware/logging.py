"""
Logging Middleware
Created: 2025-05-20 21:42:17
Author: daparthi001
"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.logging import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Log request and response details"""
        # Generate request ID
        request_id = request.headers.get('X-Request-ID', '')
        
        # Log request
        logger.info(
            "Request [%s] %s %s",
            request_id,
            request.method,
            request.url.path
        )
        
        # Track timing
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "Response [%s] %s %s - Status: %d - Duration: %.3fs",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                duration
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                "Error [%s] %s %s - %s",
                request_id,
                request.method,
                request.url.path,
                str(e),
                exc_info=True
            )
            raise
