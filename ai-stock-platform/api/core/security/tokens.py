"""Token handling functionality with improved debugging support."""
from datetime import datetime, timedelta
from typing import Optional

import logging
from jose import jwt, JWTError
from pydantic import BaseModel

from core.config import get_settings

# Setup module-level logger
logger = logging.getLogger(__name__)

config = get_settings()

# Warn when critical security settings are missing or using defaults
secret_value = (
    config.JWT_SECRET.get_secret_value()
    if getattr(config, "JWT_SECRET", None)
    else getattr(config, "SECRET_KEY", "")
)
if not secret_value or secret_value == "your-secret-key":
    logger.warning(
        "JWT secret key is not configured or using insecure default. Token validation may be compromised."
    )

class TokenHandler:
    # Use JWT_SECRET value if provided, falling back to SECRET_KEY
    SECRET_KEY = config.JWT_SECRET.get_secret_value() if hasattr(config, "JWT_SECRET") else config.SECRET_KEY
    ALGORITHM = config.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_MINUTES = getattr(config, "REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)

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
    def create_refresh_token(
        cls, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token with a longer expiration."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=cls.REFRESH_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> Optional[BaseModel]:
        return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Convenience wrapper to create an access token using :class:`TokenHandler`."""
    return TokenHandler.create_access_token(data, expires_delta)


def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Convenience wrapper to create a refresh token using :class:`TokenHandler`."""
    return TokenHandler.create_refresh_token(data, expires_delta)


def decode_token(token: str) -> Optional[BaseModel]:
    """Convenience wrapper to decode a JWT token."""
    return TokenHandler.decode_token(token)


def validate_token(token: str) -> bool:
    """Return ``True`` if the provided JWT is valid, ``False`` otherwise."""
    if not token:
        logger.warning("Token validation attempted with missing token")
        return False

    try:
        TokenHandler.decode_token(token)
        return True
    except JWTError as exc:
        logger.warning("Token validation failed: %s", exc)
        return False
