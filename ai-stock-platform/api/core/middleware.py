"""
Custom middleware for the API.
"""
import logging
import time
import uuid

from core import settings
from core.config import settings
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request/response details."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host
            }
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Response: {response.status_code} ({process_time:.2f}ms)",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Handle exceptions globally."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(
                "Unhandled exception",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "error": str(e)
                }
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": str(e) if request.app.debug else None,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
