"""
Authentication schemas
Created: 2025-05-19 03:27:22
Author: daparthi001
"""
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = None

class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: str = None
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        orm_mode = True