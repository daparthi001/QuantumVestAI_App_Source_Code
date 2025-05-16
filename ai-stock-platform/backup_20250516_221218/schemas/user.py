from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user data."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def password_complexity(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserInDB(UserBase):
    """Schema for user data from database."""
    id: int
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class UserPublic(UserBase):
    """Schema for public user data."""
    id: int
    role: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    class Config:
        orm_mode = True

class UserPrivate(UserPublic):
    """Schema for private user data."""
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_expiry: Optional[datetime] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    phone: Optional[str] = None
    timezone: str
    api_key: str
    
    class Config:
        orm_mode = True