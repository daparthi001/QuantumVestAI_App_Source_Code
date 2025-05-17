"""
Authentication router for user login, registration, and account management.
Created: 2025-05-17 14:29:46 UTC
Author: daparthi001
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from api.core.config import settings
from api.core.security import (
    create_access_token,
    get_password_hash,
    verify_password
)
from api.core.dependencies import get_db, get_current_user
from api.schemas.auth import (
    Token,
    LoginResponse,
    PasswordResetRequest,
    PasswordChangeRequest
)
from api.models.user import User
from api.core.exceptions import AuthenticationError
from api.services.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise AuthenticationError("Incorrect email or password")
    
    if not user.is_active:
        raise AuthenticationError("Account is inactive")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=LoginResponse)
async def register(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    user_in: UserCreate
) -> Any:
    """
    Register new user.
    """
    # Check if user exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send welcome email
    background_tasks.add_task(
        send_welcome_email,
        user.email,
        user.full_name
    )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/password-reset", response_model=dict)
async def request_password_reset(
    *,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
    request: PasswordResetRequest
) -> Any:
    """
    Request password reset.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        # Generate reset token
        reset_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(hours=1)
        )
        
        # Update user
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # Send reset email
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            reset_token
        )
    
    return {
        "message": "If an account exists with this email, a password reset link will be sent"
    }

@router.post("/password-change", response_model=dict)
async def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: PasswordChangeRequest
) -> Any:
    """
    Change user password.
    """
    if not verify_password(request.current_password, current_user.password_hash):
        raise AuthenticationError("Incorrect current password")
    
    # Update password
    current_user.password_hash = get_password_hash(request.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout user.
    """
    # In a real implementation, you might want to invalidate the token
    # This would require implementing a token blacklist
    return {"message": "Successfully logged out"}