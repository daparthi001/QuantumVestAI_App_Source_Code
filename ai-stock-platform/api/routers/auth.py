"""
Authentication Router
Updated: 2025-06-19 18:00:37
Author: daparthi001
"""
import logging
from datetime import timedelta
from typing import Annotated, Optional

from core.config import settings
from core.database import get_db_session
from core.models.response import StandardResponse
from core.security import (get_current_active_user, get_current_user,
                           get_password_hash, verify_password)
from core.security.tokens import create_access_token
# Use the SQLAlchemy model from the consolidated db.models package
from db.models.user import User
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, validator
from schemas.auth import TokenResponse, UserBase
from sqlalchemy.ext.asyncio import AsyncSession

# Create router WITHOUT a prefix (prefix will be added in main.py)
router = APIRouter(tags=["Authentication"])

logger = logging.getLogger("quantumvestai_api.auth")


# Registration request model
class RegisterRequest(BaseModel):
    """Registration request payload with basic validation."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    terms_accepted: bool = Field(...)

    @validator("confirm_password")
    def passwords_match(cls, v, values):  # noqa: D417
        password = values.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v

    @validator("terms_accepted")
    def terms_required(cls, v):  # noqa: D417
        if not v:
            raise ValueError("Terms must be accepted")
        return v


# Registration response model
class RegisterResponse(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


# Password reset request model
class PasswordResetRequest(BaseModel):
    email: EmailStr


# Password reset confirmation model
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


@router.post(
    "/login",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Login User",
    description="Authenticate user and return access token",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db_session),
):
    """Authenticate user and return token"""
    logger.info(f"Login attempt for user: {form_data.username}")

    # Find user by username and ensure related roles are loaded to avoid
    # asynchronous lazy loading issues
    user = await User.get_by_username(db, form_data.username)
    if user:
        await db.refresh(user, attribute_names=["user_roles"])

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
        expires_delta=access_token_expires,
    )

    logger.info(f"Successful login for user: {form_data.username}")

    return StandardResponse(
        status="success",
        message="Login successful",
        data=TokenResponse(access_token=access_token, token_type="bearer"),
    )


@router.get("/login")
async def login_get():
    """GET handler for login endpoint - shows helpful message"""
    return StandardResponse(
        status="error",
        message="This endpoint only accepts POST requests with form data.",
        data={
            "curl": "curl -X POST -d 'username=demo&password=password' http://dev.quantumvestai.com/api/v1/auth/login",
            "required_fields": ["username", "password"],
            "method": "POST",
        },
    )


@router.options("/login")
async def login_options():
    """Handle CORS preflight requests for login endpoint"""
    return Response(status_code=200)


@router.post(
    "/register",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Register a new user account",
)
async def register(
    register_data: RegisterRequest, db: AsyncSession = Depends(get_db_session)
):
    """Register a new user"""
    logger.info(
        f"Registration attempt for username: {register_data.username}, email: {register_data.email}"
    )

    # Check if username already exists
    existing_user = await User.get_by_username(db, register_data.username)
    if existing_user:
        logger.warning(
            f"Registration failed - username already exists: {register_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Check if email already exists
    existing_email = await User.get_by_email(db, register_data.email)
    if existing_email:
        logger.warning(
            f"Registration failed - email already exists: {register_data.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(register_data.password)

    new_user = User(
        username=register_data.username,
        email=register_data.email,
        hashed_password=hashed_password,
        full_name=register_data.full_name,
        is_active=True,
        role="user",  # Default role for new users
    )

    await new_user.save(db)

    logger.info(f"User registered successfully: {register_data.username}")

    # Return response without password
    return StandardResponse(
        status="success",
        message="User registered successfully",
        data=RegisterResponse(
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
        ),
    )


@router.get(
    "/me",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get current authenticated user details",
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user"""
    return StandardResponse(
        status="success",
        message="User details retrieved",
        data=UserBase(**current_user.__dict__),
    )


@router.post(
    "/password-reset/request",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Request a password reset email",
)
async def request_password_reset(
    reset_data: PasswordResetRequest, db: AsyncSession = Depends(get_db_session)
):
    """Request password reset"""
    logger.info(f"Password reset requested for email: {reset_data.email}")

    # Find user by email
    user = await User.get_by_email(db, reset_data.email)

    # Always return success to prevent email enumeration
    if not user:
        logger.warning(
            f"Password reset attempted for non-existent email: {reset_data.email}"
        )
        return StandardResponse(
            status="success",
            message="If your email is registered, you will receive password reset instructions",
            data=None,
        )

    # Generate password reset token
    # In a real implementation, we would:
    # 1. Generate a unique token
    # 2. Store it in the database with expiration
    # 3. Send an email with a link containing the token
    # For this demo, we'll simulate the process

    # In production, implement actual email sending here

    return StandardResponse(
        status="success",
        message="If your email is registered, you will receive password reset instructions",
        data=None,
    )


@router.post(
    "/password-reset/confirm",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm Password Reset",
    description="Reset password using token",
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm, db: AsyncSession = Depends(get_db_session)
):
    """Confirm password reset with token"""
    logger.info("Password reset confirmation attempt")

    # In a real implementation, we would:
    # 1. Validate the token and check expiration
    # 2. Find the user associated with the token
    # 3. Update the password
    # For this demo, we'll simulate the process

    # Mock implementation - would be replaced with real logic
    token_valid = (
        reset_data.token == "valid_token"
    )  # In production, validate against DB

    if not token_valid:
        logger.warning("Invalid or expired password reset token")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    # In production, implement actual password update logic here

    return StandardResponse(
        status="success", message="Password has been reset successfully", data=None
    )


@router.options("/register")
async def register_options():
    """Handle CORS preflight requests for register endpoint"""
    return Response(status_code=200)


@router.options("/password-reset/request")
async def password_reset_request_options():
    """Handle CORS preflight requests for password reset request endpoint"""
    return Response(status_code=200)


@router.options("/password-reset/confirm")
async def password_reset_confirm_options():
    """Handle CORS preflight requests for password reset confirm endpoint"""
    return Response(status_code=200)
