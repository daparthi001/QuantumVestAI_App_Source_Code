"""
Main application file for QuantumVestAI UI (Enhanced)
Updated: 2025-06-20 19:31:29
Enhanced: 2025-01-09 (AI Assistant)
Author: daparthi001
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
from utils import format_large_number
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
    version="1.1.0"
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
    from controllers import auth_controller
    from utils.template_filters import register_filters

    register_filters(app)
    logger.info("Template filters registered successfully")
except Exception as e:
    logger.error(f"Error importing controllers or registering filters: {str(e)}")
    
    # Create enhanced fallback functions
    def get_asset_url(path, version=None):
        if not version:
            version = os.environ.get('APP_VERSION', 'v1.5.2')
# Import controllers - moved after app creation
# Create fallback functions for critical template filters
def get_asset_url(path, version=None):
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
    
    logger.info("Enhanced fallback template filters added")


# Enhanced request middleware with performance monitoring
    logger.info("Added fallback for get_asset_url filter")
    logger.info("Added fallback for format_large_number filter")


# Import proxy router - with error handling
# try:
#     from routes import api_proxy
# except ImportError as e:
#     logger.error(f"Could not import api_proxy: {str(e)}")
#     # Create dummy router as fallback
#     from fastapi import APIRouter
#     api_proxy = APIRouter()
#     app.include_router(api_proxy)

# Import controllers with error handling
controllers = {}
try:
    from controllers import auth_controller
    controllers['auth'] = auth_controller
except ImportError as e:
    logger.error(f"Could not import auth_controller: {str(e)}")

try:
    from controllers import dashboard_controller
    controllers['dashboard'] = dashboard_controller
except ImportError as e:
    logger.error(f"Could not import dashboard_controller: {str(e)}")

try:
    from controllers import market_controller
    controllers['market'] = market_controller
except ImportError as e:
    logger.error(f"Could not import market_controller: {str(e)}")

try:
    from controllers import stock_controller
    controllers['stock'] = stock_controller
except ImportError as e:
    logger.error(f"Could not import stock_controller: {str(e)}")

try:
    from controllers import watchlist_controller
    controllers['watchlist'] = watchlist_controller
except ImportError as e:
    logger.error(f"Could not import watchlist_controller: {str(e)}")

try:
    from controllers import profile_controller
    controllers['profile'] = profile_controller
except ImportError as e:
    logger.error(f"Could not import profile_controller: {str(e)}")

try:
    from controllers import forecast_controller
    controllers['forecast'] = forecast_controller
except ImportError as e:
    logger.error(f"Could not import forecast_controller: {str(e)}")

try:
    from controllers import news_controller
    controllers['news'] = news_controller
except ImportError as e:
    logger.error(f"Could not import news_controller: {str(e)}")

try:
    from controllers import feature_controller
    controllers['feature'] = feature_controller
except ImportError as e:
    logger.error(f"Could not import feature_controller: {str(e)}")

# Debug middleware to log all requests
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
        logger.error(f"[{request_id}] Error processing request {method} {path}: {str(e)}")
        logger.error(f"[{request_id}] Duration before error: {duration:.3f}s")
        # Re-raise to let error handlers handle it
        raise
@app.post("/emergency-login")
async def direct_emergency_login(request: Request):
    """Emergency login endpoint for when normal login fails"""
    try:
        # If not JSON, try to parse it as form data
        form = await request.form()
        data = dict(form)
        username = data.get("username", "")
        password = data.get("password", "")
        
        logger.info(f"Emergency login for: {username}")
        
        # Create emergency token
        expires = datetime.utcnow() + timedelta(hours=24)
        token = f"emergency_{username}_{expires.timestamp()}"
        
        # For now, just return a success response
        return JSONResponse({
            "success": True,
            "message": "Emergency login successful",
            "token": token
        })
        
    except Exception as e:
        logger.error(f"Emergency login error: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": "Emergency login failed"
        }, status_code=500)

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

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Serve registration page"""
        logger.error(f"Error rendering register page: {str(e)}")

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
                                        <div class="alert alert-warning">
                                            Login page temporarily unavailable. Please try again later.
                                        </div>
                                        <div class="text-center">
                                            <a href="/" class="btn btn-secondary">Go Home</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            """,
            status_code=500
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
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Create login data for API
        login_data = {
            "username": username.strip(),
            "password": password,
            "remember": remember
        }
        
        # Call API login endpoint with timeout
        try:
            response = requests.post(
                f"{API_V1_URL}/auth/login", 
                json=login_data,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )

                error_message = f"Registration failed with status {response.status_code}"

            
            if response.status_code == 200:
                token_data = response.json()
                logger.info(f"[{request_id}] API login successful for {username}")
                
                # Create redirect response
                redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
                
                # Set secure cookie
                max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days or session
                redirect_response.set_cookie(
                    key="access_token",
                    value=f"Bearer {token_data.get('data', {}).get('access_token', 'mock_token')}",
                    httponly=True,
                    max_age=max_age,
                    samesite="lax",
                    secure=request.url.scheme == "https"
                )
                
                return redirect_response
            else:
                # API login failed, try fallback
                logger.warning(f"[{request_id}] API login failed with status {response.status_code}")
                raise requests.RequestException("API login failed")
                
        except requests.RequestException as e:
            logger.warning(f"[{request_id}] API unavailable, using fallback authentication: {str(e)}")
            
            # Fallback authentication (demo purposes)
            if username.lower() in ["demo", "test", "admin"] and password == "password":
                logger.info(f"[{request_id}] Fallback login successful for {username}")
                
                # Create emergency token
                expires = datetime.utcnow() + timedelta(hours=24)
                token = f"fallback_{username}_{int(expires.timestamp())}"
                
                redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
                redirect_response.set_cookie(
                    key="access_token",
                    value=f"Bearer {token}",
                    httponly=True,
                    max_age=86400,  # 1 day
                    samesite="lax",
                    secure=request.url.scheme == "https"
                )
                
                return redirect_response
            else:
                raise ValueError("Invalid username or password")
    
    except ValueError as e:
        logger.warning(f"[{request_id}] Login validation failed: {str(e)}")
        return app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "api_url": API_URL,
                "request_id": request_id
            },
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"[{request_id}] Login error: {str(e)}")
        return app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": "Login failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "username": username,
                "api_url": API_URL,
                "request_id": request_id
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
        
        return app.state.templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request, 
                "user": user,
                "api_url": API_URL,
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # Fallback dashboard HTML

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    """Serve login page"""
        logger.error(f"Error rendering login page: {str(e)}")

        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <script src="/static/js/enhanced-ui.js"></script>
                <script src="/static/js/enhanced-dashboard.js"></script>
            </head>
            <body>
                <div class="container-fluid mt-4">
                    <div class="row">
                        <div class="col-12">
                            <h1>QuantumVestAI Dashboard</h1>
                            <p class="lead">Welcome! Your dashboard is loading...</p>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-body" id="marketOverview">
                                            <h5 class="card-title">Market Overview</h5>
                                            <p>Loading market data...</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-body" id="trendingStocks">
                                            <h5 class="card-title">Trending Stocks</h5>
                                            <p>Loading trending stocks...</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row mt-4">
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-body" id="watchlist">
                                            <h5 class="card-title">Watchlist</h5>
                                            <p>Loading watchlist...</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-body" id="portfolioSummary">
                                            <h5 class="card-title">Portfolio Summary</h5>
                                            <p>Loading portfolio...</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    window.API_BASE_URL = '/api/v1';
                    // Dashboard will auto-initialize
                </script>
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
            "version": "1.1.0",
            "features": {
                "enhanced_error_handling": "enabled",
                "loading_states": "enabled",
                "responsive_design": "enabled",
                "accessibility": "enabled"
            }
        },
        "api": api_health
    }

# Enhanced logout
@app.post("/logout")
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

async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""

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

# Include controllers AFTER defining direct routes to avoid conflicts
try:
    from routes import api_proxy
    app.include_router(api_proxy.router)
    logger.info("Included API proxy router")
except Exception as e:
    logger.error(f"Failed to include api_proxy router: {str(e)}")

# Only include controllers that were successfully imported
for name, controller in controllers.items():
    try:
        app.include_router(controller.router)
        logger.info(f"Included {name} router")
    except Exception as e:
        logger.error(f"Failed to include {name} router: {str(e)}")

# Include any existing controllers that work
controllers_imported = []
try:
    from controllers import auth_controller
    if hasattr(auth_controller, 'router'):
        app.include_router(auth_controller.router)
        controllers_imported.append("auth_controller")
except ImportError as e:
    logger.warning(f"Could not import auth_controller: {str(e)}")

try:
    from controllers import dashboard_controller
    if hasattr(dashboard_controller, 'router'):
        app.include_router(dashboard_controller.router)
        controllers_imported.append("dashboard_controller")
except ImportError as e:
    logger.warning(f"Could not import dashboard_controller: {str(e)}")

if controllers_imported:
    logger.info(f"Successfully imported controllers: {', '.join(controllers_imported)}")

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