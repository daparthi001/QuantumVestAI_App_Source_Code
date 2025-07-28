# Authentication dependencies
# Last updated: 2025-06-20 04:10:30
# Updated by: daparthi001

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from services.httpx_client import HTTPXService, create_httpx_service

# OAuth2 scheme for token extraction
oauth2_scheme = HTTPBearer(auto_error=False)


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

# get_optional_current_user function removed as per requirements

# validate_admin_access function removed as per requirements
async def get_current_user(
    request: Request,
    response: Response,
    token: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    """
    Validate user authentication from JWT token or session cookie.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        token: Bearer token from Authorization header
        access_token: Token from session cookie
        
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
    token_to_use = token or access_token
    
    if not token_to_use:
        # Redirect to login page if no token
        if request.url.path != "/login":
            return response.headers.append("Location", f"/login?next={request.url.path}")
        raise credentials_exception
    
    try:
        # Verify token with JWT
        payload = jwt.decode(token_to_use, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        exp_timestamp: int = payload.get("exp")
        
        if username is None:
            raise credentials_exception
        
        # Check if token is expired
        if exp_timestamp and time.time() > exp_timestamp:
            logger.info(f"Token expired for user {username}")
            if request.url.path != "/login":
                response.headers["Location"] = f"/login?next={request.url.path}"
            raise credentials_exception
        
        # Verify with API server using improved HTTPX client
        user_data = await verify_token_with_api_improved(token_to_use)
        
        return user_data
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in authentication: {str(e)}")
        raise credentials_exception

async def verify_token_with_api_improved(token: str) -> Dict[str, Any]:
    """
    Verify token with the API server using improved HTTPX client
    """
    try:
        # Create HTTPX service with authentication
        service = create_httpx_service(base_url=API_URL, auth_token=token)
        
        # Make request to verify token
        response = await service.post(
            "/auth/verify",
            json_data={"token": token},
            timeout=10.0
        )
        
        if response.status_code != 200:
            logger.error(f"Token verification failed: {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return response.json()
        
    except Exception as e:
        logger.error(f"API connection error during token verification: {str(e)}")
        
        # Fall back to local verification if API is unavailable
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {
                "username": payload.get("sub"),
                "email": payload.get("email"),
                "full_name": payload.get("name"),
                "permissions": payload.get("permissions", []),
                "token": token,
                "verified_locally": True
            }
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

async def get_optional_current_user(
    request: Request,
    response: Response,
    token: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(None)
) -> Optional[Dict[str, Any]]:
    """
    Similar to get_current_user but returns None instead of raising an exception
    if no valid token is found. This is useful for routes that work with or without
    authentication.
    
    Args:
        request: FastAPI request object
        response: FastAPI response object
        token: Bearer token from Authorization header
        access_token: Token from session cookie
        
    Returns:
        Dict containing user information or None if not authenticated
    """
    try:
        return await get_current_user(request, response, token, access_token)
    except HTTPException:
        return None

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
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
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
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
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
