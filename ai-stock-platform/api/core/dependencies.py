"""
Common dependencies for API endpoints.
"""
from typing import Generator

from core.exceptions import AuthenticationError, PermissionError
from core.security import decode_token, get_token
from db.session import SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session

from models.user import User

async def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
) -> User:
    """Get current authenticated user."""
    try:
        payload = decode_token(token)
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            raise AuthenticationError("User not found")
        if not user.is_active:
            raise AuthenticationError("Inactive user")
        return user
    except Exception as e:
        raise AuthenticationError(str(e))

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        raise PermissionError("Admin privileges required")
    return current_user
