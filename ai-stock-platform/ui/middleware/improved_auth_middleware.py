"""
Improved Authentication Middleware
Created to fix login state persistence issues

This middleware provides consistent authentication handling and login state persistence
across browser sessions and tabs.
"""
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import quote

import jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

logger = logging.getLogger("quantumvestai.auth_middleware")

# JWT Configuration - independent of settings to avoid circular dependencies
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"

# Protected routes that require authentication
PROTECTED_ROUTES = {
    "/settings", "/dashboard", "/profile", "/portfolio", "/watchlist", 
    "/market/analysis", "/forecast", "/notifications"
}

# Public routes that don't require authentication
PUBLIC_ROUTES = {
    "/", "/login", "/auth/login", "/register", "/auth/register", 
    "/auth/forgot-password", "/health", "/static", "/api/health",
    "/sw.js", "/favicon.ico", "/robots.txt"  # Static assets that should always be public
}


class ImprovedAuthMiddleware(BaseHTTPMiddleware):
    """
    Improved authentication middleware that provides:
    - Consistent login state persistence
    - Cross-tab authentication synchronization  
    - Proper cookie handling
    - Graceful error handling
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.logger = logger
        
    async def dispatch(self, request: Request, call_next):
        """Process request with improved authentication handling"""
        start_time = time.time()
        path = request.url.path
        
        try:
            # Add request ID for tracking
            request_id = f"auth-{int(start_time * 1000)}"
            request.state.request_id = request_id
            
            # Check if authentication is required for this path
            requires_auth = self._requires_authentication(path)
            
            if requires_auth:
                auth_result = await self._authenticate_request(request)
                
                if auth_result["authenticated"]:
                    # Store user info in request state for route handlers
                    request.state.user = auth_result["user"]
                    request.state.authenticated = True
                else:
                    # Redirect to login for unauthenticated requests to protected routes
                    login_url = f"/auth/login?next={quote(str(request.url))}"
                    return RedirectResponse(url=login_url, status_code=302)
            else:
                # For public routes, still try to get user info if available
                auth_result = await self._authenticate_request(request)
                if auth_result["authenticated"]:
                    request.state.user = auth_result["user"]
                    request.state.authenticated = True
                else:
                    request.state.user = None
                    request.state.authenticated = False
            
            # Process the request
            response = await call_next(request)
            
            # Add authentication headers for debugging
            if hasattr(request.state, "authenticated"):
                response.headers["X-Auth-Status"] = "authenticated" if request.state.authenticated else "unauthenticated"
            
            duration = time.time() - start_time
            self.logger.debug(f"[{request_id}] Auth middleware processed {path} in {duration:.3f}s")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Auth middleware error for {path}: {str(e)}")
            # Continue with request even if auth middleware fails
            response = await call_next(request)
            response.headers["X-Auth-Error"] = "middleware-error"
            return response
    
    def _requires_authentication(self, path: str) -> bool:
        """Check if the given path requires authentication"""
        # Exact matches for protected routes
        if path in PROTECTED_ROUTES:
            return True
            
        # Check if path starts with any protected route pattern
        for protected_path in PROTECTED_ROUTES:
            if path.startswith(protected_path + "/"):
                return True
        
        # Public routes and static assets don't require auth
        for public_path in PUBLIC_ROUTES:
            if path.startswith(public_path):
                return False
        
        # API endpoints generally don't require auth through middleware
        if path.startswith("/api/"):
            return False
            
        # Default to requiring authentication for unknown routes
        return True
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """
        Authenticate request using multiple token sources with improved persistence
        
        Returns:
            Dict with 'authenticated' bool and 'user' data if authenticated
        """
        # Try multiple token sources in order of preference
        token = self._extract_token_from_request(request)
        
        if not token:
            return {"authenticated": False, "user": None}
        
        try:
            # Verify and decode the token
            user_data = await self._verify_token(token)
            
            if user_data:
                self.logger.debug(f"Authentication successful for user: {user_data.get('username', 'unknown')}")
                return {"authenticated": True, "user": user_data}
            else:
                self.logger.debug("Token verification failed")
                return {"authenticated": False, "user": None}
                
        except Exception as e:
            self.logger.warning(f"Token verification error: {str(e)}")
            return {"authenticated": False, "user": None}
    
    def _extract_token_from_request(self, request: Request) -> Optional[str]:
        """Extract authentication token from various sources"""
        # 1. Authorization header (Bearer token)
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        # 2. access_token cookie (HttpOnly, most secure)
        access_token_cookie = request.cookies.get("access_token")
        if access_token_cookie:
            if access_token_cookie.startswith("Bearer "):
                return access_token_cookie[7:]
            return access_token_cookie
        
        # 3. qvai_token cookie (JavaScript accessible, for SPA)
        qvai_token_cookie = request.cookies.get("qvai_token")
        if qvai_token_cookie:
            return qvai_token_cookie
        
        # 4. token query parameter (least secure, only for special cases)
        token_param = request.query_params.get("token")
        if token_param:
            return token_param
        
        return None
    
    async def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return user data
        
        Args:
            token: JWT token to verify
            
        Returns:
            User data dict if token is valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp and time.time() > exp_timestamp:
                self.logger.debug("Token expired")
                return None
            
            # Extract user information
            username = payload.get("sub")
            if not username:
                self.logger.debug("Token missing username (sub)")
                return None
            
            user_data = {
                "username": username,
                "email": payload.get("email", ""),
                "full_name": payload.get("name", username),
                "role": payload.get("role", "user"),
                "permissions": payload.get("permissions", []),
                "token": token,
                "expires_at": exp_timestamp,
                "verified_at": datetime.utcnow().isoformat()
            }
            
            return user_data
            
        except jwt.ExpiredSignatureError:
            self.logger.debug("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.debug(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            self.logger.warning(f"Token verification error: {str(e)}")
            return None


def create_persistent_auth_cookies(response: Response, token: str, remember: bool = False, 
                                   user_info: Dict[str, Any] = None, secure: bool = False) -> None:
    """
    Create persistent authentication cookies with improved settings
    
    Args:
        response: FastAPI response object
        token: Authentication token
        remember: Whether to use long-term persistence (7 days vs 1 day)
        user_info: User information to store in cookies
        secure: Whether to use secure cookies (HTTPS only)
    """
    # Set cookie duration
    max_age = 7 * 24 * 60 * 60 if remember else 24 * 60 * 60  # 7 days or 1 day
    
    # Set secure HttpOnly cookie for server-side authentication
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        max_age=max_age,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/"
    )
    
    # Set JavaScript-accessible cookie for SPA functionality
    response.set_cookie(
        key="qvai_token", 
        value=token,
        max_age=max_age,
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/"
    )
    
    # Set user info cookie if provided
    if user_info:
        user_info_value = "|".join([
            user_info.get("username", ""),
            user_info.get("role", "user"),
            user_info.get("full_name", "")
        ])
        response.set_cookie(
            key="user_info",
            value=user_info_value,
            max_age=max_age,
            httponly=False,
            secure=secure,
            samesite="lax",
            path="/"
        )
    
    logger.info(f"Created persistent auth cookies for user {user_info.get('username', 'unknown') if user_info else 'unknown'}")


def clear_auth_cookies(response: Response) -> None:
    """Clear all authentication-related cookies"""
    cookie_names = ["access_token", "qvai_token", "user_info"]
    
    for cookie_name in cookie_names:
        response.delete_cookie(
            key=cookie_name,
            path="/",
            samesite="lax"
        )
    
    logger.info("Cleared all authentication cookies")