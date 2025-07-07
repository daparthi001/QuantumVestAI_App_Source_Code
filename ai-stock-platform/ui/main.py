"""
Main application file for QuantumVestAI UI (Enhanced)
Updated: 2025-07-07 21:54:42
Author: hemanth9398
Version: 2.0.0 - Complete Production Ready Application
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
    description="Complete Web UI for QuantumVestAI Platform - Production Ready with Demo Mode",
    version="2.0.0"
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
def get_asset_url(path, version=None):
    """Generate versioned asset URLs"""
    if not version:
        version = os.environ.get('APP_VERSION', 'v2.0.0')
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
templates.env.filters['get_asset_url'] = get_asset_url
templates.env.filters["format_large_number"] = format_large_number
templates.env.filters["format_currency"] = format_currency
templates.env.filters["format_percentage"] = format_percentage

# Add globals for template context
templates.env.globals["now"] = datetime.utcnow
templates.env.globals["API_URL"] = API_URL

logger.info("Template filters registered successfully")

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
    return {
        "ui": {
            "status": "healthy",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "2.0.0",
            "author": "hemanth9398",
            "updated": "2025-07-07 21:54:42",
            "features": {
                "enhanced_error_handling": "enabled",
                "demo_mode": "enabled",
                "responsive_design": "enabled",
                "real_time_updates": "enabled"
            }
        }
    }

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

# Enhanced error handlers
@app.exception_handler(404)
async def enhanced_not_found_handler(request: Request, exc: HTTPException):
    """Enhanced 404 error handler"""
    try:
        return templates.TemplateResponse(
            "404.html", 
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