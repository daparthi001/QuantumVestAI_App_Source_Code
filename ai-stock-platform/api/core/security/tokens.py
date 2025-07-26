"""
Token handling functionality.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from pydantic import BaseModel

from core.config import get_settings

config = get_settings()

class TokenHandler:
    # Use JWT_SECRET value if provided, falling back to SECRET_KEY
    SECRET_KEY = config.JWT_SECRET.get_secret_value() if hasattr(config, "JWT_SECRET_KEY") else config.SECRET_KEY
    ALGORITHM = config.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> Optional[BaseModel]:
        return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Convenience wrapper to create an access token using :class:`TokenHandler`."""
    return TokenHandler.create_access_token(data, expires_delta)


def decode_token(token: str) -> Optional[BaseModel]:
    """Convenience wrapper to decode a JWT token."""
    return TokenHandler.decode_token(token)
