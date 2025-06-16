"""
Authentication Middleware
Created: 2025-05-19 03:44:39
Author: daparthi001
Updated: 2025-06-16 03:03:46 by daparthi001ok
"""
import logging
import json
from fastapi import Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse, RedirectResponse
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

# Auth middleware class - must inherit from BaseHTTPMiddleware for proper ASGI compatibility
class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI
    """
    def __init__(self, app):
        super().__init__(app)
        # Paths that don't require authentication
        self.exclude_paths = [
            "/login",
            "/auth/login",
            "/auth/token",
            "/register",
            "/auth/register",
            "/password-reset",
            "/auth/password-reset",
            "/forgot-password",
            "/auth/forgot-password",
            "/static",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
        ]
    
    # This is the correct signature for the dispatch method
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and add authentication"""
        # Log the request path for debugging
        logger.info(f"Request path: {request.url.path}")
        
        # Skip auth for certain paths
        if self._should_skip_auth(request.url.path):
            logger.info(f"Skipping auth for path: {request.url.path}")
            return await call_next(request)

        # Check for authorization header
        authorization = request.headers.get("Authorization")
        
        # Also check for access_token in cookies
        if not authorization and "access_token" in request.cookies:
            authorization = request.cookies["access_token"]
            
        if not authorization:
            # Choose response based on Accept header to differentiate between
            # API requests and browser requests
            accept = request.headers.get("Accept", "")
            logger.info(f"No authorization found. Accept header: {accept}")
            
            if "text/html" in accept:
                # Browser request - redirect to login page with next parameter
                redirect_to = request.url.path
                if request.url.query:
                    redirect_to = f"{redirect_to}?{request.url.query}"
                logger.info(f"Redirecting to login with next={redirect_to}")
                return RedirectResponse(
                    f"/login?next={redirect_to}",
                    status_code=302
                )
            else:
                # API request - return JSON response
                logger.info("Returning JSON 401 response for API request")
                return self._handle_no_auth()

        # Validate token
        try:
            # Handle "Bearer" prefix
            if " " in authorization:
                token_type, token = authorization.split(None, 1)
                if token_type.lower() != "bearer":
                    logger.warning(f"Invalid token type: {token_type}")
                    return self._handle_invalid_token_type()
            else:
                # No token type prefix
                token = authorization
            
            # Decode and validate token
            logger.info("Validating token")
            user = await self._validate_token(token)
            
            # Log successful authentication
            logger.info(f"Authentication successful for user: {user.get('sub', 'unknown')}")
            
            # Add user to request state
            request.state.user = user
            
            # Continue with the request
            return await call_next(request)
        
        except Exception as e:
            logger.error(f"Auth middleware error: {e}", exc_info=True)
            return self._handle_auth_error(str(e))

    def _should_skip_auth(self, path: str) -> bool:
        """Determine if auth should be skipped for this path"""
        return any(path.startswith(skip_path) for skip_path in self.exclude_paths)
    
    async def _validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return user info"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid authentication token"
            )
    
    def _handle_no_auth(self) -> JSONResponse:
        """Handle request with no auth header"""
        # Return JSONResponse instead of raising HTTPException
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header not found"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _handle_invalid_token_type(self) -> JSONResponse:
        """Handle invalid token type"""
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token type. Bearer token required"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _handle_auth_error(self, error_message: str = "Authentication failed") -> JSONResponse:
        """Handle general auth error"""
        return JSONResponse(
            status_code=401,
            content={"detail": error_message},
            headers={"WWW-Authenticate": "Bearer"}
        )