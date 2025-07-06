"""
Fixed authentication routes with proper HTTPX error handling
Updated: 2025-07-06 19:11:39
Author: daparthi001
"""

from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.httpx_client import create_httpx_service
import secrets
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Base API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://quantumvestai-dev-api:8000/api/v1")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    """Display login page"""
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False)
):
    """Handle login form submission with improved HTTPX error handling"""
    try:
        # Create HTTPX service
        service = create_httpx_service(base_url=API_BASE_URL)
        
        # Prepare login payload
        payload = {"username": username, "password": password}
        
        # Make login request with proper error handling
        response = await service.post(
            "/login-ui",
            json_data=payload,
            timeout=15.0
        )
        
        if response.status_code != 200:
            logger.warning(f"Login failed for user {username}: {response.status_code}")
            error_msg = "Invalid username or password"
            
            # Try to get specific error message from response
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except:
                pass
            
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "msg": error_msg,
                    "username": username
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Parse response
        data = response.json()
        access_token = data.get("access_token")
        
        if not access_token:
            logger.error("No access token in login response")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "msg": "Invalid response from server"
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create successful response
        response_redirect = RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_302_FOUND
        )
        
        # Set cookies
        csrf_token = secrets.token_urlsafe(32)
        max_age = 7 * 24 * 60 * 60 if remember else None
        secure = request.url.scheme == "https"
        
        response_redirect.set_cookie(
            "access_token",
            f"Bearer {access_token}",
            httponly=True,
            max_age=max_age,
            samesite="strict",
            secure=secure
        )
        
        response_redirect.set_cookie(
            "csrf_token",
            csrf_token,
            httponly=False,
            max_age=max_age,
            samesite="strict",
            secure=secure
        )
        
        logger.info(f"Successful login for user {username}")
        return response_redirect
        
    except Exception as e:
        logger.error(f"Login error for user {username}: {str(e)}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "msg": "An error occurred during login. Please try again.",
                "username": username
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Handle registration with improved HTTPX error handling"""
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "msg": "Passwords don't match",
                "username": username,
                "email": email
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "msg": "Password must be at least 8 characters",
                "username": username,
                "email": email
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    try:
        # Create HTTPX service
        service = create_httpx_service(base_url=API_BASE_URL)
        
        # Prepare registration payload
        payload = {
            "username": username,
            "email": email,
            "password": password
        }
        
        # Make registration request
        response = await service.post(
            "/register-ui",
            json_data=payload,
            timeout=15.0
        )
        
        if response.status_code == 201:
            # Registration successful
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "msg": "Registration successful! Please log in.",
                    "username": username
                }
            )
        else:
            # Registration failed
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", "Registration failed")
            except:
                error_msg = "Registration failed"
            
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "msg": error_msg,
                    "username": username,
                    "email": email
                },
                status_code=response.status_code
            )
        
    except Exception as e:
        logger.error(f"Registration error for user {username}: {str(e)}")
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "msg": "An error occurred during registration. Please try again.",
                "username": username,
                "email": email
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    response.delete_cookie("csrf_token")
    return response