"""
Logging Middleware
Created: 2025-05-21 05:17:43
Author: daparthi001
"""
import time
import uuid
from typing import Callable

from core.logger import logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Log request and response details"""
        # Generate request ID if not present
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Add request ID to response headers
        request.state.request_id = request_id
        
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
            
            # Add request ID to response
            response.headers['X-Request-ID'] = request_id
            
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
