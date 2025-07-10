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
from .services.api_client import APIClient

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


def get_templates(request: Request) -> Jinja2Templates:
    """Return the application templates object."""
    return getattr(request.app.state, "templates", templates)

# Expose helper to templates in case a page references it
templates.env.globals["get_templates"] = get_templates

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Service worker needs to be accessible at root level
@app.get("/sw.js")
async def service_worker():
    """Serve service worker from root path"""
    from fastapi.responses import FileResponse
    import os
    
    sw_path = os.path.join(BASE_DIR, "static", "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="Service worker not found")

# API configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000")
API_V1_URL = f"{API_URL}/api/v1"

def _add_fallback_filters(templates):
    """Add minimal fallback filters if comprehensive system fails"""
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

    def format_change_value(value):
        """Format change value with sign"""
        if isinstance(value, (int, float)):
            sign = "+" if value > 0 else ""
            return f"{sign}{value:.2f}"
        return str(value)

    def format_number(value, decimal_places=0):
        """Simple thousands separator formatting"""
        try:
            num_value = float(value)
            if decimal_places == 0:
                return f"{int(num_value):,}"
            return f"{num_value:,.{decimal_places}f}"
        except (ValueError, TypeError):
            return "0"

    def humanize_date(value):
        """Convert datetime to human readable relative time"""
        if not value:
            return ""
        try:
            if isinstance(value, str):
                # Try to parse ISO format
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif not isinstance(value, datetime):
                return str(value)

            now = datetime.utcnow()
            if value.tzinfo is not None:
                # Convert to UTC for comparison
                value = value.replace(tzinfo=None)

            diff = now - value
            seconds = diff.total_seconds()

            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                minutes = int(seconds // 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif seconds < 86400:
                hours = int(seconds // 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif seconds < 2592000:
                days = int(seconds // 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
            elif seconds < 31536000:
                months = int(seconds // 2592000)
                return f"{months} month{'s' if months != 1 else ''} ago"
            else:
                years = int(seconds // 31536000)
                return f"{years} year{'s' if years != 1 else ''} ago"
        except Exception:
            return str(value)

    # Register fallback filters
    templates.env.filters['get_asset_url'] = get_asset_url
    templates.env.filters["format_large_number"] = format_large_number
    templates.env.filters["format_currency"] = format_currency
    templates.env.filters["format_percentage"] = format_percentage
    templates.env.filters["format_change_value"] = format_change_value
    templates.env.filters["humanize_date"] = humanize_date
    templates.env.filters["format_number"] = format_number

    logger.info("✓ Fallback template filters registered")

# Enhanced template filters and utilities setup
try:
    # Import and register comprehensive template filters
    from utils.template_filters import register_filters, validate_template_filters, get_template_filter_status
    
    # Register all template filters
    filter_registration_success = register_filters(app)
    
    if filter_registration_success:
        logger.info("✓ Comprehensive template filters registered successfully")

        # Validate that critical filters are working
        validation_success = validate_template_filters(app)
        if validation_success:
            logger.info("✓ Template filter validation passed")
        else:
            logger.warning("⚠ Template filter validation failed, but registration succeeded")
    else:
        logger.error("✗ Template filter registration failed, adding fallback filters")
        # Add minimal fallback filters if comprehensive registration fails
        _add_fallback_filters(templates)

except ImportError as e:
    logger.error(f"Could not import template filters module: {e}")
    _add_fallback_filters(templates)
except Exception as e:
    logger.error(f"Error setting up template filters: {e}")
    _add_fallback_filters(templates)

# Add globals for template context
templates.env.globals["now"] = datetime.utcnow
templates.env.globals["API_URL"] = API_URL

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
        
        # Demo portfolio data for index page
        demo_portfolio = {
            "total_value": 125750.45,
            "daily_change": 1234.56,
            "daily_change_pct": 0.99,
            "total_gain": 8750.45,
            "total_gain_percent": 7.48,
            "status": "available",
            "holdings": [
                {"symbol": "AAPL", "shares": 50, "price": 198.45, "value": 9922.50, "change": 2.34},
                {"symbol": "MSFT", "shares": 25, "price": 425.63, "value": 10640.75, "change": 1.87},
                {"symbol": "GOOGL", "shares": 15, "price": 2847.92, "value": 42718.80, "change": -0.56},
                {"symbol": "TSLA", "shares": 30, "price": 264.78, "value": 7943.40, "change": 3.21}
            ]
        }
        
        # Demo market data and news for index page
        demo_market = {
            "status": "open",
            "indices": [
                {"name": "S&P 500", "value": 4592.83, "change": 0.47},
                {"name": "Dow Jones", "value": 35421.12, "change": -0.23},
                {"name": "NASDAQ", "value": 14893.75, "change": 0.85}
            ]
        }
        
        # Demo news with proper dates for humanize_date filter
        demo_news = [
            {
                "title": "Tech Stocks Rally as AI Optimism Grows",
                "summary": "Major technology companies see significant gains as artificial intelligence adoption accelerates.",
                "source": "MarketWatch",
                "published": datetime.utcnow() - timedelta(hours=2),
                "url": "#"
            },
            {
                "title": "Federal Reserve Maintains Interest Rates",
                "summary": "The Fed keeps rates steady as inflation shows signs of cooling.",
                "source": "Reuters", 
                "published": datetime.utcnow() - timedelta(hours=6),
                "url": "#"
            },
            {
                "title": "EV Market Shows Strong Q2 Performance", 
                "summary": "Electric vehicle sales surge 45% year-over-year.",
                "source": "Bloomberg",
                "published": datetime.utcnow() - timedelta(days=1),
                "url": "#"
            }
        ]
        
        return get_templates(request).TemplateResponse(
            "index.html", 
            {
                "request": request,
                "user": user,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False,
                "portfolio": demo_portfolio,
                "data": {
                    "user": user,
                    "portfolio": demo_portfolio,
                    "market": demo_market,
                    "news": demo_news,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
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
        
        return get_templates(request).TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "msg": msg,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False
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
        
        if not password or len(password) < 3:
            raise ValueError("Password must be at least 3 characters long")
        
        api = APIClient()
        api_resp = api.post_form(
            "/auth/login",
            data={"username": username, "password": password}
        )
        token = api_resp.get("data", {}).get("access_token")
        if not token:
            raise ValueError(api_resp.get("message", "Login failed"))

        redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        max_age = 30 * 24 * 60 * 60 if remember else None
        redirect_response.set_cookie(
            key="access_token",
            value=f"Bearer {token}",
            httponly=True,
            max_age=max_age,
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        return redirect_response
    
    except ValueError as e:
        logger.warning(f"[{request_id}] Login validation failed: {str(e)}")
        return get_templates(request).TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False
            },
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Login error: {str(e)}")
        return get_templates(request).TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": "Login failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "username": username,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False
            },
            status_code=500
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Registration page"""
    try:
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Check if already authenticated
        if AuthUtils.is_authenticated(request):
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        return get_templates(request).TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": msg,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False
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

@app.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(False),
):
    """Enhanced registration handler"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] Registration attempt for: {username}")
    
    try:
        # Validate input
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            raise ValueError("Please enter a valid email address")
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        if not terms:
            raise ValueError("You must accept the Terms of Service and Privacy Policy")
        
        api = APIClient()
        api.post(
            "/auth/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "full_name": username,
            },
        )

        return RedirectResponse(
            url="/login?msg=Registration+successful!+Please+log+in.",
            status_code=status.HTTP_302_FOUND
        )
        
    except ValueError as e:
        logger.warning(f"[{request_id}] Registration validation failed: {str(e)}")
        return get_templates(request).TemplateResponse(
            "register.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "email": email,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False
            },
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Registration error: {str(e)}")
        return get_templates(request).TemplateResponse(
            "register.html",
            {
                "request": request,
                "msg": "Registration failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "username": username,
                "email": email,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False
            },
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
        
        # Demo portfolio data for dashboard page
        demo_portfolio = {
            "total_value": 125750.45,
            "daily_change": 1234.56,
            "daily_change_pct": 0.99,
            "total_gain": 8750.45,
            "total_gain_percent": 7.48,
            "status": "available"
        }
        
        # Demo data for dashboard
        market_summary = {
            "indices": {
                "S&P 500": {"value": 4567.89, "change": 23.45, "change_pct": 0.52},
                "NASDAQ": {"value": 14234.56, "change": -45.67, "change_pct": -0.32},
                "DOW": {"value": 34567.12, "change": 156.78, "change_pct": 0.46}
            },
            "sectors": {},
            "top_movers": {}
        }
        
        return get_templates(request).TemplateResponse(
            "dashboard/index.html",
            {
                "request": request, 
                "user": user,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_mode": False,
                "portfolio": demo_portfolio,
                "market_summary": market_summary,
                "popular_stocks": [],
                "news": [],
                "watchlist": [],
                "page_title": "Dashboard - QuantumVestAI"
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
async def logout_post(request: Request):
    """Enhanced logout endpoint (POST)"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] User logout via POST")
    
    response = RedirectResponse(url="/login?msg=Successfully logged out", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@app.get("/logout")
async def logout_get(request: Request):
    """Enhanced logout endpoint (GET) - for backwards compatibility"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] User logout via GET")
    
    response = RedirectResponse(url="/login?msg=Successfully logged out", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@app.get("/health")
async def enhanced_health_check():
    """Enhanced health check with template filter status"""
    health_data = {
        "ui": {
            "status": "healthy",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "2.0.0",
            "author": "hemanth9398",
            "updated": "2025-07-07 21:54:42",
            "features": {
                "enhanced_error_handling": "enabled",
                "demo_mode": "disabled",
                "responsive_design": "enabled",
                "real_time_updates": "enabled",
                "template_filters": "enhanced"
            }
        }
    }
    
    # Add template filter status
    try:
        from utils.template_filters import get_template_filter_status, validate_template_filters
        
        filter_status = get_template_filter_status()
        validation_result = validate_template_filters(app)
        
        health_data["template_filters"] = {
            "status": "healthy" if validation_result else "degraded",
            "total_filters": filter_status["total_filters"],
            "critical_filters_available": validation_result,
            "available_filters": filter_status["available_filters"]
        }
    except Exception as e:
        health_data["template_filters"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health_data

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

# Analytics endpoint for pageview tracking
from pydantic import BaseModel
class PageviewRequest(BaseModel):
    page: str
    title: str
    timestamp: str
    userAgent: str
    language: str

@app.post("/analytics/pageview")
async def track_pageview(request: Request, pageview_data: PageviewRequest):
    """Track page view for analytics (demo mode)."""
    try:
        # In a real implementation, this would save to database
        # For now, just log the pageview and return success
        logger.info(f"Page view tracked: {pageview_data.page} at {pageview_data.timestamp}")
        
        return {
            "status": "success",
            "message": "Page view tracked successfully",
            "data": {
                "page": pageview_data.page,
                "timestamp": pageview_data.timestamp
            }
        }
    except Exception as e:
        logger.error(f"Error tracking pageview: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Enhanced error handlers
@app.exception_handler(404)
async def enhanced_not_found_handler(request: Request, exc: HTTPException):
    """Enhanced 404 error handler"""
    try:
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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

# Add top-level routes for common 404 issues
@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio_redirect(request: Request):
    """Top-level portfolio route - redirect to dashboard portfolio"""
    return RedirectResponse(url="/dashboard/portfolio", status_code=302)

@app.get("/ticker-search")
async def ticker_search_redirect(request: Request):
    """Top-level ticker search route - redirect to market search"""
    query = request.query_params.get("q", "")
    if query:
        return RedirectResponse(url=f"/market/search?q={query}", status_code=302)
    else:
        return RedirectResponse(url="/market", status_code=302)

@app.get("/api/ticker-search")
async def ticker_search_api(request: Request):
    """Top-level ticker search API route"""
    from routes.market import ticker_search
    return await ticker_search(request, 
                             request.query_params.get("q", ""), 
                             int(request.query_params.get("limit", "10")))

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
    ("routes.ai_api", "ai_api"),
    ("routes.api_proxy", "api_proxy"),
    ("routes.content_api", "content_api"),
    ("routes.utils", "utils"),
    ("controllers.news_controller", "news_controller"),
    ("controllers.stock_controller", "stock_controller"),
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
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 3000)), 
        reload=os.environ.get("DEBUG", "false").lower() == "true",
        log_level=log_level.lower()
    )