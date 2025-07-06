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

async def get_current_user(
    request: Request,
    response: Response,
    token: Optional[str] = Depends(oauth2_scheme),
    session_token: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    """
    Validate user authentication from JWT token or session cookie.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        token: Bearer token from Authorization header
        session_token: Token from session cookie
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Use token from Authorization header or cookie
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Prioritize token from Authorization header
    token_to_use = token or session_token
    
    if not token_to_use:
        # Redirect to login page if no token
        if request.url.path != "/login":
            return response.headers.append("Location", f"/login?next={request.url.path}")
        raise credentials_exception
    
    try:
        # Verify token with JWT
        payload = jwt.decode(token_to_use, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        exp_timestamp: int = payload.get("exp")
        
        if username is None:
            raise credentials_exception
        
        # Check if token is expired
        if exp_timestamp and time.time() > exp_timestamp:
            logger.info(f"Token expired for user {username}")
            if request.url.path != "/login":
                return response.headers.append("Location", f"/login?next={request.url.path}")
            raise credentials_exception
        
        # In a real implementation, validate with the API
        # This is a simplified example for demonstration
        user_data = {
            "username": username,
            "email": payload.get("email"),
            "full_name": payload.get("name"),
            "permissions": payload.get("permissions", []),
            "token": token_to_use
        }
        
        return user_data
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception

async def validate_admin_access(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Validate that the current user has admin permissions.
    
    Args:
        user: User information from get_current_user
        
    Returns:
        The user dict if they have admin permissions
        
    Raises:
        HTTPException: If user doesn't have admin permissions
    """
    if "admin" not in user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return user

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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/auth/verify",
                json={"token": token},
                timeout=5.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            return response.json()
    except httpx.RequestError as e:
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