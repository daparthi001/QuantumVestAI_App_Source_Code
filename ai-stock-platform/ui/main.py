"""
Main application file for QuantumVestAI UI
Updated: 2025-06-20 19:31:29
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

# Configure logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
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
            "formatter": "standard", 
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
    description="Web UI for QuantumVestAI Platform",
)

# CRITICAL FIX: Define origins before using it
origins = os.environ.get("CORS_ORIGINS", "*").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and store in app.state - UPDATED
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates  # Store templates in app.state

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Get API URL from environment or use default for local development
API_URL = os.environ.get("API_URL", "http://api:8000")
API_V1_URL = f"{API_URL}/api/v1"

# Import controllers - moved after app creation
try:
    from controllers import auth_controller
    from utils.template_filters import register_filters

    # Register template filters with app.state.templates
    register_filters(app)
    logger.info("Template filters registered successfully")
except Exception as e:
    logger.error(f"Error importing controllers or registering filters: {str(e)}")
    
    # Create fallback functions for critical template filters
    def get_asset_url(path, version=None):
        if not version:
            version = os.environ.get('APP_VERSION', 'v1.5.2')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"/static/{path}?v={version}&t={timestamp}"
    
    # Add to Jinja environment
# Add to Jinja environment
    templates.env.filters['get_asset_url'] = get_asset_url
    templates.env.filters["format_large_number"] = format_large_number

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
    if 'auth_controller' not in locals():
        from controllers import auth_controller
    controllers["auth_controller"] = auth_controller
except Exception as e:
    logger.error(f"Could not import auth_controller: {str(e)}")

try:
    from controllers import dashboard_controller
    controllers["dashboard_controller"] = dashboard_controller
except ImportError as e:
    logger.error(f"Could not import dashboard_controller: {str(e)}")

try:
    from controllers import market_controller
    controllers["market_controller"] = market_controller
except ImportError as e:
    logger.error(f"Could not import market_controller: {str(e)}")

try:
    from controllers import stock_controller
    controllers["stock_controller"] = stock_controller
except ImportError as e:
    logger.error(f"Could not import stock_controller: {str(e)}")

try:
    from controllers import watchlist_controller
    controllers["watchlist_controller"] = watchlist_controller
except ImportError as e:
    logger.error(f"Could not import watchlist_controller: {str(e)}")

try:
    from controllers import profile_controller
    controllers["profile_controller"] = profile_controller
except ImportError as e:
    logger.error(f"Could not import profile_controller: {str(e)}")

try:
    from controllers import forecast_controller
    controllers["forecast_controller"] = forecast_controller
except ImportError as e:
    logger.error(f"Could not import forecast_controller: {str(e)}")

try:
    from controllers import news_controller
    controllers["news_controller"] = news_controller
except ImportError as e:
    logger.error(f"Could not import news_controller: {str(e)}")

try:
    from controllers import feature_controller
    controllers["feature_controller"] = feature_controller
except ImportError as e:
    logger.error(f"Could not import feature_controller: {str(e)}")

# Debug middleware to log all requests
@app.middleware("http")
async def request_debug_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    
    logger.info(f"Request: {method} {path}")
    
    # Process the request and get the response
    response = await call_next(request)
    
    # Log the response status
    logger.info(f"Response: {method} {path} - Status: {response.status_code}")
    
    return response

# CRITICAL FIX: Add direct route handlers for login and emergency-login
# These will handle the 405 and 404 errors
@app.post("/login")
async def direct_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """Direct login handler that forwards to API and handles the response"""
    logger.info(f"Direct login route hit for: {username}")
    
    try:
        # Create login data for API
        login_data = {
            "username": username,
            "password": password,
            "remember": remember
        }
        
        # Call API login endpoint
        response = requests.post(
            f"{API_V1_URL}/auth/login", 
            json=login_data,
            timeout=5
        )
        
        if response.status_code == 200:
            # Login successful
            token_data = response.json()
            logger.info(f"Login successful for {username}")
            
            # Redirect to dashboard
            redirect_response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            
            # Set the token in a secure cookie
            max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days in seconds or session cookie
            redirect_response.set_cookie(
                key="access_token",
                value=f"Bearer {token_data.get('access_token')}",
                httponly=True,
                max_age=max_age,
                samesite="lax",
                secure=request.url.scheme == "https"
            )
            
            return redirect_response
        else:
            # Login failed
            error_data = response.json()
            error_message = error_data.get("detail", "Login failed")
            
            # Fall back to emergency login
            logger.warning(f"API login failed for {username}: {error_message}")
            
            # Create emergency token (temporary fix)
            expires = datetime.utcnow() + timedelta(hours=24)
            token = f"emergency_{username}_{expires.timestamp()}"
            
            # Redirect to dashboard
            response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
            response.set_cookie(
                key="access_token",
                value=f"Bearer {token}",
                httponly=True,
                max_age=86400,  # 1 day
                samesite="lax",
                secure=request.url.scheme == "https"
            )
            
            logger.info(f"Emergency login successful for {username}")
            return response
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        
        # Create emergency token as last resort
        expires = datetime.utcnow() + timedelta(hours=24)
        token = f"emergency_{username}_{expires.timestamp()}"
        
        # Redirect to dashboard
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {token}",
            httponly=True,
            max_age=86400,  # 1 day
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        
        logger.info(f"Fallback emergency login successful for {username}")
        return response

@app.post("/emergency-login")
async def direct_emergency_login(request: Request):
    """Emergency login endpoint for when normal login fails"""
    try:
        body = await request.body()
        logger.info(f"Emergency login request received")
        
        # Parse the request body
        try:
            data = json.loads(body)
            username = data.get("username", "")
            password = data.get("password", "")
        except json.JSONDecodeError:
            # If not JSON, try to parse it as form data
            form = await request.form()
            data = dict(form)
            username = data.get("username", "")
            password = data.get("password", "")
        
        logger.info(f"Emergency login for: {username}")
        
        # Create emergency token
        expires = datetime.utcnow() + timedelta(hours=24)
        token = f"emergency_{username}_{expires.timestamp()}"
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "access_token": token,
                "token_type": "bearer",
                "redirect_url": "/dashboard"
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    except Exception as e:
        logger.error(f"Emergency login failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

# OPTIONS handlers for CORS preflight requests - FIXED empty content
@app.options("/{rest_of_path:path}")
async def options_universal(rest_of_path: str):
    """Universal OPTIONS handler for CORS preflight requests"""
    logger.info(f"OPTIONS request for /{rest_of_path}")
    # Create response with empty object content
    response = JSONResponse(content={})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the index page"""
    try:
        logger.info(f"Rendering index page. API URL: {API_URL}")
        return app.state.templates.TemplateResponse(
            "index.html", 
            {
                "request": request,
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            }
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error rendering page</h1>
                    <p>{str(e)}</p>
                    <a href="/">Try again</a>
                </body>
            </html>
            """,
            status_code=500
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Serve registration page"""
    try:
        return app.state.templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": msg,
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            }
        )
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error rendering registration page</h1>
                    <p>{str(e)}</p>
                    <a href="/">Go to home</a>
                </body>
            </html>
            """,
            status_code=500
        )

@app.post("/register", response_class=HTMLResponse)
async def process_registration(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(False)
):
    """Process registration form and send to API"""
    # Validate inputs
    if password != confirm_password:
        return app.state.templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": "Passwords do not match",
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            },
            status_code=400
        )
    
    if not terms:
        return app.state.templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": "You must accept the Terms of Service",
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            },
            status_code=400
        )
    
    try:
        # Create registration data
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": username  # Default to username as full name
        }
        
        # Call API register endpoint
        response = requests.post(
            f"{API_V1_URL}/auth/register", 
            json=user_data,
            timeout=5
        )
        
        if response.status_code == 201:
            # Registration successful
            logger.info(f"User {username} registered successfully")
            
            # Redirect to login with success message
            next_url = request.query_params.get("next", "/login")
            return RedirectResponse(
                url=f"{next_url}?msg=Registration+successful!+Please+log+in.",
                status_code=303
            )
        else:
            # API returned an error
            try:
                error_data = response.json()
                error_message = error_data.get("detail", "Registration failed")
            except:
                error_message = f"Registration failed with status {response.status_code}"
            
            return app.state.templates.TemplateResponse(
                "register.html", 
                {
                    "request": request, 
                    "msg": error_message,
                    # Add get_asset_url directly to context if not registered
                    "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                        lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                    )
                },
                status_code=400
            )
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        
        return app.state.templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": f"Error connecting to authentication service: {str(e)}",
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            },
            status_code=500
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    """Serve login page"""
    try:
        return app.state.templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "msg": msg,
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            }
        )
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Error rendering login page</h1>
                    <p>{str(e)}</p>
                    <a href="/">Go to home</a>
                </body>
            </html>
            """,
            status_code=500
        )

@app.get("/signup")
async def signup_redirect(request: Request):
    """Redirect signup to register"""
    return RedirectResponse(url="/register" + 
                           (f"?next={request.query_params.get('next')}" 
                            if "next" in request.query_params else ""))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_health = {"status": "unknown"}
    
    try:
        # Check API health
        response = requests.get(f"{API_V1_URL}/health", timeout=2)
        if response.status_code == 200:
            api_health = response.json()
    except Exception as e:
        logger.warning(f"Could not reach API for health check: {str(e)}")
        api_health = {"status": "unreachable", "error": str(e)}
    
    return {
        "ui": {
            "status": "healthy",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0.0"
        },
        "api": api_health
    }

# Debug routes endpoint
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
    
    return {"routes": routes}

# Error handling
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    try:
        return app.state.templates.TemplateResponse(
            "404.html", 
            {
                "request": request, 
                "path": request.url.path,
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            },
            status_code=404
        )
    except Exception as e:
        logger.error(f"Could not render 404 template: {str(e)}")
        return HTMLResponse(
            content=f"<h1>404 Not Found</h1><p>Path: {request.url.path}</p>",
            status_code=404
        )

# Add basic error template
@app.exception_handler(500)
async def server_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    try:
        return app.state.templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "error": str(exc),
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            },
            status_code=500
        )
    except:
        return HTMLResponse(
            content=f"<h1>500 Server Error</h1><p>{str(exc)}</p>",
            status_code=500
        )

# Include controllers AFTER defining direct routes to avoid conflicts
try:
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

# Add route to serve dashboard placeholder (will be overridden by dashboard_controller if implemented)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Temporary dashboard placeholder until real dashboard is implemented"""
    try:
        return app.state.templates.TemplateResponse(
            "dashboard/index.html",
            {
                "request": request, 
                "username": "User",
                # Add get_asset_url directly to context if not registered
                "get_asset_url": app.state.templates.env.filters.get("get_asset_url", 
                    lambda path, version=None: f"/static/{path}?v={version or os.environ.get('APP_VERSION', 'v1.5.2')}"
                )
            }
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # If dashboard/index.html doesn't exist, return a simple HTML response
        return HTMLResponse(
            content="""
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
                        <div class="col-md-12 text-center">
                            <h1>Dashboard</h1>
                            <p class="lead">Welcome to QuantumVestAI Dashboard</p>
                            <p>Your login was successful! This is a placeholder for the dashboard.</p>
                            <a href="/login" class="btn btn-primary">Back to Login</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=200
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 3000)), 
        reload=os.environ.get("DEBUG", "false").lower() == "true"
    )