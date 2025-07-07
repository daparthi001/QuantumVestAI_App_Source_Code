"""
Comprehensive Error Handling Middleware for QuantumVestAI
Created: 2025-01-18
Author: AI Assistant

This middleware provides world-class error handling, graceful degradation,
and comprehensive logging for all application errors.
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Any
import traceback
import time
import json
from datetime import datetime

from utils.enhanced_error_handling import get_enhanced_renderer, create_error_response

logger = logging.getLogger("quantumvestai_ui.middleware")


class ComprehensiveErrorMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware that catches all exceptions
    and provides graceful degradation with detailed logging.
    """
    
    def __init__(self, app, templates=None, debug_mode: bool = False):
        super().__init__(app)
        self.templates = templates
        self.debug_mode = debug_mode
        self.error_count = 0
        self.start_time = time.time()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle request with comprehensive error catching"""
        
        # Generate request ID for tracking
        request_id = f"req-{int(time.time() * 1000)}"
        request.state.request_id = request_id
        
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        logger.info(f"[{request_id}] {method} {path} - Started")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add headers for debugging
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            logger.info(f"[{request_id}] {method} {path} - Completed {response.status_code} in {process_time:.3f}s")
            
            return response
            
        except HTTPException as http_exc:
            # Handle FastAPI HTTP exceptions
            process_time = time.time() - start_time
            logger.warning(f"[{request_id}] {method} {path} - HTTP {http_exc.status_code}: {http_exc.detail}")
            
            return await self._handle_http_exception(request, http_exc, request_id)
            
        except Exception as exc:
            # Handle all other exceptions
            self.error_count += 1
            process_time = time.time() - start_time
            
            logger.error(f"[{request_id}] {method} {path} - Error after {process_time:.3f}s: {str(exc)}")
            logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
            
            return await self._handle_general_exception(request, exc, request_id)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException, request_id: str) -> Response:
        """Handle FastAPI HTTP exceptions with appropriate responses"""
        
        if self._is_api_request(request):
            # Return JSON for API requests
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": True,
                    "status_code": exc.status_code,
                    "detail": exc.detail,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )
        else:
            # Return HTML for web requests
            if exc.status_code == 404:
                return await self._create_404_response(request, request_id)
            elif exc.status_code == 403:
                return await self._create_403_response(request, request_id)
            elif exc.status_code == 401:
                return await self._create_401_response(request, request_id)
            else:
                return await self._create_generic_error_response(request, exc, request_id)
    
    async def _handle_general_exception(self, request: Request, exc: Exception, request_id: str) -> Response:
        """Handle general exceptions with graceful degradation"""
        
        # Determine error category
        error_category = self._categorize_error(exc)
        
        if self._is_api_request(request):
            # Return JSON error for API requests
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "status_code": 500,
                    "detail": "Internal server error" if not self.debug_mode else str(exc),
                    "error_category": error_category,
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers={"X-Request-ID": request_id}
            )
        else:
            # Return HTML error page for web requests
            if self.templates:
                try:
                    # Try to use enhanced template renderer
                    renderer = get_enhanced_renderer(self.templates)
                    return renderer.render_template_safe(
                        "errors/500.html",
                        {
                            "request": request,
                            "error": exc,
                            "error_category": error_category,
                            "request_id": request_id
                        },
                        request
                    )
                except Exception as template_error:
                    logger.error(f"[{request_id}] Template error handler also failed: {template_error}")
                    # Fall back to simple error response
                    return create_error_response(exc, request, fallback_title="System Error")
            else:
                # No templates available, create simple error response
                return create_error_response(exc, request, fallback_title="System Error")
    
    def _categorize_error(self, exc: Exception) -> str:
        """Categorize errors for better handling"""
        error_str = str(exc).lower()
        exc_type = type(exc).__name__.lower()
        
        if "template" in error_str or "jinja" in error_str:
            return "template_error"
        elif "filter" in error_str and "named" in error_str:
            return "template_filter_error"
        elif "connection" in error_str or "timeout" in error_str:
            return "connection_error"
        elif "database" in error_str or "sql" in error_str:
            return "database_error"
        elif "permission" in error_str or "forbidden" in error_str:
            return "permission_error"
        elif "validation" in error_str or "invalid" in error_str:
            return "validation_error"
        elif "import" in error_str or "module" in error_str:
            return "import_error"
        else:
            return "unknown_error"
    
    def _is_api_request(self, request: Request) -> bool:
        """Determine if request is for API endpoint"""
        path = request.url.path
        accept_header = request.headers.get("accept", "")
        
        return (
            path.startswith("/api/") or
            path.startswith("/health") or
            "application/json" in accept_header or
            request.method in ["PUT", "PATCH", "DELETE"]
        )
    
    async def _create_404_response(self, request: Request, request_id: str) -> HTMLResponse:
        """Create 404 not found response"""
        if self.templates:
            try:
                renderer = get_enhanced_renderer(self.templates)
                return renderer.render_template_safe(
                    "errors/404.html",
                    {
                        "request": request,
                        "path": request.url.path,
                        "request_id": request_id
                    },
                    request
                )
            except Exception:
                pass
        
        # Fallback 404 page
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Page Not Found - QuantumVestAI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-1">404</h1>
                    <h2>Page Not Found</h2>
                    <p class="lead">The page you're looking for doesn't exist.</p>
                    <p>Path: {request.url.path}</p>
                    <a href="/" class="btn btn-primary">Go Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(
            content=html_content,
            status_code=404,
            headers={"X-Request-ID": request_id}
        )
    
    async def _create_403_response(self, request: Request, request_id: str) -> HTMLResponse:
        """Create 403 forbidden response"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Access Forbidden - QuantumVestAI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-1">403</h1>
                    <h2>Access Forbidden</h2>
                    <p class="lead">You don't have permission to access this resource.</p>
                    <a href="/" class="btn btn-primary">Go Home</a>
                    <a href="/login" class="btn btn-secondary">Login</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(
            content=html_content,
            status_code=403,
            headers={"X-Request-ID": request_id}
        )
    
    async def _create_401_response(self, request: Request, request_id: str) -> HTMLResponse:
        """Create 401 unauthorized response"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Authentication Required - QuantumVestAI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-1">401</h1>
                    <h2>Authentication Required</h2>
                    <p class="lead">You need to log in to access this resource.</p>
                    <a href="/login" class="btn btn-primary">Login</a>
                    <a href="/" class="btn btn-secondary">Go Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(
            content=html_content,
            status_code=401,
            headers={"X-Request-ID": request_id}
        )
    
    async def _create_generic_error_response(self, request: Request, exc: HTTPException, request_id: str) -> HTMLResponse:
        """Create generic error response for HTTP exceptions"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error {exc.status_code} - QuantumVestAI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-1">{exc.status_code}</h1>
                    <h2>Error</h2>
                    <p class="lead">{exc.detail}</p>
                    <a href="/" class="btn btn-primary">Go Home</a>
                    <button onclick="history.back()" class="btn btn-secondary">Go Back</button>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(
            content=html_content,
            status_code=exc.status_code,
            headers={"X-Request-ID": request_id}
        )
    
    def get_error_stats(self) -> dict:
        """Get error statistics for monitoring"""
        uptime = time.time() - self.start_time
        return {
            "total_errors": self.error_count,
            "uptime_seconds": uptime,
            "error_rate": self.error_count / (uptime / 3600) if uptime > 0 else 0,  # errors per hour
            "status": "healthy" if self.error_count < 10 else "degraded"
        }