"""Authentication utilities and helpers."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from db.session import get_db
from db.models.user import User as DBUser
from .tokens import TokenHandler

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> Optional[DBUser]:
    """Retrieve a user by username."""
    return db.query(DBUser).filter(DBUser.username == username).first()


async def authenticate_user(db: Session, username: str, password: str) -> Optional[DBUser]:
    """Authenticate a user using the database."""
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> DBUser:
    """Retrieve the current user based on the provided JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = TokenHandler.decode_token(token)
        username = payload.get("sub") or payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: DBUser = Depends(get_current_user),
) -> DBUser:
    """Ensure the authenticated user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
