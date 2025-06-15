import requests
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Response, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from config.settings import settings
# Change this import to the local namespace
# from core.config.constants import USER_ROLE_BASIC
from typing import Optional, Dict, Any
from services.api_client import APIClient

# Define USER_ROLE_BASIC constant if it doesn't exist in this context
USER_ROLE_BASIC = "basic"

# API base URL
API_BASE_URL = settings.API_BASE_URL

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["authentication"])

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# User dependency
async def get_current_user(request: Request) -> Optional[dict]:
    """Get the current authenticated user from the request"""
    token = request.cookies.get("token")
    if not token:
        return None
    
    try:
        # Verify token locally to avoid unnecessary API calls
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        
        expiration = payload.get("exp")
        if expiration and datetime.fromtimestamp(expiration) < datetime.utcnow():
            return None
        
        return {
            "username": username,
            "role": payload.get("role", USER_ROLE_BASIC),
            "exp": payload.get("exp")
        }
    except JWTError:
        return None

# Login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the login page"""
    # If user is already logged in, redirect to home
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    # Check if there's a next URL parameter for redirect after login
    next_url = request.query_params.get("next", "/")
    
    # Get any registration success message
    registered = request.query_params.get("registered", False)
    msg = "Registration successful! Please log in with your new account." if registered else None
    
    return templates.TemplateResponse(
        "login.html", 
        {
            "request": request, 
            "next": next_url,
            "msg": msg
        }
    )

# Login form handler
@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False)
):
    """Handle login form submission"""
    next_url = request.query_params.get("next", "/")
    
    # Call authentication API
    try:
        api_client = APIClient()
        auth_response = api_client.post(
            "/api/auth/login",
            data={"username": username, "password": password}
        )
        
        # Get token from response
        access_token = auth_response.get("access_token")
        
        # Set token expiration based on remember checkbox
        expiration = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        if remember:
            expiration = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60 * 24 * 7  # 7 days
        
        # Set cookie with token
        response = RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="token",
            value=access_token,
            httponly=True,
            max_age=expiration,
            expires=expiration,
            samesite="lax",
            secure=settings.ENVIRONMENT == "production"
        )
        
        return response
        
    except Exception as e:
        error_detail = "Invalid username or password"
        
        # Try to extract more detailed error message
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_detail = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "login.html", 
            {
                "request": request, 
                "msg": error_detail,
                "next": next_url
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )

# Registration page
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render the registration page"""
    # If user is already logged in, redirect to home
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse("register.html", {"request": request})

# Registration form handler
@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Handle registration form submission"""
    # Password validation
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "msg": "Passwords do not match"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Call registration API
    try:
        api_client = APIClient()
        api_client.post(
            "/api/auth/register",
            data={"username": username, "email": email, "password": password}
        )
        
        # Redirect to login with success message
        response = RedirectResponse(url="/login?registered=true", status_code=status.HTTP_303_SEE_OTHER)
        return response
        
    except Exception as e:
        error_detail = "Registration failed"
        
        # Try to extract more detailed error message
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_detail = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "msg": error_detail},
            status_code=status.HTTP_400_BAD_REQUEST
        )

# Profile page
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Render user profile page"""
    if not current_user:
        return RedirectResponse(url="/login?next=/profile", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Get user profile from API
        api_client = APIClient(token=request.cookies.get("token"))
        profile_data = api_client.get("/api/users/profile")
        
        # Get user activity
        activity_data = api_client.get("/api/users/activity")
        
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request, 
                "user": {**current_user, **profile_data},
                "activity": activity_data
            }
        )
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request, 
                "user": current_user, 
                "msg": f"Error loading profile: {error_message}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Account settings page
@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, current_user: dict = Depends(get_current_user)):
    """Render account settings page"""
    if not current_user:
        return RedirectResponse(url="/login?next=/settings", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse(
        "settings.html", 
        {"request": request, "user": current_user}
    )

# Update profile
@router.post("/profile/update", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
    full_name: str = Form(None),
    bio: str = Form(None),
    location: str = Form(None)
):
    """Update user profile"""
    if not current_user:
        return RedirectResponse(url="/login?next=/profile", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Update profile via API
        api_client = APIClient(token=request.cookies.get("token"))
        api_client.put(
            "/api/users/profile",
            data={
                "full_name": full_name,
                "bio": bio,
                "location": location
            }
        )
        
        # Redirect back to profile with success message
        response = RedirectResponse(url="/profile?updated=true", status_code=status.HTTP_303_SEE_OTHER)
        return response
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request, 
                "user": current_user, 
                "msg": f"Error updating profile: {error_message}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Change password
@router.post("/profile/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_user: dict = Depends(get_current_user),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password"""
    if not current_user:
        return RedirectResponse(url="/login?next=/profile", status_code=status.HTTP_303_SEE_OTHER)
    
    # Validate passwords
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request, 
                "user": current_user, 
                "msg": "New passwords do not match"
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Change password via API
        api_client = APIClient(token=request.cookies.get("token"))
        api_client.put(
            "/api/users/change-password",
            data={
                "current_password": current_password,
                "new_password": new_password
            }
        )
        
        # Redirect back to profile with success message
        response = RedirectResponse(url="/profile?password_changed=true", status_code=status.HTTP_303_SEE_OTHER)
        return response
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request, 
                "user": current_user, 
                "msg": f"Error changing password: {error_message}"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Logout endpoint
@router.get("/logout")
async def logout(response: Response, request: Request):
    """Log out the current user"""
    next_url = request.query_params.get("next", "/")
    response = RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="token")
    return response

# Password reset request page
@router.get("/password-reset", response_class=HTMLResponse)
async def password_reset_page(request: Request):
    """Render password reset request page"""
    return templates.TemplateResponse("password_reset.html", {"request": request})

# Password reset request handler
@router.post("/password-reset", response_class=HTMLResponse)
async def password_reset_request(
    request: Request,
    email: str = Form(...)
):
    """Handle password reset request submission"""
    try:
        # Send password reset request via API
        api_client = APIClient()
        api_client.post(
            "/api/auth/password-reset-request",
            data={"email": email}
        )
        
        # Show success message
        return templates.TemplateResponse(
            "password_reset_sent.html", 
            {"request": request, "email": email}
        )
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "password_reset.html", 
            {"request": request, "msg": error_message},
            status_code=status.HTTP_400_BAD_REQUEST
        )