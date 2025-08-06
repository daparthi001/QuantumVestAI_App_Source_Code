"""
Authentication functionality.
Created: 2025-08-04
Author: gayatri
"""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from core.exceptions import AuthenticationError
from db.models.user import User
from db.session import get_db
from .tokens import validate_token

# Password context for hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False
)


def _strip_token(token: str) -> str:
    """Remove Bearer prefix and surrounding quotes from a token."""
    token = token.strip().strip('"')
    if token.startswith("Bearer "):
        token = token[7:]
    return token


async def get_token(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> str:
    """Retrieve access token from Authorization header or cookies."""
    token = token or request.cookies.get("access_token")
    if not token:
        raise AuthenticationError("Not authenticated")
    return _strip_token(token)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

async def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    """Get current user from token."""
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET.get_secret_value(), 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise AuthenticationError("Could not validate credentials")
            
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            raise AuthenticationError("User not found")
            
        if not user.is_active:
            raise AuthenticationError("Inactive user")
            
        return user
    except JWTError:
        raise AuthenticationError("Could not validate credentials")

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user."""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user

def check_admin_role(current_user = Depends(get_current_user)):
    """Check if user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
