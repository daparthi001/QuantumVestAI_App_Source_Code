from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from api.core.config import settings
from api.core.security_utils import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)
from api.core.exceptions import AuthenticationError, ValidationError
from api.db.session import get_db
from api.db.models.user import User
from api.schemas.token import Token
from api.schemas.user import UserCreate, UserPrivate, UserPasswordUpdate

router = APIRouter(prefix="/auth")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationError("Incorrect username or password")
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Dict[str, Any])
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint for UI clients."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationError("Incorrect username or password")
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Set cookie for browser clients
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT != "development"
    )
    
    # Return token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserPrivate.from_orm(user).dict()
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise ValidationError("Username already registered")
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise ValidationError("Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role="free"  # Default role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"success": True, "user_id": db_user.id}

@router.post("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify JWT token and return user info."""
    return UserPrivate.from_orm(current_user).dict()

@router.post("/logout")
async def logout(response: Response):
    """Logout endpoint - clear cookie."""
    response.delete_cookie(key="access_token")
    return {"success": True}

@router.post("/password/change")
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user or not verify_password(password_data.current_password, user.hashed_password):
        raise AuthenticationError("Current password is incorrect")
    
    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"success": True}

@router.post("/password/reset/request")
async def request_password_reset(
    email: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Request password reset."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't leak information about user existence
        return {"success": True}
    
    # Generate reset token
    import uuid
    import secrets
    reset_token = f"{uuid.uuid4()}-{secrets.token_urlsafe(16)}"
    
    # Store token and expiry
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
    db.commit()
    
    # In a real implementation, send email with reset link
    # For now, just return success
    return {"success": True}

@router.post("/password/reset/verify")
async def verify_reset_token(
    token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Verify password reset token."""
    user = db.query(User).filter(
        User.password_reset_token == token,
        User.password_reset_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise ValidationError("Invalid or expired reset token")
    
    return {"success": True}

@router.post("/password/reset/complete")
async def complete_password_reset(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Complete password reset."""
    user = db.query(User).filter(
        User.password_reset_token == token,
        User.password_reset_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise ValidationError("Invalid or expired reset token")
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    
    return {"success": True}