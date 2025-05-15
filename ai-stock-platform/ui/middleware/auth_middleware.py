from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from typing import Optional, Dict, Any, Callable
from functools import wraps
from ui.config.settings import settings
from ui.config.constants import USER_ROLE_ADMIN

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an authentication token and extract user data
    
    Args:
        token: JWT token string
        
    Returns:
        Dict containing user data or None if token is invalid
    """
    if not token:
        return None
        
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user data from token
        username = payload.get("sub")
        if username is None:
            return None
            
        # Return user data from token
        return {
            "username": username,
            "role": payload.get("role", "basic"),
            "exp": payload.get("exp")
        }
    except JWTError:
        return None

async def get_authenticated_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract and verify authenticated user from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict containing user data or None if not authenticated
    """
    # Try to get token from cookie
    token = request.cookies.get("token")
    if not token:
        return None
        
    # Verify the token
    user_data = await verify_token(token)
    return user_data

def require_auth(redirect_url: str = "/login") -> Callable:
    """
    Dependency to require authentication for routes
    
    Args:
        redirect_url: URL to redirect to if not authenticated
        
    Returns:
        Dependency function for FastAPI
    """
    async def dependency(request: Request) -> Dict[str, Any]:
        user = await get_authenticated_user(request)
        if not user:
            # If this is an API route, return 401 error
            if request.url.path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            else:
                # For UI routes, redirect to login page
                next_url = str(request.url).replace(str(request.base_url), '/')
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": f"{redirect_url}?next={next_url}"}
                )
        return user
    return dependency

def require_admin(redirect_url: str = "/login") -> Callable:
    """
    Dependency to require admin role for routes
    
    Args:
        redirect_url: URL to redirect to if not admin
        
    Returns:
        Dependency function for FastAPI
    """
    async def dependency(request: Request) -> Dict[str, Any]:
        user = await get_authenticated_user(request)
        if not user:
            # If not authenticated at all
            if request.url.path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            else:
                next_url = str(request.url).replace(str(request.base_url), '/')
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": f"{redirect_url}?next={next_url}"}
                )
        
        # Check for admin role
        if user.get("role") != USER_ROLE_ADMIN:
            if request.url.path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin privileges required"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                    headers={"Location": "/"}
                )
                
        return user
    return dependency

# Authentication middleware class for FastAPI
class AuthenticationMiddleware:
    """
    Middleware for adding user authentication to every request
    """
    
    async def __call__(self, request: Request, call_next):
        """
        Process request to add user data to request state
        """
        # Get user data if authenticated
        user = await get_authenticated_user(request)
        
        # Add user data to request state
        request.state.user = user
        
        # Process the request
        response = await call_next(request)
        return response