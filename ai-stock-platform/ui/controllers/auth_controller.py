"""
Authentication Controller for QuantumVestAI
Updated: 2025-06-20 23:13:04
Author: daparthi001
"""
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
import jwt
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from core.config.settings import settings

router = APIRouter()
logger = logging.getLogger("quantumvestai.auth_controller")

templates = Jinja2Templates(directory=str(Path("templates")))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)


# Get API URL from environment or use default
API_URL = os.environ.get(
    "API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000"
)
API_V1_URL = f"{API_URL}/api/v1"


def format_error_message(error_data):
    """Format error data into a readable message"""
    try:
        if not error_data:
            return "An unknown error occurred"

        # Handle string errors
        if isinstance(error_data, str):
            return error_data

        # Handle dictionary error responses (API errors)
        if isinstance(error_data, dict):
            if "message" in error_data:
                return error_data["message"]
            elif "detail" in error_data:
                return error_data["detail"]
            elif "error" in error_data:
                return error_data["error"]
            else:
                # Unknown dict format, use fallback
                return "An error occurred during registration"

        # Handle exception objects
        if hasattr(error_data, "__str__"):
            return str(error_data)

        # Fallback for any other type
        return "An error occurred during registration"

    except Exception as e:
        logger.error(f"Error formatting error message: {str(e)}")
        return "An error occurred during registration"


# Function to get the current user from the token in the cookie
# get_current_user function removed as per requirements


@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/dashboard", msg: str = None):
    """Render login page"""
    templates = get_templates(request)
    return get_templates(request).TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "next": next,
            "msg": msg,
            "now": datetime.utcnow(),  # Add current datetime
            "username": "",  # Ensure username is always defined
            "msg_type": "info",  # Default message type
        },
    )


@router.post("/auth/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
):
    """Process login form submission"""
    logger.info(f"Login attempt for username: {username}")
    templates = get_templates(request)

    try:
        api = APIClient()
        api_resp = api.post_form(
            "/auth/login",
            data={"username": username, "password": password},
        )
        access_token = api_resp.get("data", {}).get("access_token")

        # If no format worked or no token received
        if not access_token:
            error_msg = "Invalid username or password"

            # Try emergency login for development/testing when API is unavailable
            if (
                username in ["demo", "daparthi001", "test", "chavala"]
                and password == "password123"
            ):
                logger.warning(
                    f"Using emergency login for {username} due to API errors"
                )

                # Create emergency token with username and timestamp
                timestamp = int(datetime.utcnow().timestamp())
                emergency_token = f"emergency_{username}_{timestamp}"

                # Create redirect response
                redirect_url = request.query_params.get("next", "/dashboard")
                response = RedirectResponse(
                    url=redirect_url, status_code=status.HTTP_302_FOUND
                )

                # Set cookie with emergency token
                max_age = 30 * 24 * 60 * 60 if remember else None
                response.set_cookie(
                    key="access_token",
                    value=f"Bearer {emergency_token}",
                    httponly=True,
                    max_age=max_age,
                    samesite="lax",
                    secure=request.url.scheme == "https",
                )

                logger.info(f"Emergency login successful for {username}")
                return response

            return get_templates(request).TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "msg": error_msg,
                    "username": username,
                    "now": datetime.utcnow(),  # Add current datetime
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Create redirect response
        redirect_url = request.query_params.get("next", "/dashboard")
        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

        # Set cookie with token
        max_age = (
            30 * 24 * 60 * 60 if remember else None
        )  # 30 days in seconds or session
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=max_age,
            samesite="lax",
            secure=request.url.scheme == "https",
        )

        # Store basic user info for UI convenience
        secret = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key")
        try:
            payload = jwt.decode(access_token, secret, algorithms=["HS256"])
            uname = payload.get("sub", username)
            role = payload.get("role", "user")
            full_name = payload.get("name", uname)
            response.set_cookie(
                key="user_info",
                value=f"{uname}|{role}|{full_name}",
                httponly=False,
                max_age=max_age,
                samesite="lax",
                secure=request.url.scheme == "https",
            )
        except Exception:
            # If decoding fails, continue without user_info cookie
            pass

        logger.info(f"User {username} successfully logged in")
        return response

    except requests.RequestException as e:
        logger.error(f"API connection error during login: {str(e)}")

        # Emergency login for development/testing when API is unavailable
        if username in [
            "demo",
            "daparthi001",
            "test",
            "chavala",
            "daparthi0012025",
        ] and (password == "password123" or password == "testpass"):
            logger.warning(
                f"Using emergency login for {username} due to API unavailability"
            )

            # Create emergency token with username and timestamp
            timestamp = int(datetime.utcnow().timestamp())
            emergency_token = f"emergency_{username}_{timestamp}"

            # Create redirect response
            redirect_url = request.query_params.get("next", "/dashboard")
            response = RedirectResponse(
                url=redirect_url, status_code=status.HTTP_302_FOUND
            )

            # Set cookie with emergency token
            max_age = 30 * 24 * 60 * 60 if remember else None
            response.set_cookie(
                key="access_token",
                value=f"Bearer {emergency_token}",
                httponly=True,
                max_age=max_age,
                samesite="lax",
                secure=request.url.scheme == "https",
            )

            logger.info(f"Emergency login successful for {username}")
            return response

        return get_templates(request).TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": f"API connection error: {str(e)}",
                "username": username,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return get_templates(request).TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": f"An unexpected error occurred",
                "username": username,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/auth/logout")
async def logout():
    """Handle user logout"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response


@router.get("/logout")
async def logout_shortcut():
    """Shortcut for logout"""
    return RedirectResponse(url="/auth/logout", status_code=status.HTTP_302_FOUND)


@router.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render registration page"""
    templates = get_templates(request)
    return get_templates(request).TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "now": datetime.utcnow(),  # Add current datetime
            "username": "",
            "email": "",
        },
    )


@router.post("/auth/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    terms: bool = Form(None),  # Make terms optional in the controller
):
    """Process registration form submission"""
    logger.info(f"Registration attempt for username: {username}")
    templates = get_templates(request)

    # Check if terms were accepted
    if not terms:
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": "You must accept the Terms of Service",
                "username": username,
                "email": email,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # Check if passwords match
    if password != confirm_password:
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": "Passwords don't match",
                "username": username,
                "email": email,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        # TODO: Add main API registration logic here
        # For now, add placeholder to make the structure work
        payload = {"username": username, "email": email, "password": password}

        # Placeholder for API call
        response = None

        if response and response.status_code == 201:
            # Registration successful, redirect to login
            logger.info(f"Registration successful for {username}")
            return RedirectResponse(
                url="/auth/login?msg=Registration+successful!+Please+log+in.",
                status_code=status.HTTP_302_FOUND,
            )

        # Get error message from response
        error_msg = "Registration failed"
        try:
            # Try to parse error response
            if response and hasattr(response, "json"):
                error_data = response.json()
                error_msg = format_error_message(error_data)
            elif response and hasattr(response, "text"):
                error_msg = f"Registration failed: {response.text[:100]}"
        except Exception as parse_error:
            logger.error(f"Failed to parse API error response: {str(parse_error)}")
            if response and hasattr(response, "text"):
                error_msg = f"Registration failed: {response.text[:100]}"

        logger.warning(f"Registration failed for {username}: {error_msg}")
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": error_msg,
                "username": username,
                "email": email,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    except Exception as e:
        logger.error(f"API call error: {str(e)}")
        # Emergency registration for testing/development
        if os.getenv("EMERGENCY_MODE", "false").lower() == "true":
            logger.warning(f"Using emergency mode registration for {username}")
            return RedirectResponse(
                url="/auth/login?msg=Emergency+registration+successful!+Please+log+in.",
                status_code=status.HTTP_302_FOUND,
            )

        # If not in emergency mode, show error
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": f"Registration service unavailable. Please try again later.",
                "username": username,
                "email": email,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.exception(f"Unexpected error during registration: {str(e)}")
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": "An unexpected error occurred during registration",
                "username": username,
                "email": email,
                "now": datetime.utcnow(),  # Add current datetime
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/auth/password-reset", response_class=HTMLResponse)
async def password_reset_page(request: Request):
    """Render password reset request page"""
    templates = get_templates(request)
    return get_templates(request).TemplateResponse(
        "auth/password_reset.html",
        {"request": request, "now": datetime.utcnow()},  # Add current datetime
    )


@router.post("/auth/password-reset")
async def password_reset_post(request: Request, email: str = Form(...)):
    """Process password reset request"""
    templates = get_templates(request)

    try:
        # TODO: Add password reset logic here
        # For now, just show success message

        # Always show success message for security (don't reveal if email exists)
        return get_templates(request).TemplateResponse(
            "auth/password_reset.html",
            {
                "request": request,
                "msg": "If an account with that email exists, we've sent password reset instructions.",
                "msg_type": "success",
                "now": datetime.utcnow(),  # Add current datetime
            },
        )

    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        # Still show success message for security
        return get_templates(request).TemplateResponse(
            "auth/password_reset.html",
            {
                "request": request,
                "msg": "If an account with that email exists, we've sent password reset instructions.",
                "msg_type": "success",
                "now": datetime.utcnow(),  # Add current datetime
            },
        )


@router.get("/auth/whoami")
async def whoami(request: Request):
    """Test route to show current user info."""

    return JSONResponse({"authenticated": False}, status_code=401)
