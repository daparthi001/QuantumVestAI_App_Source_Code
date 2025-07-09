from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Base user fields shared across schemas."""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    """Schema for user creation."""
    password: str

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserProfile(UserBase):
    """Public user profile schema."""
    id: int

# Backwards compatible alias used in some modules
User = UserProfile
