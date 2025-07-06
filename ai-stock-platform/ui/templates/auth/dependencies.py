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
        from core.http_client import safe_post_json
        
        # Use the centralized HTTP client with proper error handling
        response_data = await safe_post_json(
            url=f"{API_URL}/api/auth/verify",
            json_data={"token": token},
            auth_token=token
        )
        
        if response_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or API unavailable"
            )
        
        return response_data
        
    except Exception as e:
        logger.error(f"API token verification failed: {str(e)}")
        logger.error(f"API connection error during token verification: {str(e)}")
        # Fall back to local verification if API is unavailable
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
