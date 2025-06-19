"""
Authentication Router
Updated: 2025-06-19 04:35:11
Author: daparthi001
"""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.core.auth.jwt import create_access_token
from api.core.auth.hashing import verify_password
from api.core.auth.dependencies import get_current_user, get_current_active_user
from api.core.database import get_db_session
from api.core.config import settings
from api.models.response import StandardResponse
from api.models.user import User
from api.schemas.auth import Token, UserResponse

# Create router WITHOUT a prefix (prefix will be added in main.py)
router = APIRouter(tags=["Authentication"])

logger = logging.getLogger("quantumvestai_api.auth")

@router.post(
    "/login",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Login User",
    description="Authenticate user and return access token"
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticate user and return token"""
    logger.info(f"Login attempt for user: {form_data.username}")
    
    # Find user by username
    user = await User.get_by_username(db, form_data.username)
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user: {form_data.username}")
    
    return StandardResponse(
        status="success",
        message="Login successful",
        data=Token(
            access_token=access_token,
            token_type="bearer"
        )
    )

@router.get(
    "/me",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get current authenticated user details"
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user"""
    return StandardResponse(
        status="success",
        message="User details retrieved",
        data=UserResponse.from_orm(current_user)
    )

# Other auth endpoints remain the same