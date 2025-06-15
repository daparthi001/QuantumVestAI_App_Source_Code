"""
Authentication Middleware
Created: 2025-06-15 02:44:55
Author: daparthi001
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decode JWT token and return current user
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # You can add additional user data validation here
        return {"user_id": user_id}
    
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

class AuthMiddleware:
    """
    Authentication middleware for FastAPI
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next):
        # Skip auth for certain paths
        if self._should_skip_auth(request.url.path):
            return await call_next(request)

        # Check for authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return self._handle_no_auth()

        # Validate token
        try:
            token_type, token = authorization.split()
            if token_type.lower() != "bearer":
                return self._handle_invalid_token_type()
            
            # Decode and validate token
            user = self._validate_token(token)
            # Add user to request state
            request.state.user = user
            
            return await call_next(request)
        
        except Exception as e:
            logger.error(f"Auth middleware error: {e}")
            return self._handle_auth_error()

    def _should_skip_auth(self, path: str) -> bool:
        """Determine if auth should be skipped for this path"""
        skip_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return user info"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid authentication token"
            )
    
    def _handle_no_auth(self):
        """Handle request with no auth header"""
        raise HTTPException(
            status_code=401, 
            detail="Authorization header not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _handle_invalid_token_type(self):
        """Handle invalid token type"""
        raise HTTPException(
            status_code=401, 
            detail="Invalid token type. Bearer token required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _handle_auth_error(self):
        """Handle general auth error"""
        raise HTTPException(
            status_code=401, 
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )