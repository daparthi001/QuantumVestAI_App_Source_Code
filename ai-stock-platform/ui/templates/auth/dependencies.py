# Authentication dependencies
# Last updated: 2025-06-20 02:53:45
# Updated by: daparthi001

from fastapi import Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
import jwt
import time
from datetime import datetime, timedelta
import logging
import os
import httpx

# Setup logging
logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# JWT Configuration
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-key")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

# API Configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

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
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def verify_token_with_api(token: str) -> Dict[str, Any]:
    """
    Verify token with the API server (more secure approach for production).
    
    Args:
        token: JWT token to verify
        
    Returns:
        Dict containing user information from API
        
    Raises:
        HTTPException: If token verification fails
    """
        logger.error(f"API connection error during token verification: {str(e)}")
        # Fall back to local verification if API is unavailable
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {
            "username": payload.get("sub"),
            "email": payload.get("email"),
            "full_name": payload.get("name"),
            "permissions": payload.get("permissions", []),
            "token": token,
            "verified_locally": True
        }