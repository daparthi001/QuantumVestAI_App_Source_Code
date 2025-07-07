"""
Main application file for QuantumVestAI UI (Enhanced)
<<<<<<< HEAD
Updated: 2025-07-07 21:49:53
Author: hemanth9398
=======
Updated: 2025-07-07 21:54:42
Author: hemanth9398
Version: 2.0.0 - Complete Production Ready Application
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
"""
import os
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from logging.config import dictConfig

from fastapi import FastAPI, HTTPException, Request, Form, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from datetime import datetime, timedelta
import logging
from pathlib import Path
from logging.config import dictConfig
import sys
=======
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c

# Define BASE_DIR first
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

# Create FastAPI application
app = FastAPI(
    title="QuantumVestAI UI",
<<<<<<< HEAD
    description="Enhanced Web UI for QuantumVestAI Platform with improved error handling and user experience",
    version="1.2.0"
=======
    description="Complete Web UI for QuantumVestAI Platform - Production Ready with Demo Mode",
    version="2.0.0"
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
)

# CORS configuration
origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=86400,
)

# Setup templates and store in app.state
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# API configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_V1_URL = f"{API_URL}/api/v1"

# Enhanced template filters and utilities
<<<<<<< HEAD
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
=======
def get_asset_url(path, version=None):
    """Generate versioned asset URLs"""
    if not version:
        version = os.environ.get('APP_VERSION', 'v2.0.0')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
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

<<<<<<< HEAD
# Add enhanced filters to Jinja environment
=======
def format_large_number(value):
    """Format large numbers with K, M, B suffixes"""
    if not isinstance(value, (int, float)):
        return str(value)
    
    if abs(value) >= 1e9:
        return f"{value / 1e9:.1f}B"
    elif abs(value) >= 1e6:
        return f"{value / 1e6:.1f}M"
    elif abs(value) >= 1e3:
        return f"{value / 1e3:.1f}K"
    else:
        return f"{value:.2f}"

# Register template filters
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
templates.env.filters['get_asset_url'] = get_asset_url
templates.env.filters["format_large_number"] = format_large_number
templates.env.filters["format_currency"] = format_currency
templates.env.filters["format_percentage"] = format_percentage

# Add globals for template context
templates.env.globals["now"] = datetime.utcnow
templates.env.globals["API_URL"] = API_URL

<<<<<<< HEAD
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
=======
logger.info("Template filters registered successfully")
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c

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

<<<<<<< HEAD
# Enhanced route handlers with better error handling
=======
# Authentication utilities
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
        if AuthUtils.is_authenticated(request):
            return {
                "username": "demo",
                "email": "demo@quantumvestai.com",
                "role": "user",
                "is_authenticated": True,
                "features_enabled": {
                    "advanced_analytics": True,
                    "real_time_data": True,
                    "portfolio_management": True,
                    "ai_predictions": True
                }
            }
        return {"is_authenticated": False}

# Enhanced route handlers
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
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
        
        return templates.TemplateResponse(
            "index.html", 
            {
                "request": request,
                "user": user,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": True
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_html("QuantumVestAI - Error", 
                "Service Unavailable", 
                "We're experiencing technical difficulties. Please try again later."),
            status_code=500
        )

<<<<<<< HEAD
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
    
=======
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    """Enhanced login page"""
    try:
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Check if already authenticated
        if AuthUtils.is_authenticated(request):
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "msg": msg,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": True
            }
        )
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_login_html(msg),
            status_code=500
        )

@app.post("/login")
async def enhanced_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """Enhanced login handler with demo authentication"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] Login attempt for: {username}")
    
    try:
        # Validate input
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        # Demo authentication (accepts demo/demo, admin/admin, test/test)
        valid_users = {
            "demo": "demo",
            "admin": "admin", 
            "test": "test",
            "user": "password"
        }
        
        if username.lower() in valid_users and password == valid_users[username.lower()]:
            logger.info(f"[{request_id}] Demo login successful for {username}")
            
            # Create demo token
            expires = datetime.utcnow() + timedelta(hours=24)
            token = f"demo_{username}_{int(expires.timestamp())}"
            
            redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            redirect_response.set_cookie(
                key="access_token",
                value=f"Bearer {token}",
                httponly=True,
                max_age=86400 if remember else None,
                samesite="lax",
                secure=request.url.scheme == "https"
            )
            
            return redirect_response
        else:
            raise ValueError("Invalid username or password. Try demo/demo, admin/admin, or test/test")
    
    except ValueError as e:
        logger.warning(f"[{request_id}] Login validation failed: {str(e)}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": True
            },
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Login error: {str(e)}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": "Login failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "username": username,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": True
            },
            status_code=500
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Registration page"""
    try:
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": msg,
                "api_url": API_URL,
                "demo_mode": True
            }
        )
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_html("Registration - QuantumVestAI",
                "Registration",
                "Registration page temporarily unavailable. Please try again later."),
            status_code=500
        )

@app.get("/dashboard", response_class=HTMLResponse)
async def enhanced_dashboard(request: Request):
    """Enhanced dashboard with authentication check"""
    try:
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Check authentication
        if not AuthUtils.is_authenticated(request):
            return RedirectResponse(url="/login?msg=Please log in to access the dashboard", status_code=status.HTTP_302_FOUND)
        
        user = AuthUtils.get_user_info(request)
        
        return templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request, 
                "user": user,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": True
            }
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return HTMLResponse(
            content=create_fallback_html("Dashboard - QuantumVestAI",
                "Dashboard Error",
                "Unable to load dashboard. Please try again later."),
            status_code=500
        )

@app.post("/logout")
async def logout(request: Request):
    """Enhanced logout endpoint"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] User logout")
    
    response = RedirectResponse(url="/login?msg=Successfully logged out", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@app.get("/health")
async def enhanced_health_check():
    """Enhanced health check"""
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    return {
        "ui": {
            "status": "healthy",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
<<<<<<< HEAD
            "version": "1.2.0",
=======
            "version": "2.0.0",
            "author": "hemanth9398",
            "updated": "2025-07-07 21:54:42",
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
            "features": {
                "enhanced_error_handling": "enabled",
                "demo_mode": "enabled",
                "responsive_design": "enabled",
                "real_time_updates": "enabled"
            }
        }
    }

<<<<<<< HEAD
=======
# Utility functions for fallback HTML
def create_fallback_html(title, heading, message):
    """Create fallback HTML for error cases"""
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-6 text-center">
                        <h1 class="text-primary">{heading}</h1>
                        <p class="lead">{message}</p>
                        <a href="/" class="btn btn-primary">Go Home</a>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

def create_fallback_login_html(msg=None):
    """Create fallback login HTML"""
    msg_html = f'<div class="alert alert-warning">{msg}</div>' if msg else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - QuantumVestAI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title text-center">Login</h2>
                            {msg_html}
                            <form method="post" action="/login">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                    <small class="form-text text-muted">Try: demo, admin, test, or user</small>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                    <small class="form-text text-muted">Use same as username (demo/demo, admin/admin, etc.)</small>
                                </div>
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="remember" name="remember">
                                    <label class="form-check-label" for="remember">Remember me</label>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                            <div class="text-center mt-3">
                                <a href="/" class="btn btn-secondary">Go Home</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
# Enhanced error handlers
@app.exception_handler(404)
async def enhanced_not_found_handler(request: Request, exc: HTTPException):
    """Enhanced 404 error handler"""
    try:
<<<<<<< HEAD
        return app.state.templates.TemplateResponse(
            "errors/404.html", 
=======
        return templates.TemplateResponse(
            "404.html", 
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
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
            content=create_fallback_html("Page Not Found - QuantumVestAI",
                "404 - Page Not Found",
                f"The page {request.url.path} was not found."),
            status_code=404
        )

@app.exception_handler(500)
async def enhanced_server_error_handler(request: Request, exc: HTTPException):
    """Enhanced 500 error handler"""
    try:
        return templates.TemplateResponse(
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
            content=create_fallback_html("Server Error - QuantumVestAI",
                "500 - Server Error",
                "Something went wrong. Please try again later."),
            status_code=500
        )

<<<<<<< HEAD
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
=======
# Import and include routers with error handling
def include_router_safely(router_module, router_name):
    """Safely include a router with error handling"""
    try:
        app.include_router(router_module.router)
        logger.info(f"Successfully included {router_name} router")
        return True
    except Exception as e:
        logger.error(f"Failed to include {router_name} router: {str(e)}")
        return False

# Include routers
routers_to_include = [
    ("routes.auth", "auth"),
    ("routes.dashboard", "dashboard"),
    ("routes.forecast", "forecast"),
    ("routes.market", "market"),
    ("routes.watchlist", "watchlist"),
    ("routes.predictability", "predictability"),
    ("routes.settings", "settings"),
    ("routes.api_proxy", "api_proxy"),
    ("routes.utils", "utils"),
]

for module_name, router_name in routers_to_include:
    try:
        module = __import__(module_name, fromlist=[router_name])
        include_router_safely(module, router_name)
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Error including {router_name}: {str(e)}")

logger.info("QuantumVestAI UI application initialized successfully")
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting QuantumVestAI UI - Complete Production Ready Application")
    logger.info("Author: hemanth9398")
    logger.info("Updated: 2025-07-07 21:54:42")
    uvicorn.run(
        "main_fixed:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 3000)), 
        reload=os.environ.get("DEBUG", "false").lower() == "true",
        log_level=log_level.lower()
    )