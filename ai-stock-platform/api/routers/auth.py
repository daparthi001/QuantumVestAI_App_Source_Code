"""
Authentication Router
Created: 2025-05-20 04:43:53
Author: daparthi001
"""
from fastapi import APIRouter, Depends, Body, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from core.config import settings
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from core.exceptions import AuthenticationError, ValidationError
from api.db.session import get_db
from api.db.models.user import User
from api.schemas.auth import (
    TokenResponse,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    PasswordChangeRequest,
    PasswordResetRequest
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Unauthorized"}}
)

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Login endpoint for UI clients"
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> LoginResponse:
    """User login endpoint."""
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Verify credentials
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
    
    # Update last login
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account"
)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
) -> RegisterResponse:
    """Register a new user."""
    # Check existing username
    if db.query(User).filter(User.username == user_data.username).first():
        raise ValidationError("Username already registered")
    
    # Check existing email
    if db.query(User).filter(User.email == user_data.email).first():
        raise ValidationError("Email already registered")
    
    # Create user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role="free",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "success": True,
        "user_id": db_user.id,
        "created_at": db_user.created_at.isoformat()
    }

@router.post(
    "/password/change",
    summary="Change password",
    description="Change user password"
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise AuthenticationError("Current password is incorrect")
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True}

@router.post(
    "/password/reset/request",
    summary="Request password reset",
    description="Request a password reset token"
)
async def request_password_reset(
    email_data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """Request password reset."""
    user = db.query(User).filter(User.email == email_data.email).first()
    
    if not user:
        # Don't leak user existence
        return {"success": True}
    
    # Generate reset token
    import secrets
    reset_token = secrets.token_urlsafe(32)
    
    # Store token with expiry
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # TODO: Send reset email
    
    return {"success": True}

@router.post(
    "/logout",
    summary="User logout",
    description="Logout and clear session"
)
async def logout(response: Response) -> Dict[str, bool]:
    """Logout user."""
    response.delete_cookie(key="access_token")
    return {"success": True}