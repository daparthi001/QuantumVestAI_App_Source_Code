"""
Main Application Entry Point
Created: 2025-06-17 00:07:14
Author: daparthi001
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Add API directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "api"))

# Import API and its components
from api.main import app as api_app
from core.config import settings
from core.logger import logger
from db.session import get_db
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
    return {
        "status": "healthy",
        "timestamp": "2025-06-17 00:07:14",
        "version": settings.VERSION
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)