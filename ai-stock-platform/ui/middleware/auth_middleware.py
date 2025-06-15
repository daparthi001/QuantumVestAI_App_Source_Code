"""
Authentication Middleware
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-15 03:52:21 by daparthi001
"""
import logging
from fastapi import Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union

# Try to import settings safely
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    class Settings:
        SECRET_KEY = "supersecretkey123456789abcdef"
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Helper function to get current user from token
async def get_current_user(token: str) -> Dict[str, Any]:
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

# Auth middleware class - must inherit from BaseHTTPMiddleware for proper ASGI compatibility
class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI
    """
    def __init__(self, app):
        super().__init__(app)
        # Paths that don't require authentication
        self.exclude_paths = [
            "/auth/login",
            "/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/static",
        ]
    
    # This is the correct signature for the __call__ method
    # Overriding dispatch instead of __call__ in BaseHTTPMiddleware
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and add authentication"""
        # Skip auth for certain paths
        if self._should_skip_auth(request.url.path):
            return await call_next(request)

        # Check for authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            # For excluded paths, just continue without auth
            if self._is_path_excluded(request.url.path):
                return await call_next(request)
            return self._handle_no_auth()

        # Validate token
        try:
            token_type, token = authorization.split()
            if token_type.lower() != "bearer":
                return self._handle_invalid_token_type()
            
            # Decode and validate token
            user = await self._validate_token(token)
            # Add user to request state
            request.state.user = user
            
            return await call_next(request)
        
        except Exception as e:
            logger.error(f"Auth middleware error: {e}")
            # For excluded paths, just continue without auth even if there's an error
            if self._is_path_excluded(request.url.path):
                return await call_next(request)
            return self._handle_auth_error()

    def _should_skip_auth(self, path: str) -> bool:
        """Determine if auth should be skipped for this path"""
        return any(path.startswith(skip_path) for skip_path in self.exclude_paths)
    
    def _is_path_excluded(self, path: str) -> bool:
        """Check if the path is in the exclude list"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)
    
    async def _validate_token(self, token: str) -> Dict[str, Any]:
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