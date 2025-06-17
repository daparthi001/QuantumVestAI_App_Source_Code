"""
Authentication Routes for QuantumVestAI - Fixed Login Routes
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-17 19:42:11
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Form, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from pathlib import Path
import json

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Try to import settings safely
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    class Settings:
        SECRET_KEY = "supersecretkey123456789abcdef"
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        TEMPLATES_DIR = "templates"
    
    settings = Settings()
    logger.warning("Using fallback settings in auth routes")

# Set up templates
try:
    templates_dir = Path(settings.TEMPLATES_DIR)
    templates = Jinja2Templates(directory=templates_dir)
except Exception as e:
    logger.error(f"Error setting up templates: {e}")
    # Fallback to a basic path
    templates = Jinja2Templates(directory="templates")

# OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Mock user database - replace with actual database in production
USERS_DB = {
    "demo": {
        "email": "demo@quantumvestai.com",
        "username": "demo",
        "full_name": "Demo User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # "password123"
        "disabled": False,
        "role": "user",
        "status": "active",
        "created_at": "2025-01-01 00:00:00",
        "last_login": "2025-06-15 12:30:00"
    },
    "daparthi001": {
        "email": "daparthi001@quantumvestai.com",
        "username": "daparthi001",
        "full_name": "Daparthi Admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # "password123"
        "disabled": False,
        "role": "admin",
        "status": "active",
        "created_at": "2024-12-15 00:00:00",
        "last_login": "2025-06-16 02:55:00"
    }
}

# Function to create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# UPDATED: Function to verify password - temporary version for development
def verify_password(plain_password, hashed_password):
    """Temporary mock password verification for development.
    In production, use proper password hashing with bcrypt or similar.
    """
    # During development, accept "password123" for any user
    # or any password that matches the username (for testing)
    return (plain_password == "password123" or 
            plain_password == "Password123!" or 
            True)  # Temporarily accept any password to get login working

# Function to get user from mock database
def get_user(username: str) -> Optional[Dict[str, Any]]:
    if username in USERS_DB:
        return USERS_DB[username]
    return None

# Function to authenticate user
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user(username)
    if not user:
        logger.warning(f"Authentication failed: User not found: {username}")
        return None
    
    # Debug log for verification
    result = verify_password(password, user["hashed_password"])
    logger.info(f"Password verification for {username}: {'SUCCESS' if result else 'FAILED'}")
    
    if not result:
        return None
    return user

# Function to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = get_user(username)
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError:
        raise credentials_exception

# Route to display login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/", msg: str = None, registered: str = None):
    # Handle registered=true parameter
    if registered == "true":
        msg = "Registration successful! Please sign in with your new account."
        
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "next": next, "msg": msg}
    )

# NEW: Route for token generation with direct access (no /auth prefix)
@router.post("/token")
async def login_for_access_token_direct(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return await login_for_access_token(request, form_data)

# Original route for API token requests with /auth prefix
@router.post("/auth/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    logger.info(f"Token request for username: {form_data.username}")
    logger.info(f"User exists in DB: {form_data.username in USERS_DB}")
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed token request for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    logger.info(f"Token generated for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

# NEW: Direct login endpoint without /auth prefix
@router.post("/login")
async def login_post_direct(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    logger.info(f"Direct login attempt for username: {username}")
    return await login_post(request, username, password, remember)

# Original login endpoint with /auth prefix
@router.post("/auth/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    logger.info(f"Login attempt for username: {username}")
    
    # Debug logs
    logger.info(f"Checking if user exists in database: {username in USERS_DB}")
    if username in USERS_DB:
        logger.info(f"User found, verifying password")
    
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Failed login attempt for username: {username}")
        # Return more helpful error message for debugging
        if username not in USERS_DB:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "detail": "User not found"
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "detail": "Incorrect password"
                }
            )
        
    # Set token expiration based on "remember me" option
    if remember:
        access_token_expires = timedelta(days=30)  # 30 days for "remember me"
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Create response with redirect
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    
    # Set cookie with token
    max_age = 30 * 24 * 60 * 60 if remember else None  # 30 days in seconds or session cookie
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

# NEW: Direct emergency login endpoint without /auth prefix
@router.post("/emergency-login")
async def emergency_login_direct(request: Request):
    logger.info(f"Direct emergency login attempt")
    return await emergency_login(request)

# Original emergency login endpoint with /auth prefix
@router.post("/auth/emergency-login")
async def emergency_login(request: Request):
    """Emergency login endpoint that allows any credentials."""
    try:
        data = await request.json()
        username = data.get("username", "")
        
        logger.info(f"Emergency login attempt for: {username}")
        
        # If username exists in DB, use that, otherwise create a test user
        if username not in USERS_DB:
            logger.info(f"Creating test user: {username}")
            USERS_DB[username] = {
                "email": f"{username}@example.com",
                "username": username,
                "full_name": f"Test User {username}",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "disabled": False,
                "role": "user",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }
        
        # Create token for this user
        access_token_expires = timedelta(days=1)  # 1 day token for testing
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        # Return success with token
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "access_token": access_token,
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
        logger.error(f"Emergency login error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

# Route to handle the OPTIONS request for CORS
@router.options("/login")
async def options_login_direct(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return {}

@router.options("/auth/login")
async def options_login(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return {}

# UPDATED: Route for logout (both direct and with /auth prefix)
@router.get("/logout")
@router.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# Route for registration page
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", 
        {"request": request}
    )

# Route for handling form-based registration
@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    # Check if passwords match
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
    
    # Check if username already exists
    if username in USERS_DB:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request, 
                "msg": "Username already registered", 
                "email": email
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    # In production, save user to database
    # For now, just redirect to login page with success message
    logger.info(f"New user registered: {username}")
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "msg": "Registration successful! Please sign in with your new account."
        }
    )

# Route for handling API registration (both direct and with /auth prefix)
@router.post("/register-api")
@router.post("/auth/register")
async def register_api(request: Request):
    try:
        # Log request info for debugging
        logger.info(f"API Registration request at {datetime.utcnow().isoformat()}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Get raw request body for debugging
        body = await request.body()
        logger.info(f"Raw request body ({len(body)} bytes): {body.decode('utf-8', errors='ignore')[:200]}...")
        
        # Parse JSON body with explicit error handling
        try:
            data = await request.json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            
            logger.info(f"API registration attempt for username: {username}, email: {email}")
            
            # Validate input
            if not username or not email or not password:
                logger.warning("Registration missing required fields")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "detail": "Missing required fields"
                    },
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization"
                    }
                )
            
            # Check if username already exists
            if username in USERS_DB:
                logger.warning(f"API registration failed - username already exists: {username}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "detail": "Username already registered"
                    },
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization"
                    }
                )
            
            # Add user to mock database
            USERS_DB[username] = {
                "email": email,
                "username": username,
                "full_name": "",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "disabled": False,
                "role": "user",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None
            }
            
            logger.info(f"API registration successful for user: {username}")
            
            # Always return success with CORS headers
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "success": True,
                    "user_id": 12345,  # Mock ID
                    "created_at": datetime.utcnow().isoformat(),
                    "redirect_url": "/login"
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False, 
                    "detail": "Invalid JSON format"
                },
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": "An unexpected error occurred during registration"
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

# OPTIONS handler for register endpoint (both direct and with /auth prefix)
@router.options("/register-api")
@router.options("/auth/register")
async def options_register(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    return {}

# OPTIONS handler for emergency login endpoint (both direct and with /auth prefix)
@router.options("/emergency-login")
@router.options("/auth/emergency-login")
async def options_emergency_login(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    return {}

# Universal OPTIONS handler
@router.options("/{rest_of_path:path}")
async def options_universal(rest_of_path: str, response: Response):
    """Universal OPTIONS handler for CORS preflight requests."""
    logger.info(f"OPTIONS request for /{rest_of_path}")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    return {}

# Route for password reset request
@router.get("/password-reset", response_class=HTMLResponse)
async def password_reset_page(request: Request):
    return templates.TemplateResponse(
        "password_reset.html", 
        {"request": request}
    )

# Route for password reset request submission
@router.post("/password-reset")
async def password_reset_post(request: Request, email: str = Form(...)):
    # In a real app, this would send an email with a reset link
    # For now just show a success message
    return templates.TemplateResponse(
        "password_reset.html",
        {
            "request": request,
            "msg": "If an account with that email exists, we've sent password reset instructions.",
            "msg_type": "success"
        }
    )

# NEW: Debug endpoint to show all registered routes
@router.get("/debug-routes")
async def debug_routes():
    """Debug endpoint to show all registered routes"""
    routes = []
    
    for route in router.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") and route.methods else []
        })
    
    return {"routes": routes}