"""
Authentication Module
Created: 2025-05-21 16:53:29
Author: daparthi001
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

from core.config import settings
from core.utils.password import verify_password
from db.models.user import User

def authenticate_user(db_session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password
    
    Args:
        db_session: Database session
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        Optional[User]: User if authenticated, None otherwise
    """
    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt