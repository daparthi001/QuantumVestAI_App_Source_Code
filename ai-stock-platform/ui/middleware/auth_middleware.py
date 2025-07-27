"""
Simplified authentication middleware for QuantumVestAI UI.
This demo version validates optional Bearer tokens and attaches
user information to the request state. If no valid token is
provided, browser requests are redirected to the login page while
API requests receive a 401 JSON response.
"""

import logging
import os
from typing import Any, Dict, Optional
from datetime import timedelta, datetime

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, RedirectResponse, Response
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

try:
    # Import from the API package to ensure we get the actual Settings
    # instance.  Using the ``core`` compatibility layer can return the
    # module object when both packages are present on ``PYTHONPATH``.
    from core.config.settings import settings
except Exception:  # pragma: no cover - fallback if settings import fails
    class Settings:
        SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "supersecretkey123456789abcdef")
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30

    settings = Settings()
    logger.warning("Using fallback settings in auth middleware")


async def verify_token(token: str) -> Dict[str, Any]:
    """Validate JWT token and return user info."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid token payload")
        return {"username": username}
    except (JWTError, ValueError) as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")


class AuthMiddleware(BaseHTTPMiddleware):
    """Minimal authentication middleware."""

    def __init__(self, app):
        super().__init__(app)
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
        logger.info("Auth middleware initialized")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self._should_skip_auth(request.url.path):
            return await call_next(request)

        token = request.headers.get("Authorization")
        if not token and "access_token" in request.cookies:
            token = request.cookies["access_token"]

        if not token:
            accept = request.headers.get("Accept", "")
            if "text/html" in accept:
                redirect_to = request.url.path
                if request.url.query:
                    redirect_to = f"{redirect_to}?{request.url.query}"
                return RedirectResponse(f"/login?next={redirect_to}", status_code=302)
            return self._handle_no_auth()

        if token.lower().startswith("bearer "):
            token = token[7:]
        else:
            return self._handle_invalid_token_type()

        try:
            user = await verify_token(token)
            request.state.user = user
        except HTTPException as e:
            return self._handle_auth_error(e.detail)

        return await call_next(request)

    def _should_skip_auth(self, path: str) -> bool:
        return any(path.startswith(skip) for skip in self.exclude_paths)

    def _handle_no_auth(self) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header not found"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _handle_invalid_token_type(self) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token type. Bearer token required"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _handle_auth_error(self, error_message: str = "Authentication failed") -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": error_message},
            headers={"WWW-Authenticate": "Bearer"},
        )
