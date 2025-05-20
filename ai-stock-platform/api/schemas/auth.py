"""
Authentication Schemas
Created: 2025-05-20 04:43:53
Author: daparthi001
"""
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str
    token_type: str
    user: UserResponse

class RegisterRequest(BaseModel):
    """Register request schema."""
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    full_name: Optional[str]

class RegisterResponse(BaseModel):
    """Register response schema."""
    success: bool
    user_id: int
    created_at: str

class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    current_password: str
    new_password: constr(min_length=8)

class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr