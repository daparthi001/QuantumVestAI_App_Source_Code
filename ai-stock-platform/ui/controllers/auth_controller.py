"""
Authentication Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import requests
import logging
import json
from fastapi import APIRouter, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.auth_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/dashboard", msg: str = None):
    """Render login page"""
    return templates.TemplateResponse(
        "auth/login.html", 
        {"request": request, "next": next, "msg": msg}
    )

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """Process login form submission"""
    logger.info(f"Login attempt for username: {username}")
    
    try:
        # Call API login endpoint
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        
        if response.status_code != 200:
            error_msg = "Invalid username or password"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except:
                pass
                
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request, 
                    "msg": error_msg,
                    "username": username
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get token from response
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            logger.error(f"No access token in API response for user {username}")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request, 
                    "msg": "Authentication error: No token received",
                    "username": username
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create redirect response
        redirect_url = request.query_params.get("next", "/dashboard")
        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        
        # Set cookie with token
        max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days in seconds or session
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=max_age,
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        
        logger.info(f"User {username} successfully logged in")
        return response
        
    except requests.RequestException as e:
        logger.error(f"API connection error during login: {str(e)}")
        
        # Emergency login for development/testing when API is unavailable
        if username in ["demo", "daparthi001"] and password == "password123":
            logger.warning(f"Using emergency login for {username} due to API unavailability")
            
            # Create emergency token with username and timestamp
            timestamp = int(datetime.utcnow().timestamp())
            emergency_token = f"emergency_{username}_{timestamp}"
            
            # Create redirect response
            redirect_url = request.query_params.get("next", "/dashboard")
            response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
            
            # Set cookie with emergency token
            max_age = 30 * 24 * 60 * 60 if remember else None
            response.set_cookie(
                key="access_token",
                value=emergency_token,
                httponly=True,
                max_age=max_age,
                samesite="lax",
                secure=request.url.scheme == "https"
            )
            
            logger.info(f"Emergency login successful for {username}")
            return response
        
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request, 
                "msg": f"API connection error: {str(e)}",
                "username": username
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request, 
                "msg": f"An unexpected error occurred",
                "username": username
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/logout")
async def logout():
    """Handle user logout"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render registration page"""
    return templates.TemplateResponse(
        "auth/register.html", 
        {"request": request}
    )

@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Process registration form submission"""
    # Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request, 
                "msg": "Passwords don't match", 
                "username": username,
                "email": email
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    try:
        # Call API registration endpoint
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=5
        )
        
        # Check for API errors
        if response.status_code != 201:
            error_msg = "Registration failed"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except:
                pass
                
            return templates.TemplateResponse(
                "auth/register.html",
                {
                    "request": request, 
                    "msg": error_msg,
                    "username": username,
                    "email": email
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Registration successful, redirect to login
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": "Registration successful! Please sign in with your new account.",
                "username": username
            }
        )
        
    except requests.RequestException as e:
        logger.error(f"API connection error during registration: {str(e)}")
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request, 
                "msg": f"API connection error: {str(e)}",
                "username": username,
                "email": email
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request, 
                "msg": f"An unexpected error occurred",
                "username": username,
                "email": email
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/password-reset", response_class=HTMLResponse)
async def password_reset_page(request: Request):
    """Render password reset request page"""
    return templates.TemplateResponse(
        "auth/password_reset.html", 
        {"request": request}
    )

@router.post("/password-reset")
async def password_reset_post(request: Request, email: str = Form(...)):
    """Process password reset request"""
    try:
        # Call API password reset endpoint
        response = requests.post(
            f"{API_URL}/auth/password-reset",
            json={"email": email},
            timeout=5
        )
        
        # Always show success message for security (don't reveal if email exists)
        return templates.TemplateResponse(
            "auth/password_reset.html",
            {
                "request": request,
                "msg": "If an account with that email exists, we've sent password reset instructions.",
                "msg_type": "success"
            }
        )
        
    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        # Still show success message for security
        return templates.TemplateResponse(
            "auth/password_reset.html",
            {
                "request": request,
                "msg": "If an account with that email exists, we've sent password reset instructions.",
                "msg_type": "success"
            }
        )