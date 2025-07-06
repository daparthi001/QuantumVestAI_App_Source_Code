"""
Authentication Routes for QuantumVestAI - Secured DB Version
Author: daparthi001
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
import os
import secrets
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db.models.user import User
from db.rds_session import get_db
from core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates_dir = Path(settings.TEMPLATES_DIR)
templates = Jinja2Templates(directory=templates_dir)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user(db, username)
    if not user:
        logger.warning("Failed login attempt: username not found")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning("Failed login attempt: wrong password")
        return None
    user.last_login = datetime.utcnow()
    db.commit()
    return user

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise credentials_exception
        user = get_user(db, username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/token")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    csrf_token = request.cookies.get("csrf_token")
    if not csrf_token or csrf_token != request.headers.get("X-CSRF-Token"):
        logger.warning("CSRF token validation failed")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token validation failed")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    user_agent = request.headers.get("User-Agent", "")
    access_token = create_access_token(data={"sub": user.username, "role": user.role, "fingerprint": {"user_agent_hash": pwd_context.hash(user_agent)[:16]}}, expires_delta=access_token_expires)
    logger.info("Token generated successfully")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), remember: bool = Form(False), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid username or password", "username": username}, status_code=status.HTTP_401_UNAUTHORIZED)
    access_token_expires = timedelta(days=7) if remember else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    user_agent = request.headers.get("User-Agent", "")
    client_ip = request.client.host if request.client else None
    access_token = create_access_token(data={"sub": user.username, "role": user.role, "fingerprint": {"user_agent_hash": pwd_context.hash(user_agent)[:16], "ip_prefix": client_ip.split(".")[0] if client_ip else None}}, expires_delta=access_token_expires)
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    csrf_token = secrets.token_urlsafe(32)
    max_age = 7 * 24 * 60 * 60 if remember else None
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True, max_age=max_age, samesite="strict", secure=request.url.scheme == "https")
    response.set_cookie("csrf_token", csrf_token, httponly=False, max_age=max_age, samesite="strict", secure=request.url.scheme == "https")
    logger.info("User successfully logged in")
    return response

@router.get("/logout")
@router.get("/auth/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    response.delete_cookie("csrf_token")
    return response

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Passwords don't match", "username": username, "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if len(password) < 8:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Password must be at least 8 characters long", "username": username, "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if password.lower() == username.lower() or password.lower() == email.lower():
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Password cannot be the same as your username or email", "username": username, "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Username already registered", "email": email}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password, created_at=datetime.utcnow(), role="user", status="active", disabled=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("New user registered successfully")
    return templates.TemplateResponse("login.html", {"request": request, "msg": "Registration successful! Please sign in with your new account."})

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
