"""
User schemas for QuantumVestAI API
Created: 2025-07-23
Author: daparthi001
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


# ==========================================
# BASE SCHEMAS
# ==========================================

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    display_name: Optional[str] = Field(None, max_length=100, description="Custom display name")

    @validator('username')
    def validate_username(cls, v):
        if v:
            v = v.lower().strip()
            if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores, hyphens, and dots')
        return v

    @validator('first_name', 'last_name', 'display_name')
    def validate_names(cls, v):
        if v:
            return v.strip()
        return v


# ==========================================
# REQUEST SCHEMAS
# ==========================================

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    password_confirm: Optional[str] = Field(None, description="Password confirmation")
    is_active: Optional[bool] = Field(True, description="User active status")
    is_verified: Optional[bool] = Field(False, description="Email verification status")
    default_role: Optional[str] = Field("user", description="Default role to assign")

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
                "password_confirm": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "display_name": "Johnny",
                "is_active": True,
                "is_verified": False,
                "default_role": "user"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

    @validator('username')
    def validate_username(cls, v):
        if v:
            v = v.lower().strip()
            if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores, hyphens, and dots')
        return v

    @validator('first_name', 'last_name', 'display_name')
    def validate_names(cls, v):
        if v is not None and v.strip() == '':
            return None
        if v:
            return v.strip()
        return v

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "display_name": "Johnny D",
                "is_active": True
            }
        }


class PasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")

    @validator('new_password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v


# ==========================================
# RESPONSE SCHEMAS
# ==========================================

class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: int
    uuid: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: str
    display_name: Optional[str]
    effective_display_name: str
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    is_admin: bool
    is_superuser: bool  # Backward compatibility
    primary_role: str
    role: str  # Legacy field
    roles: List[str]
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "full_name": "John Doe",
                "display_name": "Johnny",
                "effective_display_name": "Johnny",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "is_verified": True,
                "is_admin": False,
                "is_superuser": False,
                "primary_role": "user",
                "role": "free",
                "roles": ["user"],
                "last_login": "2025-07-23T10:30:00Z",
                "created_at": "2025-07-23T10:00:00Z",
                "updated_at": "2025-07-23T10:30:00Z"
            }
        }


class UserPublic(BaseModel):
    """Schema for public user information"""
    id: int
    uuid: UUID
    username: str
    full_name: str
    display_name: Optional[str]
    effective_display_name: str
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: List[UserProfile]
    total: int
    skip: int
    limit: int

    class Config:
        schema_extra = {
            "example": {
                "users": [],
                "total": 25,
                "skip": 0,
                "limit": 10
            }
        }


class UserSuggestion(BaseModel):
    """Schema for user search suggestions"""
    id: int
    uuid: UUID
    username: str
    full_name: str
    email: str
    avatar_url: Optional[str]

    class Config:
        orm_mode = True


class UserSuggestionsResponse(BaseModel):
    """Schema for user suggestions response"""
    suggestions: List[UserSuggestion]


# ==========================================
# ROLE-RELATED SCHEMAS
# ==========================================

class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., max_length=50, description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Role permissions")


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None


class Role(RoleBase):
    """Schema for role response"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserRoleAssignment(BaseModel):
    """Schema for assigning roles to users"""
    user_id: int
    role_names: List[str] = Field(..., description="List of role names to assign")


class UserRoleResponse(BaseModel):
    """Schema for user role assignment response"""
    user_id: int
    role_id: int
    role_name: str
    assigned_at: datetime
    assigned_by: Optional[int]

    class Config:
        orm_mode = True


# ==========================================
# AUTHENTICATION SCHEMAS
# ==========================================

class LoginRequest(BaseModel):
    """Schema for login request"""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="Password")
    remember_me: Optional[bool] = Field(False, description="Remember me option")

    class Config:
        schema_extra = {
            "example": {
                "username_or_email": "johndoe",
                "password": "securepassword123",
                "remember_me": False
            }
        }


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {}
            }
        }


class RegisterRequest(UserCreate):
    """Schema for user registration"""
    terms_accepted: bool = Field(..., description="Terms and conditions acceptance")
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")

    @validator('new_password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# ==========================================
# UTILITY SCHEMAS
# ==========================================

class MessageResponse(BaseModel):
    """Schema for simple message responses"""
    message: str
    success: bool = True

    class Config:
        schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None
    success: bool = False

    class Config:
        schema_extra = {
            "example": {
                "detail": "User not found",
                "error_code": "USER_NOT_FOUND",
                "success": False
            }
        }