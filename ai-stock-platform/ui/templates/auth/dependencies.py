# Authentication dependencies
# Last updated: 2025-06-20 02:53:45
# Updated by: daparthi001

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import HTTPException, status

# Setup logging
logger = logging.getLogger(__name__)

# JWT Configuration
# Prefer JWT_SECRET but fall back to SECRET_KEY for backward compatibility
JWT_SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "default-dev-key")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))

# API Configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000")


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

async def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token with API verification fallback.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Dict containing token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # First try to verify with API server using improved HTTPX client
        from core.http_client import safe_post_json
        
        response_data = await safe_post_json(
            url=f"{API_URL}/api/auth/verify",
            json_data={"token": token},
            auth_token=token
        )
        
        if response_data is not None:
            return response_data
            
    except Exception as e:
        logger.error(f"API token verification failed: {str(e)}")
    
    # Fall back to local JWT verification if API is unavailable
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {
            "username": payload.get("sub"),
            "email": payload.get("email"),
            "full_name": payload.get("name"),
            "permissions": payload.get("permissions", []),
            "token": token,
            "verified_locally": True
        }
    except jwt.PyJWTError as jwt_error:
        logger.error(f"Local token verification failed: {str(jwt_error)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
