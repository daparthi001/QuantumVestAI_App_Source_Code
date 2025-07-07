"""
Main application file for QuantumVestAI UI (Enhanced)
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""
import os
import json
import requests
from fastapi import FastAPI, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import logging
from pathlib import Path
from logging.config import dictConfig
import sys

# CRITICAL FIX: Define BASE_DIR before using it
BASE_DIR = Path(__file__).resolve().parent

# Configure enhanced logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level": log_level,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
        "file": {
            "level": log_level,
            "formatter": "detailed", 
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "logs" / "app.log"),
            "mode": "a",
        },
    },
    "loggers": {
        "quantumvestai_ui": {
            "handlers": ["default", "file"],
            "level": log_level,
            "propagate": True
        },
    }
}

# Ensure logs directory exists
logs_dir = BASE_DIR / "logs"
logs_dir.mkdir(exist_ok=True)

dictConfig(log_config)
logger = logging.getLogger("quantumvestai_ui")

# Create FastAPI application for UI
app = FastAPI(
    title="QuantumVestAI UI",
    description="Enhanced Web UI for QuantumVestAI Platform with improved error handling and user experience",
    version="1.2.0"
)

# CORS origins configuration
origins = os.environ.get("CORS_ORIGINS", "*").split(",")

# Add enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Setup templates and store in app.state
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Get API URL from environment
API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_V1_URL = f"{API_URL}/api/v1"

# Enhanced template filters and utilities
def format_large_number(value):
    """Format large numbers with K, M, B suffixes"""
    if not isinstance(value, (int, float)):
        return str(value)
    
    if abs(value) >= 1000000000:
        return f"{value/1000000000:.1f}B"
    elif abs(value) >= 1000000:
        return f"{value/1000000:.1f}M"
    elif abs(value) >= 1000:
        return f"{value/1000:.1f}K"
    else:
        return str(value)

def get_asset_url(path, version=None):
    """Generate versioned asset URLs"""
    if not version:
        version = os.environ.get('APP_VERSION', 'v1.5.2')
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"/static/{path}?v={version}&t={timestamp}"

def format_currency(amount):
    """Format currency with proper formatting"""
    if isinstance(amount, (int, float)):
        return f"${amount:,.2f}"
    return str(amount)

def format_percentage(value):
    """Format percentage with proper sign"""
    if isinstance(value, (int, float)):
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2f}%"
    return str(value)

# Add enhanced filters to Jinja environment
templates.env.filters['get_asset_url'] = get_asset_url
templates.env.filters["format_large_number"] = format_large_number
templates.env.filters["format_currency"] = format_currency
templates.env.filters["format_percentage"] = format_percentage

# Add globals for template context
templates.env.globals["now"] = datetime.utcnow
templates.env.globals["API_URL"] = API_URL

logger.info("Enhanced template filters and globals added")

# Enhanced authentication utilities
class AuthUtils:
    @staticmethod
    def is_authenticated(request: Request) -> bool:
        """Check if user is authenticated via cookie or token"""
        auth_cookie = request.cookies.get("access_token")
        auth_header = request.headers.get("authorization")
        
        return bool(auth_cookie or auth_header)
    
    @staticmethod
    def get_user_info(request: Request) -> dict:
        """Get user information from request"""
        # Mock user info - in production, decode token
        if AuthUtils.is_authenticated(request):
            return {
                "username": "demo",
                "email": "demo@example.com",
                "role": "user",
                "is_authenticated": True
            }
        return {"is_authenticated": False}

# Enhanced request middleware with performance monitoring
@app.middleware("http")
async def enhanced_request_middleware(request: Request, call_next):
    start_time = datetime.now()
    path = request.url.path
    method = request.method
    
    # Generate request ID
    request_id = f"ui-{int(start_time.timestamp() * 1000)}"
    request.state.request_id = request_id
    
    logger.info(f"[{request_id}] {method} {path} started")
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Add performance headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(duration)
        
        logger.info(f"[{request_id}] {method} {path} completed - Status: {response.status_code} - Duration: {duration:.3f}s")
        
        return response
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"[{request_id}] {method} {path} failed - Duration: {duration:.3f}s - Error: {str(e)}")
        raise

# Enhanced route handlers with better error handling
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Enhanced index page with user context"""
    try:
        request_id = getattr(request.state, 'request_id', 'unknown')
        logger.info(f"[{request_id}] Rendering index page")
        
        # Check if user is authenticated
        user = AuthUtils.get_user_info(request)
        
        # If authenticated, redirect to dashboard
        if user.get("is_authenticated"):
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        return app.state.templates.TemplateResponse(
            "index.html", 
            {
                "request": request,
                "user": user,
                "api_url": API_URL,
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>QuantumVestAI - Error</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row justify-content-center">
                            <div class="col-md-6 text-center">
                                <h1 class="text-danger">Service Unavailable</h1>
                                <p class="lead">We're experiencing technical difficulties. Please try again later.</p>
                                <a href="/" class="btn btn-primary">Try Again</a>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """,
            status_code=500
        )

@app.get("/health")
async def enhanced_health_check():
    """Enhanced health check with API status"""
    api_health = {"status": "unknown"}
    
    try:
        response = requests.get(f"{API_V1_URL}/health", timeout=5)
        if response.status_code == 200:
            api_health = response.json()
    except Exception as e:
        logger.warning(f"Could not reach API for health check: {str(e)}")
        api_health = {"status": "unreachable", "error": str(e)}
    
    return {
        "ui": {
            "status": "healthy",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.2.0",
            "features": {
                "enhanced_error_handling": "enabled",
                "loading_states": "enabled",
                "responsive_design": "enabled",
                "accessibility": "enabled"
            }
        },
        "api": api_health
    }

# Enhanced error handlers
@app.exception_handler(404)
async def enhanced_not_found_handler(request: Request, exc: HTTPException):
    """Enhanced 404 error handler"""
    try:
        return app.state.templates.TemplateResponse(
            "errors/404.html", 
            {
                "request": request, 
                "path": request.url.path,
                "api_url": API_URL
            },
            status_code=404
        )
    except Exception as e:
        logger.error(f"Could not render 404 template: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Page Not Found - QuantumVestAI</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row justify-content-center">
                            <div class="col-md-6 text-center">
                                <h1 class="display-1">404</h1>
                                <h2>Page Not Found</h2>
                                <p>The page <code>{request.url.path}</code> was not found.</p>
                                <a href="/" class="btn btn-primary">Go Home</a>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """,
            status_code=404
        )

@app.exception_handler(500)
async def enhanced_server_error_handler(request: Request, exc: HTTPException):
    """Enhanced 500 error handler"""
    try:
        return app.state.templates.TemplateResponse(
            "errors/500.html", 
            {
                "request": request, 
                "error": str(exc),
                "api_url": API_URL
            },
            status_code=500
        )
    except:
        return HTMLResponse(
            content="""<!DOCTYPE html>
<html>
<head>
    <title>500 Server Error</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <h1 class="display-1">500</h1>
                <h2>Server Error</h2>
                <p>Something went wrong. Please try again later.</p>
                <a href="/" class="btn btn-primary">Go Home</a>
            </div>
        </div>
    </div>
</body>
</html>""",
            status_code=500
        )

# Import and register route modules
route_modules = []

# Try to import all route modules
try:
    from routes.auth import router as auth_router
    app.include_router(auth_router, tags=["auth"])
    route_modules.append("auth")
    logger.info("Registered auth routes")
except Exception as e:
    logger.error(f"Failed to import auth routes: {str(e)}")

try:
    from routes.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
    route_modules.append("dashboard")
    logger.info("Registered dashboard routes")
except Exception as e:
    logger.error(f"Failed to import dashboard routes: {str(e)}")

try:
    from routes.forecast import router as forecast_router
    app.include_router(forecast_router, tags=["forecast"])
    route_modules.append("forecast")
    logger.info("Registered forecast routes")
except Exception as e:
    logger.error(f"Failed to import forecast routes: {str(e)}")

try:
    from routes.market import router as market_router
    app.include_router(market_router, prefix="/market", tags=["market"])
    route_modules.append("market")
    logger.info("Registered market routes")
except Exception as e:
    logger.error(f"Failed to import market routes: {str(e)}")

try:
    from routes.watchlist import router as watchlist_router
    app.include_router(watchlist_router, prefix="/watchlist", tags=["watchlist"])
    route_modules.append("watchlist")
    logger.info("Registered watchlist routes")
except Exception as e:
    logger.error(f"Failed to import watchlist routes: {str(e)}")

try:
    from routes.predictability import router as predictability_router
    app.include_router(predictability_router, prefix="/predictability", tags=["predictability"])
    route_modules.append("predictability")
    logger.info("Registered predictability routes")
except Exception as e:
    logger.error(f"Failed to import predictability routes: {str(e)}")

try:
    from routes.settings import router as settings_router
    app.include_router(settings_router, prefix="/settings", tags=["settings"])
    route_modules.append("settings")
    logger.info("Registered settings routes")
except Exception as e:
    logger.error(f"Failed to import settings routes: {str(e)}")

try:
    from routes.api_proxy import router as api_proxy_router
    app.include_router(api_proxy_router, prefix="/api", tags=["api_proxy"])
    route_modules.append("api_proxy")
    logger.info("Registered api_proxy routes")
except Exception as e:
    logger.error(f"Failed to import api_proxy routes: {str(e)}")

try:
    from routes.utils import router as utils_router
    app.include_router(utils_router, prefix="/utils", tags=["utils"])
    route_modules.append("utils")
    logger.info("Registered utils routes")
except Exception as e:
    logger.error(f"Failed to import utils routes: {str(e)}")

try:
    from routes.admin import router as admin_router
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
    route_modules.append("admin")
    logger.info("Registered admin routes")
except Exception as e:
    logger.error(f"Failed to import admin routes: {str(e)}")

logger.info(f"Successfully registered route modules: {', '.join(route_modules)}")

@app.get("/debug-routes")
async def debug_routes():
    """Show all registered routes for debugging"""
    routes = []
    
    for route in app.routes:
        route_info = {
            "path": getattr(route, "path", None),
            "name": getattr(route, "name", None),
            "methods": list(route.methods) if hasattr(route, "methods") and route.methods else []
        }
        routes.append(route_info)
    
    return {
        "routes": routes,
        "route_modules": route_modules,
        "total_routes": len(routes)
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Enhanced QuantumVestAI UI")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 3000)), 
        reload=os.environ.get("DEBUG", "false").lower() == "true",
        log_level=log_level.lower()
    )