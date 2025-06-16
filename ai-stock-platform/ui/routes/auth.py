"""
Authentication Routes
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 03:34:45 by daparthi001
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Form, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from pathlib import Path

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

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Set up templates
templates_dir = Path(settings.TEMPLATES_DIR)
templates = Jinja2Templates(directory=templates_dir)

# OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Mock user database - replace with actual database in production
USERS_DB = {
    "demo": {
        "email": "demo@quantumvestai.com",
        "username": "demo",
        "full_name": "Demo User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # "password123"
        "disabled": False,
        "role": "user",
        "status": "active"
    },
    "daparthi001": {
        "email": "daparthi001@quantumvestai.com",
        "username": "daparthi001",
        "full_name": "Daparthi Admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW", # "password123"
        "disabled": False,
        "role": "admin",
        "status": "active"
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

# Function to verify password - replace with proper password hashing in production
def verify_password(plain_password, hashed_password):
    # In production, use proper password verification like:
    # from passlib.context import CryptContext
    # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # return pwd_context.verify(plain_password, hashed_password)
    
    # This is just a mock for demonstration
    return plain_password == "password123" and hashed_password == "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

# Function to get user from mock database
def get_user(username: str) -> Optional[Dict[str, Any]]:
    if username in USERS_DB:
        return USERS_DB[username]
    return None

# Function to authenticate user
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

# Route to display login page
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "next": next}
    )

# Route to handle token requests for API authentication
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Route to handle form-based login
@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
    next: str = "/"
):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "msg": "Incorrect username or password", 
                "next": next
            },
            status_code=status.HTTP_401_UNAUTHORIZED
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
    response = RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
    
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
    
    return response

# Route for logout
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response