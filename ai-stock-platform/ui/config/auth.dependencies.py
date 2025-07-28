# Authentication dependencies
# Last updated: 2025-06-20 03:05:12
# Updated by: daparthi001

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt

# Setup logging
logger = logging.getLogger(__name__)

# JWT Configuration
# Prefer JWT_SECRET but fall back to SECRET_KEY for backward compatibility
# Use the API default when neither is provided to avoid mismatched tokens
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

# API Configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")


# get_current_user function removed as per requirements

# validate_admin_access function removed as per requirements


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """
    Create a new JWT access token.
    
    Args:
        data: Data to encode in the JWT
        expires_delta: Optional expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Dict containing token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise
