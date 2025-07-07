"""
<<<<<<< HEAD
Authentication routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Form, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import secrets
import os
import logging
import requests
from datetime import datetime, timedelta
=======
QuantumVestAI Authentication Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging
from datetime import datetime, timedelta
from pathlib import Path
import secrets
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c

# Setup router
router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# Create router
router = APIRouter()

# Setup templates - use relative path from project root
=======
# Templates setup
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Demo user database
DEMO_USERS = {
    "demo": {
        "username": "demo",
        "email": "demo@quantumvestai.com",
        "password": "demo",  # In production, this would be hashed
        "full_name": "Demo User",
        "role": "user",
        "created_at": "2025-01-01",
        "features": ["basic", "advanced", "premium"]
    },
    "admin": {
        "username": "admin", 
        "email": "admin@quantumvestai.com",
        "password": "admin",
        "full_name": "Admin User",
        "role": "admin",
        "created_at": "2025-01-01",
        "features": ["basic", "advanced", "premium", "admin"]
    },
    "test": {
        "username": "test",
        "email": "test@quantumvestai.com", 
        "password": "test",
        "full_name": "Test User",
        "role": "user",
        "created_at": "2025-01-01",
        "features": ["basic"]
    },
    "user": {
        "username": "user",
        "email": "user@quantumvestai.com",
        "password": "password",
        "full_name": "Regular User", 
        "role": "user",
        "created_at": "2025-01-01",
        "features": ["basic", "advanced"]
    }
}

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None, next: str = None):
    """Display login page"""
    try:
        # Check if already authenticated
        auth_cookie = request.cookies.get("access_token")
        if auth_cookie:
<<<<<<< HEAD
            logger.info("User already authenticated, redirecting to dashboard")
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        context = {
            "request": request,
            "msg": msg,
            "page_title": "Login - QuantumVestAI",
            "api_url": API_BASE_URL
        }
        
        return templates.TemplateResponse("login.html", context)
=======
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": msg,
                "next": next,
                "demo_mode": True,
                "demo_accounts": [
                    {"username": "demo", "password": "demo", "description": "Demo account with full features"},
                    {"username": "admin", "password": "admin", "description": "Admin account with all permissions"},
                    {"username": "test", "password": "test", "description": "Test account with basic features"},
                    {"username": "user", "password": "password", "description": "Regular user account"}
                ],
                "page_title": "Login - QuantumVestAI"
            }
        )
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        return HTMLResponse(
<<<<<<< HEAD
            content="""
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
=======
            content=create_fallback_login_html(msg),
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
            status_code=500
        )

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
    next: Optional[str] = Form(None)
):
<<<<<<< HEAD
    """Handle login form submission with comprehensive error handling"""
    logger.info(f"Login attempt for username: {username}")
    
    try:
        # Input validation
        if not username or len(username.strip()) < 3:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "msg": "Username must be at least 3 characters long",
                    "username": username,
                    "msg_type": "error"
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        if not password or len(password) < 6:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "msg": "Password must be at least 6 characters long",
                    "username": username,
                    "msg_type": "error"
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Prepare login payload
        payload = {
            "username": username.strip(),
            "password": password
        }
        
        # Try API login first
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token") or data.get("data", {}).get("access_token")
                
                if access_token:
                    logger.info(f"API login successful for {username}")
                    
                    # Create redirect response
                    redirect_response = RedirectResponse(
                        url="/dashboard",
                        status_code=status.HTTP_302_FOUND
                    )
                    
                    # Set secure cookies
                    max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days or session
                    secure = request.url.scheme == "https"
                    csrf_token = secrets.token_urlsafe(32)
                    
                    redirect_response.set_cookie(
                        "access_token",
                        f"Bearer {access_token}",
                        httponly=True,
                        max_age=max_age,
                        samesite="lax",
                        secure=secure
                    )
                    
                    redirect_response.set_cookie(
                        "csrf_token",
                        csrf_token,
                        httponly=False,
                        max_age=max_age,
                        samesite="lax",
                        secure=secure
                    )
                    
                    return redirect_response
                else:
                    logger.error("No access token in API response")
                    raise requests.RequestException("Invalid API response")
            else:
                logger.warning(f"API login failed with status {response.status_code}")
                # Try to get error message from API response
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Invalid username or password")
                except:
                    error_msg = "Invalid username or password"
                
                raise requests.RequestException(error_msg)
                
        except requests.RequestException as api_error:
            logger.warning(f"API login failed: {str(api_error)}, trying fallback authentication")
            
            # Fallback authentication for demo/testing
            demo_users = {
                "demo": "password",
                "test": "password", 
                "admin": "password",
                "user": "password"
            }
            
            if username.lower() in demo_users and password == demo_users[username.lower()]:
                logger.info(f"Fallback authentication successful for {username}")
                
                # Create emergency token
                expires = datetime.utcnow() + timedelta(hours=24)
                token = f"fallback_{username}_{int(expires.timestamp())}"
                
                redirect_response = RedirectResponse(
                    url="/dashboard",
                    status_code=status.HTTP_302_FOUND
                )
                
                redirect_response.set_cookie(
                    "access_token",
                    f"Bearer {token}",
                    httponly=True,
                    max_age=86400,  # 1 day for demo
                    samesite="lax",
                    secure=request.url.scheme == "https"
                )
                
                return redirect_response
            else:
                # Authentication failed
                error_msg = str(api_error) if "Invalid" in str(api_error) else "Invalid username or password"
                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "msg": error_msg,
                        "username": username,
                        "msg_type": "error"
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
=======
    """Handle login form submission"""
    try:
        logger.info(f"Login attempt for username: {username}")
        
        # Validate input
        if not username or len(username.strip()) < 2:
            raise ValueError("Username must be at least 2 characters long")
        
        if not password or len(password) < 3:
            raise ValueError("Password must be at least 3 characters long")
        
        username = username.strip().lower()
        
        # Check demo users
        if username in DEMO_USERS:
            user_data = DEMO_USERS[username]
            if user_data["password"] == password:
                logger.info(f"Demo login successful for {username}")
                
                # Create demo token
                expires = datetime.utcnow() + timedelta(hours=24)
                token = f"demo_{username}_{int(expires.timestamp())}"
                
                # Determine redirect URL
                redirect_url = next if next and next.startswith('/') else "/dashboard"
                
                response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
                
                # Set authentication cookie
                max_age = 7 * 24 * 60 * 60 if remember else None  # 7 days or session
                response.set_cookie(
                    key="access_token",
                    value=f"Bearer {token}",
                    httponly=True,
                    max_age=max_age,
                    samesite="lax",
                    secure=request.url.scheme == "https"
                )
                
                # Set user info cookie for quick access
                response.set_cookie(
                    key="user_info",
                    value=f"{username}|{user_data['role']}|{user_data['full_name']}",
                    max_age=max_age,
                    samesite="lax",
                    secure=request.url.scheme == "https"
                )
                
                return response
        
        # If we get here, authentication failed
        raise ValueError("Invalid username or password")
        
    except ValueError as e:
        logger.warning(f"Login validation failed: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "next": next,
                "demo_mode": True,
                "demo_accounts": [
                    {"username": "demo", "password": "demo", "description": "Demo account with full features"},
                    {"username": "admin", "password": "admin", "description": "Admin account with all permissions"},
                    {"username": "test", "password": "test", "description": "Test account with basic features"},
                    {"username": "user", "password": "password", "description": "Regular user account"}
                ],
                "page_title": "Login - QuantumVestAI"
            },
            status_code=400
        )
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
<<<<<<< HEAD
                "msg": "An error occurred during login. Please try again.",
                "username": username,
                "msg_type": "error"
=======
                "msg": "Login failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "username": username,
                "next": next,
                "demo_mode": True,
                "page_title": "Login - QuantumVestAI"
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
            },
            status_code=500
        )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Display registration page"""
    try:
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": msg,
                "demo_mode": True,
                "page_title": "Register - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_register_html(msg),
            status_code=500
        )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Display registration page"""
    try:
        # Check if already authenticated
        auth_cookie = request.cookies.get("access_token")
        if auth_cookie:
            logger.info("User already authenticated, redirecting to dashboard")
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        context = {
            "request": request,
            "msg": msg,
            "page_title": "Register - QuantumVestAI",
            "api_url": API_BASE_URL
        }
        
        return templates.TemplateResponse("register.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Register - QuantumVestAI</title>
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
                                    <h2 class="card-title text-center">Register</h2>
                                    <div class="alert alert-warning">
                                        Registration page temporarily unavailable. Please try again later.
                                    </div>
                                    <div class="text-center">
                                        <a href="/" class="btn btn-secondary">Go Home</a>
                                        <a href="/login" class="btn btn-primary">Login Instead</a>
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

@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
<<<<<<< HEAD
    terms: bool = Form(False)
):
    """Handle registration form submission with comprehensive validation"""
    logger.info(f"Registration attempt for username: {username}, email: {email}")
    
    try:
        # Input validation
        errors = []
        
        if not username or len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            errors.append("Please enter a valid email address")
        
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if not terms:
            errors.append("You must accept the terms and conditions")
        
        if errors:
            return templates.TemplateResponse(
                "register.html",
                {
                    "request": request,
                    "msg": "; ".join(errors),
                    "username": username,
                    "email": email,
                    "msg_type": "error"
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Prepare registration payload
        payload = {
            "username": username.strip(),
            "email": email.strip().lower(),
            "password": password
        }
        
        # Try API registration
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                logger.info(f"Registration successful for {username}")
                return templates.TemplateResponse(
                    "login.html",
                    {
                        "request": request,
                        "msg": "Registration successful! Please log in with your new account.",
                        "username": username,
                        "msg_type": "success"
                    }
                )
            else:
                # Registration failed
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Registration failed")
                except:
                    error_msg = "Registration failed"
                
                logger.warning(f"API registration failed for {username}: {error_msg}")
                
                return templates.TemplateResponse(
                    "register.html",
                    {
                        "request": request,
                        "msg": error_msg,
                        "username": username,
                        "email": email,
                        "msg_type": "error"
                    },
                    status_code=response.status_code
                )
        
        except requests.RequestException as e:
            logger.warning(f"API registration failed: {str(e)}, using demo registration")
            
            # For demo purposes, always succeed if API is down
            logger.info(f"Demo registration successful for {username}")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "msg": "Registration successful! Please log in with your new account. (Demo mode - API unavailable)",
                    "username": username,
                    "msg_type": "success"
                }
            )
=======
    full_name: str = Form(...)
):
    """Handle registration form submission (demo mode)"""
    try:
        logger.info(f"Registration attempt for username: {username}")
        
        # Validate input
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            raise ValueError("Please enter a valid email address")
        
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        if not full_name or len(full_name.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        
        username = username.strip().lower()
        
        # Check if user already exists
        if username in DEMO_USERS:
            raise ValueError("Username already exists. Please choose a different one.")
        
        # In demo mode, we'll just show success without actually creating the user
        logger.info(f"Demo registration successful for {username}")
        
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": "Registration successful! Please use one of the demo accounts to login (demo/demo, admin/admin, etc.)",
                "msg_type": "success",
                "demo_mode": True,
                "page_title": "Register - QuantumVestAI"
            }
        )
        
    except ValueError as e:
        logger.warning(f"Registration validation failed: {str(e)}")
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "email": email,
                "full_name": full_name,
                "demo_mode": True,
                "page_title": "Register - QuantumVestAI"
            },
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": "Registration failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "demo_mode": True,
                "page_title": "Register - QuantumVestAI"
            },
            status_code=500
        )

@router.post("/logout")
@router.get("/logout")
async def logout(request: Request):
    """Handle user logout"""
    try:
        logger.info("User logout")
        
        response = RedirectResponse(url="/auth/login?msg=Successfully logged out", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("access_token")
        response.delete_cookie("user_info")
        
        return response
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return RedirectResponse(url="/auth/login?msg=Please log in to view your profile", status_code=status.HTTP_302_FOUND)
        
        # Get user info from cookie (in production, decode JWT)
        user_cookie = request.cookies.get("user_info", "")
        if user_cookie:
            parts = user_cookie.split("|")
            if len(parts) >= 3:
                username, role, full_name = parts[0], parts[1], parts[2]
                user_data = DEMO_USERS.get(username, {})
                user_data.update({
                    "username": username,
                    "role": role,
                    "full_name": full_name
                })
            else:
                user_data = {"username": "demo", "role": "user", "full_name": "Demo User"}
        else:
            user_data = {"username": "demo", "role": "user", "full_name": "Demo User"}
        
        return templates.TemplateResponse(
            "auth/profile.html",
            {
                "request": request,
<<<<<<< HEAD
                "msg": "An error occurred during registration. Please try again.",
                "username": username,
                "email": email,
                "msg_type": "error"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/logout")
@router.post("/logout")
async def logout(request: Request):
    """Handle user logout"""
    logger.info("User logout")
    
    try:
        # Create response that redirects to login page
        response = RedirectResponse(
            url="/login?msg=You have been logged out successfully",
            status_code=status.HTTP_302_FOUND
        )
        
        # Clear authentication cookies
        response.delete_cookie("access_token")
        response.delete_cookie("csrf_token")
        
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if there's an error, redirect to login
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Display user profile page"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return RedirectResponse(
                url="/login?msg=Please log in to view your profile",
                status_code=status.HTTP_302_FOUND
            )
        
        # Mock user data for demo
        user_data = {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "full_name": "Demo User",
            "joined_date": "2025-01-01",
            "account_type": "Premium",
            "total_investments": "$125,000",
            "portfolio_value": "$142,500",
            "total_return": "+14.0%"
        }
        
        context = {
            "request": request,
            "user": user_data,
            "page_title": "Profile - QuantumVestAI"
        }
        
        return templates.TemplateResponse("profile.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering profile page: {str(e)}")
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Handle password change"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return RedirectResponse(
                url="/login?msg=Please log in to change your password",
                status_code=status.HTTP_302_FOUND
            )
        
        # Validate input
        if len(new_password) < 8:
            return templates.TemplateResponse(
                "profile.html",
                {
                    "request": request,
                    "msg": "New password must be at least 8 characters long",
                    "msg_type": "error"
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        if new_password != confirm_password:
            return templates.TemplateResponse(
                "profile.html",
                {
                    "request": request,
                    "msg": "New passwords do not match",
                    "msg_type": "error"
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # For demo purposes, always succeed
        logger.info("Password change successful (demo mode)")
        
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "msg": "Password changed successfully!",
                "msg_type": "success"
            }
        )
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "msg": "An error occurred while changing your password. Please try again.",
                "msg_type": "error"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
=======
                "user": user_data,
                "demo_mode": True,
                "page_title": "Profile - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading profile page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_profile_html(),
            status_code=500
        )

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request, msg: str = None):
    """Forgot password page"""
    try:
        return templates.TemplateResponse(
            "auth/forgot_password.html",
            {
                "request": request,
                "msg": msg,
                "demo_mode": True,
                "page_title": "Forgot Password - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering forgot password page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_forgot_password_html(),
            status_code=500
        )

@router.post("/forgot-password")
async def forgot_password_post(request: Request, email: str = Form(...)):
    """Handle forgot password form submission (demo mode)"""
    try:
        logger.info(f"Password reset request for email: {email}")
        
        if not email or "@" not in email:
            raise ValueError("Please enter a valid email address")
        
        # In demo mode, just show success message
        return templates.TemplateResponse(
            "auth/forgot_password.html",
            {
                "request": request,
                "msg": "Password reset instructions have been sent to your email (demo mode - no actual email sent)",
                "msg_type": "success",
                "demo_mode": True,
                "page_title": "Forgot Password - QuantumVestAI"
            }
        )
        
    except ValueError as e:
        return templates.TemplateResponse(
            "auth/forgot_password.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "email": email,
                "demo_mode": True,
                "page_title": "Forgot Password - QuantumVestAI"
            },
            status_code=400
        )

@router.get("/api/user")
async def get_current_user_api(request: Request):
    """API endpoint to get current user info"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return JSONResponse({
                "status": "error",
                "message": "Not authenticated"
            }, status_code=401)
        
        # Get user info from cookie
        user_cookie = request.cookies.get("user_info", "")
        if user_cookie:
            parts = user_cookie.split("|")
            if len(parts) >= 3:
                username, role, full_name = parts[0], parts[1], parts[2]
                user_data = DEMO_USERS.get(username, {})
                return JSONResponse({
                    "status": "success",
                    "user": {
                        "username": username,
                        "role": role,
                        "full_name": full_name,
                        "email": user_data.get("email", ""),
                        "features": user_data.get("features", []),
                        "is_authenticated": True
                    }
                })
        
        return JSONResponse({
            "status": "error",
            "message": "User data not found"
        }, status_code=404)
        
    except Exception as e:
        logger.error(f"Error getting user API: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

# Utility functions for fallback HTML
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
                            <h2 class="card-title text-center">Login to QuantumVestAI</h2>
                            {msg_html}
                            <form method="post" action="/auth/login">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                    <small class="form-text text-muted">Demo accounts: demo, admin, test, user</small>
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
                                <a href="/auth/forgot-password">Forgot Password?</a> |
                                <a href="/auth/register">Create Account</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def create_fallback_register_html(msg=None):
    """Create fallback register HTML"""
    msg_html = f'<div class="alert alert-warning">{msg}</div>' if msg else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - QuantumVestAI</title>
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
                            <h2 class="card-title text-center">Create Account</h2>
                            {msg_html}
                            <p class="text-center text-muted">Demo Mode - Use existing accounts to login</p>
                            <div class="text-center">
                                <a href="/auth/login" class="btn btn-primary">Back to Login</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def create_fallback_profile_html():
    """Create fallback profile HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile - QuantumVestAI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title">User Profile</h2>
                            <p>Profile page temporarily unavailable.</p>
                            <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def create_fallback_forgot_password_html():
    """Create fallback forgot password HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forgot Password - QuantumVestAI</title>
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
                            <h2 class="card-title text-center">Reset Password</h2>
                            <p class="text-center text-muted">Demo Mode - Use demo accounts to login</p>
                            <div class="text-center">
                                <a href="/auth/login" class="btn btn-primary">Back to Login</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
