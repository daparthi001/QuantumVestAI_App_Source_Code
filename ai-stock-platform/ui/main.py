"""
UI Main Module
Created: 2025-06-17 01:50:11
Author: daparthi001
"""
import os
import requests
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_ui")

# Create FastAPI application for UI
app = FastAPI(
    title="QuantumVestAI UI",
    description="Web UI for QuantumVestAI Platform",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Get API URL from environment or use default for local development
API_URL = os.environ.get("API_URL", "http://api:8000/api/v1")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the index page"""
    try:
        logger.info(f"Rendering index page. API URL: {API_URL}")
        return templates.TemplateResponse(
            "index.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Serve registration page"""
    try:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "msg": msg}
        )
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
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
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": "Passwords do not match"
            },
            status_code=400
        )
    
    if not terms:
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": "You must accept the Terms of Service"
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
            f"{API_URL}/auth/register", 
            json=user_data
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
            error_data = response.json()
            error_message = error_data.get("detail", "Registration failed")
            
            return templates.TemplateResponse(
                "register.html", 
                {
                    "request": request, 
                    "msg": error_message
                },
                status_code=400
            )
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        
        return templates.TemplateResponse(
            "register.html", 
            {
                "request": request, 
                "msg": f"Error connecting to authentication service: {str(e)}"
            },
            status_code=500
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    """Serve login page"""
    try:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "msg": msg}
        )
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
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
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            api_health = response.json()
    except Exception as e:
        logger.warning(f"Could not reach API for health check: {str(e)}")
        api_health = {"status": "unreachable", "error": str(e)}
    
    return {
        "ui": {
            "status": "healthy",
            "timestamp": "2025-06-17 01:50:11"
        },
        "api": api_health
    }

# Error handling
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    try:
        return templates.TemplateResponse(
            "404.html", 
            {"request": request, "path": request.url.path},
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
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": str(exc)},
            status_code=500
        )
    except:
        return HTMLResponse(
            content=f"<h1>500 Server Error</h1><p>{str(exc)}</p>",
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)