"""
Main Application Entry Point
Created: 2025-06-17 00:07:14
Updated: 2025-06-17 02:56:44
Author: daparthi001
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx
from datetime import datetime
from sqlalchemy import text

# Add API directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "api"))

# Import API and its components
from api.main import app as api_app
from core.config import settings
from core.logger import logger
from db.session import engine, get_db
from routers.auth import register as api_register

# Create frontend application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="QuantumVestAI Frontend",
)

# Mount the API app as a sub-application
app.mount("/api", api_app)

# Configure static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Get API base URL based on environment
def get_api_base_url():
    """Get the base URL for API calls based on environment"""
    # Default to same-process localhost
    api_host = getattr(settings, "API_HOST", "localhost")
    api_port = getattr(settings, "API_PORT", getattr(settings, "PORT", 8000))
    api_scheme = getattr(settings, "API_SCHEME", "http")
    
    return f"{api_scheme}://{api_host}:{api_port}"

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...)
):
    """Process registration form submission"""
    from schemas.auth import RegisterRequest
    
    # Create registration request
    register_data = RegisterRequest(
        username=username,
        email=email,
        password=password,
        full_name=full_name
    )
    
    try:
        # Get DB session
        db = next(get_db())
        
        # Call API register function
        result = await api_register(request, register_data, db)
        
        # Get next URL from query params or default to home
        next_url = request.query_params.get("next", "/")
        
        # Redirect to next URL or home
        return RedirectResponse(url=next_url, status_code=303)
    
    except Exception as e:
        # Log error
        logger.error(f"Registration failed: {str(e)}")
        
        # Return to registration page with error
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request,
                "error": str(e),
                "username": username,
                "email": email,
                "full_name": full_name
            },
            status_code=400
        )

# Add a simple proxy route for /auth/register
@app.post("/auth/register")
async def auth_register_proxy(request: Request):
    """Proxy to the API's /auth/register endpoint"""
    try:
        # Extract the request body
        body = await request.json()
        
        # Get API base URL
        api_base = get_api_base_url()
        api_url = f"{api_base}/api/auth/register"
        
        # Log the proxy attempt
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{now}] Proxying /auth/register request to {api_url}")
        
        # Forward to API endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url, 
                json=body,
                headers={k: v for k, v in request.headers.items() 
                        if k.lower() not in ["host", "content-length"]},
                timeout=10.0  # Add timeout for better error handling
            )
            
            # Log the proxy result
            logger.info(f"Proxied /auth/register request - Status: {response.status_code}")
            
            # Return the API response directly
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except httpx.TimeoutException:
        logger.error(f"Timeout while proxying to /auth/register")
        raise HTTPException(status_code=504, detail="Request to authentication service timed out")
    except httpx.HTTPError as e:
        logger.error(f"HTTP error while proxying to /auth/register: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Error communicating with authentication service")
    except Exception as e:
        logger.error(f"Proxy to /auth/register failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration proxy failed")

@app.get("/auth/register")
async def auth_register_get_proxy(request: Request):
    """Handle GET requests to /auth/register by redirecting to /register"""
    return RedirectResponse(url="/register")

@app.get("/signup")
async def signup_redirect(request: Request):
    """Redirect signup to register"""
    next_param = f"?next={request.query_params.get('next')}" if "next" in request.query_params else ""
    return RedirectResponse(url=f"/register{next_param}")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_data = {
        "ui": {
            "status": "healthy",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        },
        "api": {
            "status": "healthy",
            "database": {
                "status": "connected"
            },
            "environment": settings.ENVIRONMENT
        }
    }
    
    # Check database connection
    try:
        # Use text() to explicitly wrap the SQL query as required in the error message
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # No exception means database is connected
    except Exception as e:
        health_data["api"]["status"] = "unhealthy"
        health_data["api"]["database"]["status"] = "disconnected"
        health_data["api"]["database"]["error"] = str(e)
    
    # Return health status
    return health_data

# Add startup event to verify database connection
@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup"""
    try:
        # Test database connection with properly wrapped SQL query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        # Don't raise exception here to allow app to start even with DB issues

# Log application startup complete
logger.info(
    "API startup complete - %s v%s",
    settings.PROJECT_NAME,
    settings.VERSION
)

if __name__ == "__main__":
    # Use the PORT from settings
    port = getattr(settings, "PORT", 8000)
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)