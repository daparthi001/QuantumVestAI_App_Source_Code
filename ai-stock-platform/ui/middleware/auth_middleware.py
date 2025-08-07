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
import httpx

# Use the shared HTTP client utilities for API verification
from core.http_client import safe_post_json

logger = logging.getLogger(__name__)

try:
    # Import from the API package to ensure we get the actual Settings
    # instance.  Using the ``core`` compatibility layer can return the
    # module object when both packages are present on ``PYTHONPATH``.
    from core.config.settings import settings
except Exception:  # pragma: no cover - fallback if settings import fails
    class Settings:
        # Match API default to prevent token verification issues during import failures
        SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key")
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30

    settings = Settings()
    logger.warning("Using fallback settings in auth middleware")


async def verify_token(token: str) -> Dict[str, Any]:
    """Validate JWT token and return user info.

    The middleware first attempts local JWT validation using the configured
    ``SECRET_KEY``.  If that fails (commonly due to the UI and API using
    different secrets) it falls back to calling the API's ``/auth/verify``
    endpoint.  This ensures the UI remains functional even when the secrets are
    misconfigured, matching the behaviour described in the project
    documentation.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid token payload")
        
        # Check if token is close to expiration and log a warning
        exp = payload.get("exp")
        if exp:
            from datetime import datetime, timezone
            exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            now = datetime.now(tz=timezone.utc)
            time_until_exp = exp_time - now
            
            if time_until_exp.total_seconds() < 300:  # Less than 5 minutes
                logger.warning(f"Token for user {username} expires in {time_until_exp.total_seconds():.0f} seconds")
                
        return {"username": username}
    except (JWTError, ValueError) as decode_error:
        logger.warning(f"Token verification failed: {decode_error}")

        api_url = os.getenv("API_URL", getattr(settings, "API_BASE_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")).rstrip("/")
        verify_urls = [
            f"{api_url}/api/v1/auth/verify",
        ]
        # Try each verification URL in order
        last_error = None
        for verify_url in verify_urls:
            try:
                resp = await safe_post_json(verify_url, json_data={"token": token})
                if resp and resp.get("status") == "success":
                    user = resp.get("data", {}).get("user", {})
                    username = user.get("username") or user.get("id")
                    if username:
                        logger.info(f"Token verification successful via {verify_url}")
                        return {"username": username}
                else:
                    # Log the response for debugging
                    logger.warning(f"Token verification failed at {verify_url}: {resp}")
            except httpx.HTTPStatusError as api_error:
                last_error = api_error
                status_code = api_error.response.status_code
                reason = api_error.response.reason_phrase
                if status_code == 401:
                    # 401 from API means the token is invalid, this is expected for invalid tokens
                    logger.debug(f"Token rejected by API at {verify_url}: {reason}")
                else:
                    # Other HTTP errors might be temporary (5xx) so log as error
                    logger.error(f"HTTP {status_code} error during token verification at {verify_url}: {reason}")
            except Exception as api_error:
                last_error = api_error
                logger.error(f"Failed request: POST {verify_url} - Error: {str(api_error)}")

        # If we reach here, all verification attempts failed
        if last_error:
            if isinstance(last_error, httpx.HTTPStatusError) and last_error.response.status_code == 401:
                # 401 errors are expected for invalid tokens, don't log as error
                logger.debug(f"Token verification failed - API returned 401 Unauthorized")
                error_detail = "Invalid authentication token"
            else:
                error_detail = f"Token verification failed - {str(last_error)}"
                logger.error(f"All token verification attempts failed. Last error: {error_detail}")
        else:
            error_detail = "Token verification failed - invalid response format"
            logger.error(f"All token verification attempts failed. Last error: {error_detail}")
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
            "/stocks/flow",
            "/static",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/sw.js",  # Service worker should not require authentication
            "/favicon.ico",  # Favicon requests should not require authentication
            "/robots.txt",  # Robots.txt should not require authentication
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
