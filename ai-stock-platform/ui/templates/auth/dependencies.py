# Authentication dependencies
# Last updated: 2025-06-20 02:53:45
# Updated by: daparthi001

from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import logging
import os

# Setup logging
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

# API Configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

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
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
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
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise