"""
Main application file for QuantumVestAI UI (Enhanced)
Updated: 2025-07-07 21:51:56
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
            "filename": "logs/app.log",
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
try:
    from utils import format_large_number
    logger.info("Imported format_large_number successfully")
except Exception as e:
    logger.error(f"Error importing format_large_number: {str(e)}")
    # Create fallback function
    def format_large_number(value):
        """Fallback format_large_number function"""
        if value is None:
            return "—"
        try:
            num_value = float(value)
            if abs(num_value) >= 1e9:
                return f"{num_value / 1e9:.1f}B"
            elif abs(num_value) >= 1e6:
                return f"{num_value / 1e6:.1f}M"
            elif abs(num_value) >= 1e3:
                return f"{num_value / 1e3:.1f}K"
            else:
                return str(num_value)
        except (ValueError, TypeError):
            return str(value)

# Create fallback functions for critical template filters
def get_asset_url(path, version=None):
    if not version:
        version = os.environ.get('APP_VERSION', 'v1.5.2')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"/static/{path}?v={version}&t={timestamp}"
    return f"/static/{path}?v={version}"

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

logger.info("Enhanced template filters added")

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
        
        # Use simple landing page for non-authenticated users
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>QuantumVestAI - AI-Powered Investment Platform</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <style>
                        .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; }
                        .feature-card { transition: transform 0.3s; }
                        .feature-card:hover { transform: translateY(-5px); }
                    </style>
                </head>
                <body>
                    <!-- Hero Section -->
                    <div class="hero-section text-center">
                        <div class="container">
                            <h1 class="display-4 fw-bold">QuantumVestAI</h1>
                            <p class="lead">AI-Powered Investment Intelligence Platform</p>
                            <p class="fs-5">Make smarter investment decisions with advanced AI forecasting</p>
                            <a href="/login" class="btn btn-light btn-lg mt-3">Get Started</a>
                        </div>
                    </div>
                    
                    <!-- Features Section -->
                    <div class="container my-5">
                        <div class="row text-center">
                            <div class="col-12">
                                <h2 class="mb-5">Powerful Features</h2>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-4 mb-4">
                                <div class="card feature-card h-100">
                                    <div class="card-body text-center">
                                        <div class="display-6 text-primary mb-3">🤖</div>
                                        <h5 class="card-title">AI Forecasting</h5>
                                        <p class="card-text">Advanced machine learning algorithms predict stock movements with high accuracy.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-4">
                                <div class="card feature-card h-100">
                                    <div class="card-body text-center">
                                        <div class="display-6 text-success mb-3">📊</div>
                                        <h5 class="card-title">Real-time Data</h5>
                                        <p class="card-text">Live market data and analytics to keep you informed of every market movement.</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 mb-4">
                                <div class="card feature-card h-100">
                                    <div class="card-body text-center">
                                        <div class="display-6 text-warning mb-3">⚡</div>
                                        <h5 class="card-title">Smart Alerts</h5>
                                        <p class="card-text">Get notified instantly when AI detects significant market opportunities.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Demo Section -->
                    <div class="bg-light py-5">
                        <div class="container text-center">
                            <h3>Try the Demo</h3>
                            <p class="lead">Experience QuantumVestAI with our demo account</p>
                            <p><strong>Demo Credentials:</strong></p>
                            <p>Username: <code>demo</code> | Password: <code>password</code></p>
                            <a href="/login" class="btn btn-primary btn-lg">Login to Demo</a>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <footer class="bg-dark text-white py-4">
                        <div class="container text-center">
                            <p>&copy; 2025 QuantumVestAI. Built by hemanth9398</p>
                            <p class="small">Updated: 2025-07-07 21:51:56 UTC</p>
                        </div>
                    </footer>
                    
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
                </body>
            </html>
            """,
            status_code=200
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
                                <a href="/login" class="btn btn-primary">Try Login</a>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """,
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
        
        return app.state.templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "msg": msg,
                "api_url": API_URL,
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        return HTMLResponse(
            content=f"""
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
                                    {f'<div class="alert alert-info">{msg}</div>' if msg else ''}
                                    <form method="post" action="/login">
                                        <div class="mb-3">
                                            <label for="username" class="form-label">Username</label>
                                            <input type="text" class="form-control" id="username" name="username" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="password" class="form-label">Password</label>
                                            <input type="password" class="form-control" id="password" name="password" required>
                                        </div>
                                        <div class="mb-3 form-check">
                                            <input type="checkbox" class="form-check-input" id="remember" name="remember">
                                            <label class="form-check-label" for="remember">Remember me</label>
                                        </div>
                                        <button type="submit" class="btn btn-primary w-100">Login</button>
                                    </form>
                                    <div class="mt-3 text-center">
                                        <p class="text-muted">Demo credentials: username: demo, password: password</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=200
        )

@app.post("/login")
async def enhanced_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """Enhanced login handler with improved error handling"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] Login attempt for: {username}")
    
    try:
        # Validate input
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not password or len(password) < 4:  # Relaxed for demo
            raise ValueError("Password must be at least 4 characters long")
        
        # Demo/fallback authentication (always works for demo)
        if username.lower() in ["demo", "test", "admin", "user"] and password in ["password", "demo", "test"]:
            logger.info(f"[{request_id}] Demo login successful for {username}")
            
            # Create demo token
            expires = datetime.utcnow() + timedelta(hours=24)
            token = f"demo_{username}_{int(expires.timestamp())}"
            
            redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            redirect_response.set_cookie(
                key="access_token",
                value=f"Bearer {token}",
                httponly=True,
                max_age=86400 if remember else None,  # 1 day or session
                samesite="lax",
                secure=request.url.scheme == "https"
            )
            
            return redirect_response
        else:
            raise ValueError("Invalid username or password. Try demo/password")
    
    except ValueError as e:
        logger.warning(f"[{request_id}] Login validation failed: {str(e)}")
        return RedirectResponse(url=f"/login?msg={str(e)}", status_code=status.HTTP_302_FOUND)
    
    except Exception as e:
        logger.error(f"[{request_id}] Login error: {str(e)}")
        return RedirectResponse(url="/login?msg=Login failed due to a technical error", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard", response_class=HTMLResponse)
async def enhanced_dashboard(request: Request):
    """Enhanced dashboard with authentication check"""
    try:
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Check authentication
        if not AuthUtils.is_authenticated(request):
            return RedirectResponse(url="/login?msg=Please log in to access the dashboard", status_code=status.HTTP_302_FOUND)
        
        user = AuthUtils.get_user_info(request)
        
        # Demo data for dashboard
        demo_data = {
            "portfolio_value": 150000.50,
            "daily_change": 2500.75,
            "daily_change_percent": 1.69,
            "total_stocks": 12,
            "watchlist_count": 8,
            "recent_trades": [
                {"symbol": "AAPL", "action": "BUY", "shares": 50, "price": 185.50, "time": "10:30 AM"},
                {"symbol": "MSFT", "action": "SELL", "shares": 25, "price": 365.25, "time": "09:15 AM"},
                {"symbol": "GOOGL", "action": "BUY", "shares": 10, "price": 2750.00, "time": "Yesterday"}
            ],
            "top_stocks": [
                {"symbol": "AAPL", "price": 185.50, "change": 2.25, "change_percent": 1.23},
                {"symbol": "MSFT", "price": 365.25, "change": -1.50, "change_percent": -0.41},
                {"symbol": "GOOGL", "price": 2750.00, "change": 15.75, "change_percent": 0.58}
            ]
        }
        
        return app.state.templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request, 
                "user": user,
                "api_url": API_URL,
                "request_id": request_id,
                "demo_data": demo_data
            }
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # Fallback dashboard HTML
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Dashboard - QuantumVestAI</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-5">
                        <div class="row">
                            <div class="col-12">
                                <h1>QuantumVestAI Dashboard</h1>
                                <div class="alert alert-success">
                                    <h4>Welcome to QuantumVestAI!</h4>
                                    <p>You have successfully logged in. The dashboard is loading...</p>
                                </div>
                                <div class="row">
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">Portfolio Value</h5>
                                                <h3 class="text-success">$150,000.50</h3>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">Daily Change</h5>
                                                <h3 class="text-success">+$2,500.75</h3>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">Total Stocks</h5>
                                                <h3>12</h3>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5 class="card-title">Watchlist</h5>
                                                <h3>8</h3>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-4">
                                    <a href="/forecast" class="btn btn-primary">Forecasts</a>
                                    <a href="/market" class="btn btn-secondary">Market Data</a>
                                    <a href="/watchlist" class="btn btn-info">Watchlist</a>
                                    <a href="/logout" class="btn btn-outline-danger">Logout</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """,
            status_code=200
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
            "author": "hemanth9398",
            "updated": "2025-07-07 21:51:56",
            "features": {
                "enhanced_error_handling": "enabled",
                "loading_states": "enabled",
                "responsive_design": "enabled",
                "accessibility": "enabled",
                "demo_mode": "enabled"
            }
        },
        "api": api_health
    }

# Enhanced logout
@app.post("/logout")
@app.get("/logout")
async def logout(request: Request):
    """Enhanced logout endpoint"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] User logout")
    
    response = RedirectResponse(url="/login?msg=Successfully logged out", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

# Enhanced error handlers
@app.exception_handler(404)
async def enhanced_not_found_handler(request: Request, exc: HTTPException):
    """Enhanced 404 error handler"""
    try:
        return app.state.templates.TemplateResponse(
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
            content="""
            <!DOCTYPE html>
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
            </html>
            """,
            status_code=500
        )

# Import and include route controllers with error handling
controllers = {}

# Try to import basic routes first (fallback)
try:
    import sys
    sys.path.append(str(BASE_DIR / "routes"))
    from basic_routes import router as basic_router
    app.include_router(basic_router)
    controllers["basic"] = True
    logger.info("Included basic router (forecast, market, watchlist)")
except Exception as e:
    logger.warning(f"Could not import basic router: {str(e)}")

# Try to import and include route controllers (skip if broken)
route_modules = [
    ("auth", "routes.auth"),
    # Skip broken ones for now
    # ("dashboard", "routes.dashboard"),
    # ("forecast", "routes.forecast"),
    # ("market", "routes.market"),
    # ("watchlist", "routes.watchlist"),
    # ("settings", "routes.settings"),
]

for name, module_path in route_modules:
    try:
        module = __import__(module_path, fromlist=["router"])
        if hasattr(module, 'router'):
            app.include_router(module.router)
            controllers[name] = module
            logger.info(f"Included {name} router from {module_path}")
    except Exception as e:
        logger.warning(f"Could not import {name} router from {module_path}: {str(e)}")

# Try to import API proxy (skip if broken)
# try:
#     from routes import api_proxy
#     if hasattr(api_proxy, 'router'):
#         app.include_router(api_proxy.router)
#         logger.info("Included API proxy router")
# except Exception as e:
#     logger.warning(f"Could not import api_proxy router: {str(e)}")

logger.info(f"Successfully imported {len(controllers)} route controllers")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Enhanced QuantumVestAI UI")
    logger.info(f"Author: hemanth9398, Updated: 2025-07-07 21:51:56")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 3000)), 
        reload=os.environ.get("DEBUG", "false").lower() == "true",
        log_level=log_level.lower()
    )