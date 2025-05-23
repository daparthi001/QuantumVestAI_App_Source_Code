from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from typing import Optional, Dict, Any, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from core.config.settings import settings
from core.config.constants import USER_ROLE_ADMIN

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an authentication token and extract user data.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            return None
        return {
            "username": username,
            "role": payload.get("role", "basic"),
            "exp": payload.get("exp")
        }
    except JWTError:
        return None

async def get_authenticated_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract and verify authenticated user from request.
    """
    token = request.cookies.get("token")
    if not token:
        return None
    user_data = await verify_token(token)
    return user_data

def require_auth(redirect_url: str = "/login") -> Callable:
    """
    Dependency to require authentication for routes.
    """
    async def dependency(request: Request) -> Dict[str, Any]:
        user = await get_authenticated_user(request)
        if not user:
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
        return user
    return dependency

def require_admin(redirect_url: str = "/login") -> Callable:
    """
    Dependency to require admin role for routes.
    """
    async def dependency(request: Request) -> Dict[str, Any]:
        user = await get_authenticated_user(request)
        if not user:
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

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding user authentication to every request.
    Adds 'user' to request.state.
    """
    async def dispatch(self, request: Request, call_next):
        user = await get_authenticated_user(request)
        request.state.user = user
        response = await call_next(request)
        return response

# Alias for flexibility
AuthMiddleware = AuthenticationMiddleware