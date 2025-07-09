"""
Error Handlers
Created: 2025-06-16 03:41:30
Author: daparthi001
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Set up templates
try:
    # Try to use templates from app state first
    templates_dir = Path(__file__).parent.parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    logger.info(f"Templates initialized from: {templates_dir}")
except Exception as e:
    # Fallback settings
    templates_dir = Path("templates")
    logger.warning(f"Using fallback template directory: {templates_dir}")
    try:
        templates = Jinja2Templates(directory=str(templates_dir))
    except Exception as fallback_error:
        logger.error(f"Error setting up templates: {fallback_error}")
        templates = None

def setup_error_handlers(app: FastAPI):
    """Set up error handlers for the application"""
    logger.info("Setting up error handlers")
    
    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc: HTTPException):
        accept = request.headers.get("Accept", "")
        
        if "text/html" in accept and templates:
            # Return HTML response for browser requests
            return get_templates(request).TemplateResponse(
                "errors/401.html",
                {"request": request, "detail": exc.detail},
                status_code=401
            )
        else:
            # Return JSON response for API requests
            return JSONResponse(
                status_code=401,
                content={"detail": exc.detail or "Unauthorized"},
                headers=getattr(exc, "headers", None)
            )
    
    @app.exception_handler(403)
    async def forbidden_handler(request: Request, exc: HTTPException):
        accept = request.headers.get("Accept", "")
        
        if "text/html" in accept and templates:
            # Return HTML response for browser requests
            return get_templates(request).TemplateResponse(
                "errors/403.html",
                {"request": request, "detail": exc.detail},
                status_code=403
            )
        else:
            # Return JSON response for API requests
            return JSONResponse(
                status_code=403,
                content={"detail": exc.detail or "Forbidden"},
                headers=getattr(exc, "headers", None)
            )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        accept = request.headers.get("Accept", "")
        
        if "text/html" in accept and templates:
            # Return HTML response for browser requests
            return get_templates(request).TemplateResponse(
                "errors/404.html",
                {"request": request, "detail": exc.detail},
                status_code=404
            )
        else:
            # Return JSON response for API requests
            return JSONResponse(
                status_code=404,
                content={"detail": exc.detail or "Not Found"},
                headers=getattr(exc, "headers", None)
            )
    
    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc: Exception):
        logger.error(f"Server error: {exc}", exc_info=True)
        accept = request.headers.get("Accept", "")
        
        if "text/html" in accept and templates:
            # Return HTML response for browser requests
            return get_templates(request).TemplateResponse(
                "errors/500.html",
                {"request": request},
                status_code=500
            )
        else:
            # Return JSON response for API requests
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )