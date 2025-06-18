"""
Authentication Routes for QuantumVestAI - Secured Version
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-18 13:59:24
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
import os
import secrets
from passlib.context import CryptContext

# Configure logging with proper formatting
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Create router
router = APIRouter()

# Set up password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Try to import settings safely
try:
    from core.config import settings
except ImportError:
    # Fallback settings with secure defaults
    class Settings:
        # Use environment variables with secure defaults
        SECRET_KEY = os.environ.get(
            "SECRET_KEY", 
            secrets.token_urlsafe(32)  # Generate random secure key if not provided
        )
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        TEMPLATES_DIR = "templates"
    
    settings = Settings()
    logger.warning("Using fallback settings in auth routes - Please set up proper environment variables")

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

# Mock user database - use an actual database in production
# Using a separate database definition
USERS_DB = {
    "demo": {
        "email": "demo@quantumvestai.com",
        "username": "demo",
        "full_name": "Demo User",
        "hashed_password": pwd_context.hash("SecurePassword123!"),  # Properly hashed
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
        "hashed_password": pwd_context.hash("StrongAdminPass456!"),  # Properly hashed
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
    
    # Add fingerprint data for improved security    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # Issued at time
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# Function to verify password using bcrypt
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed version using secure bcrypt verification"""
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash password 
def get_password_hash(password: str) -> str:
    """Generate bcrypt hash from password"""
    return pwd_context.hash(password)

# Function to get user from database
def get_user(username: str) -> Optional[Dict[str, Any]]:
    if username in USERS_DB:
        return USERS_DB[username]
    return None

# Function to authenticate user with rate limiting
# In production, implement proper rate limiting
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user(username)
    if not user:
        # Log attempt but don't reveal if username exists or not
        logger.warning(f"Failed login attempt with non-existent username")
        return None
    
    # Verify password securely
    if not verify_password(password, user["hashed_password"]):
        logger.warning(f"Failed password verification")
        return None
        
    # Update last login time
    user["last_login"] = datetime.utcnow().isoformat()
    return user

# Function to get current user from token with improved security
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise credentials_exception
            
        user = get_user(username)
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception

# Function to get current active user
async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

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

# Route for token generation
@router.post("/token")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Don't log usernames in production for security
    logger.info(f"Token request received")
    
    # Add CSRF protection
    csrf_token = request.cookies.get("csrf_token")
    if not csrf_token or csrf_token != request.headers.get("X-CSRF-Token"):
        logger.warning("CSRF token validation failed")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token validation failed"
        )
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        # Don't reveal specific authentication failure reasons
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include user fingerprint data for improved security
    user_agent = request.headers.get("User-Agent", "")
    
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "fingerprint": {
                "user_agent_hash": pwd_context.hash(user_agent)[:16]  # Store partial hash only
            }
        }, 
        expires_delta=access_token_expires
    )
    
    logger.info(f"Token generated successfully")
    return {"access_token": access_token, "token_type": "bearer"}

# Login endpoint
@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    logger.info("Login attempt received")
    
    user = authenticate_user(username, password)
    if not user:
        # Return generic error without revealing specific reason
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "msg": "Invalid username or password", 
                "username": username
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
        
    # Set token expiration based on "remember me" option
    if remember:
        access_token_expires = timedelta(days=7)  # 7 days max for "remember me"
    else:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include user IP and other fingerprint data for improved security
    user_agent = request.headers.get("User-Agent", "")
    client_ip = request.client.host if request.client else None
    
    access_token = create_access_token(
        data={
            "sub": user["username"],
            "role": user["role"],
            "fingerprint": {
                "user_agent_hash": pwd_context.hash(user_agent)[:16],
                "ip_prefix": client_ip.split(".")[0] if client_ip else None
            }
        }, 
        expires_delta=access_token_expires
    )
    
    # Create response with redirect
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    
    # Generate CSRF token for future requests
    csrf_token = secrets.token_urlsafe(32)
    
    # Set cookies with secure attributes
    max_age = 7 * 24 * 60 * 60 if remember else None  # 7 days in seconds or session cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=max_age,
        samesite="strict",  # Stricter CSRF protection than "lax"
        secure=request.url.scheme == "https"
    )
    
    # Set CSRF token cookie
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # Accessible from JavaScript
        max_age=max_age,
        samesite="strict",
        secure=request.url.scheme == "https"
    )
    
    logger.info(f"User successfully logged in")
    return response

# UPDATED: Route for logout (both direct and with /auth prefix)
@router.get("/logout")
@router.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    return response

# Route for registration page
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html", 
        {"request": request}
    )

# Route for handling form-based registration with improved security
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
    
    # Validate password strength
    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request, 
                "msg": "Password must be at least 8 characters long", 
                "username": username,
                "email": email
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        
    # Check for common password patterns
    if password.lower() == username.lower() or password.lower() == email.lower():
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request, 
                "msg": "Password cannot be the same as your username or email", 
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
    
    # Hash the password securely
    hashed_password = get_password_hash(password)
    
    # In production, save user to database
    # For now, add to mock database
    USERS_DB[username] = {
        "email": email,
        "username": username,
        "full_name": "",
        "hashed_password": hashed_password,
        "disabled": False,
        "role": "user",
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "last_login": None
    }
    
    logger.info(f"New user registered successfully")
    
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "msg": "Registration successful! Please sign in with your new account."
        }
    )

# Route for API registration with improved security
@router.post("/register-api")
async def register_api(request: Request):
    try:
        # Check for CSRF token in API requests
        csrf_token = request.cookies.get("csrf_token")
        if request.headers.get("X-CSRF-Token") != csrf_token:
            logger.warning("Missing or invalid CSRF token in API request")
        
        # Parse JSON body with explicit error handling
        try:
            data = await request.json()
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            
            # Validate input
            if not username or not email or not password:
                logger.warning("Registration missing required fields")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "detail": "Missing required fields"
                    }
                )
            
            # Check if username already exists
            if username in USERS_DB:
                logger.warning("Username already exists")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "detail": "Username already registered"
                    }
                )
            
            # Validate password strength
            if len(password) < 8:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "detail": "Password must be at least 8 characters long"
                    }
                )
            
            # Hash the password
            hashed_password = get_password_hash(password)
            
            # Add user to mock database
            USERS_DB[username] = {
                "email": email,
                "username": username,
                "full_name": "",
                "hashed_password": hashed_password,
                "disabled": False,
                "role": "user",
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None
            }
            
            logger.info(f"API registration successful")
            
            # Return success
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "success": True,
                    "user_id": secrets.token_hex(4),  # Random ID
                    "created_at": datetime.utcnow().isoformat(),
                    "redirect_url": "/login"
                }
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False, 
                    "detail": "Invalid JSON format"
                }
            )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "detail": "An unexpected error occurred during registration"
            }
        )

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
    # In production, implement proper email-based password reset
    # For now just show a success message without revealing if the email exists
    logger.info(f"Password reset requested")
    return templates.TemplateResponse(
        "password_reset.html",
        {
            "request": request,
            "msg": "If an account with that email exists, we've sent password reset instructions.",
            "msg_type": "success"
        }
    )

# Debug endpoint - disable in production
if os.environ.get("ENVIRONMENT") != "production":
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