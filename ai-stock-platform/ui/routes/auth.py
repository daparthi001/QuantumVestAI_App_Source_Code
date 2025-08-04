"""
QuantumVestAI Authentication Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient

# Setup router
router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Demo user database removed
DEMO_USERS = {}

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = None, next: str = None):
    """Display login page"""
    try:
        # Check if already authenticated
        auth_cookie = request.cookies.get("access_token")
        if auth_cookie:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        
        return get_templates(request).TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": msg,
                "next": next,
                "page_title": "Login - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering login page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_login_html(msg),
            status_code=500
        )

@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember: bool = Form(False),
    next: Optional[str] = Form(None)
):
    """Handle login form submission"""
    try:
        logger.info(f"Login attempt for username: {username}")
        
        # Validate input
        if not username or len(username.strip()) < 2:
            raise ValueError("Username must be at least 2 characters long")
        
        if not password or len(password) < 3:
            raise ValueError("Password must be at least 3 characters long")
        
        username = username.strip().lower()
        
        # Authenticate against the main API
        api = APIClient()
        try:
            api_response = api.post_form(
                "/auth/login",
                data={"username": username, "password": password}
            )
        except Exception as api_exc:
            logger.error(f"API login failed: {api_exc}")
            raise ValueError("Invalid username or password")

        token = api_response.get("data", {}).get("access_token")
        if not token:
            raise ValueError(api_response.get("message", "Login failed"))

        # Fetch user info
        user_info = {}
        try:
            user_api = APIClient(token)
            me_resp = user_api.get("/auth/me")
            user_info = me_resp.get("data", {})
        except Exception:
            logger.warning("Failed to fetch user info after login")

        # Determine redirect URL
        redirect_url = next if next and next.startswith('/') else "/dashboard"

        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)

        max_age = 7 * 24 * 60 * 60 if remember else None
        response.set_cookie(
            key="access_token",
            value=f"Bearer {token}",
            httponly=True,
            max_age=max_age,
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        # Additional non-HTTP-only cookie so the SPA can sync the token
        response.set_cookie(
            key="qvai_token",
            value=token,
            max_age=max_age,
            samesite="lax",
            secure=request.url.scheme == "https"
        )

        if user_info:
            response.set_cookie(
                key="user_info",
                value=f"{user_info.get('username', username)}|{user_info.get('role', '')}|{user_info.get('full_name', '')}",
                max_age=max_age,
                samesite="lax",
                secure=request.url.scheme == "https"
            )

        return response
        
    except ValueError as e:
        logger.warning(f"Login validation failed: {str(e)}")
        return get_templates(request).TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "next": next,
                "page_title": "Login - QuantumVestAI"
            },
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return get_templates(request).TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "msg": "Login failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "username": username,
                "next": next,
                "page_title": "Login - QuantumVestAI"
            },
            status_code=500
        )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, msg: str = None):
    """Display registration page"""
    try:
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": msg,
                "page_title": "Register - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering register page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_register_html(msg),
            status_code=500
        )

@router.post("/register")
async def register_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    full_name: str = Form(...),
    terms: bool = Form(False)
):
    """Handle registration form submission (production)"""
    try:
        logger.info(f"Registration attempt for username: {username}")
        
        # Validate input
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not email or "@" not in email:
            raise ValueError("Please enter a valid email address")
        
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        if password != confirm_password:
            raise ValueError("Passwords do not match")
        
        if not full_name or len(full_name.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")

        if not terms:
            raise ValueError("You must accept the Terms of Service")
        
        username = username.strip().lower()
        api = APIClient()
        try:
            api_response = api.post(
                "/auth/register",
                data={
                    "username": username,
                    "email": email,
                    "password": password,
                    "confirm_password": confirm_password,
                    "full_name": full_name,
                    "terms_accepted": terms,
                },
            )
            # Check for API error
            if api_response.get("status") != "success":
                msg = api_response.get("message") or "Registration failed."
                raise ValueError(msg)
        except Exception as api_exc:
            logger.error(f"API registration failed: {api_exc}")
            raise ValueError(str(api_exc))
        # Success: redirect to login with message
        return RedirectResponse(
            url="/auth/login?msg=Registration+successful!+Please+log+in.",
            status_code=status.HTTP_302_FOUND
        )
    except ValueError as e:
        logger.warning(f"Registration validation failed: {str(e)}")
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "username": username,
                "email": email,
                "full_name": full_name,
                "terms": terms,
                "page_title": "Register - QuantumVestAI",
            },
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return get_templates(request).TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "msg": "Registration failed due to a technical error. Please try again.",
                "msg_type": "danger",
                "terms": terms,
                "page_title": "Register - QuantumVestAI"
            },
            status_code=500
        )

@router.post("/logout")
@router.get("/logout")
async def logout(request: Request):
    """Handle user logout"""
    try:
        logger.info("User logout")
        
        response = RedirectResponse(url="/auth/login?msg=Successfully logged out", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("access_token")
        response.delete_cookie("user_info")
        response.delete_cookie("qvai_token")
        
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.get("/test-auth-sync", response_class=HTMLResponse)
async def test_auth_sync_page(request: Request):
    """Test page for cross-tab authentication synchronization"""
    try:
        return get_templates(request).TemplateResponse(
            "auth-sync-test.html",
            {
                "request": request,
                "page_title": "Auth Sync Test - QuantumVestAI"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering auth sync test page: {str(e)}")
        return HTMLResponse(
            content="<h1>Error loading auth sync test page</h1>",
            status_code=500
        )

@router.get("/test-login", response_class=HTMLResponse)
async def test_login_page(request: Request):
    """Test page for login functionality"""
    try:
        return HTMLResponse(content=open('/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/ui/static/js/test-login.html').read())
    except Exception as e:
        logger.error(f"Error rendering login test page: {str(e)}")
        return HTMLResponse(
            content="<h1>Error loading login test page</h1>",
            status_code=500
        )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return RedirectResponse(url="/auth/login?msg=Please log in to view your profile", status_code=status.HTTP_302_FOUND)
        
        # Get user info from cookie (in production, decode JWT)
        user_cookie = request.cookies.get("user_info", "")
        if user_cookie:
            parts = user_cookie.split("|")
            if len(parts) >= 3:
                username, role, full_name = parts[0], parts[1], parts[2]
                user_data = DEMO_USERS.get(username, {})
                user_data.update({
                    "username": username,
                    "role": role,
                    "full_name": full_name
                })
            else:
                user_data = {"username": "demo", "role": "user", "full_name": "Demo User"}
        else:
            user_data = {"username": "demo", "role": "user", "full_name": "Demo User"}
        
        return get_templates(request).TemplateResponse(
            "auth/profile.html",
            {
                "request": request,
                "user": user_data,
                "page_title": "Profile - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading profile page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_profile_html(),
            status_code=500
        )

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request, msg: str = None):
    """Forgot password page"""
    try:
        return get_templates(request).TemplateResponse(
            "auth/forgot_password.html",
            {
                "request": request,
                "msg": msg,
                "page_title": "Forgot Password - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering forgot password page: {str(e)}")
        return HTMLResponse(
            content=create_fallback_forgot_password_html(),
            status_code=500
        )

@router.post("/forgot-password")
async def forgot_password_post(request: Request, email: str = Form(...)):
    """Handle forgot password form submission."""
    try:
        logger.info(f"Password reset request for email: {email}")
        
        if not email or "@" not in email:
            raise ValueError("Please enter a valid email address")
        
        # Show success message without sending email
        return get_templates(request).TemplateResponse(
            "auth/forgot_password.html",
            {
                "request": request,
                "msg": "Password reset instructions have been sent to your email (no actual email sent)",
                "msg_type": "success",
                "page_title": "Forgot Password - QuantumVestAI"
            }
        )
        
    except ValueError as e:
        return get_templates(request).TemplateResponse(
            "auth/forgot_password.html",
            {
                "request": request,
                "msg": str(e),
                "msg_type": "danger",
                "email": email,
                "page_title": "Forgot Password - QuantumVestAI"
            },
            status_code=400
        )

@router.get("/api/user")
async def get_current_user_api(request: Request):
    """API endpoint to get current user info"""
    try:
        # Check authentication
        auth_cookie = request.cookies.get("access_token")
        if not auth_cookie:
            return JSONResponse({
                "status": "error",
                "message": "Not authenticated"
            }, status_code=401)
        
        # Get user info from cookie
        user_cookie = request.cookies.get("user_info", "")
        if user_cookie:
            parts = user_cookie.split("|")
            if len(parts) >= 3:
                username, role, full_name = parts[0], parts[1], parts[2]
                user_data = DEMO_USERS.get(username, {})
                return JSONResponse({
                    "status": "success",
                    "user": {
                        "username": username,
                        "role": role,
                        "full_name": full_name,
                        "email": user_data.get("email", ""),
                        "features": user_data.get("features", []),
                        "is_authenticated": True
                    }
                })
        
        return JSONResponse({
            "status": "error",
            "message": "User data not found"
        }, status_code=404)
        
    except Exception as e:
        logger.error(f"Error getting user API: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

# Utility functions for fallback HTML
def create_fallback_login_html(msg=None):
    """Create fallback login HTML"""
    msg_html = f'<div class="alert alert-warning">{msg}</div>' if msg else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - QuantumVestAI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title text-center">Login to QuantumVestAI</h2>
                            {msg_html}
                            <form method="post" action="/auth/login">
                                <div class="mb-3">
                                    <label for="username" class="form-label">Username</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                    <small class="form-text text-muted">Demo accounts: demo, admin, test, user</small>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                    <small class="form-text text-muted">Use same as username (demo/demo, admin/admin, etc.)</small>
                                </div>
                                <div class="mb-3 form-check">
                                    <input type="checkbox" class="form-check-input" id="remember" name="remember">
                                    <label class="form-check-label" for="remember">Remember me</label>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                            <div class="text-center mt-3">
                                <a href="/auth/forgot-password">Forgot Password?</a> |
                                <a href="/auth/register">Create Account</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def create_fallback_register_html(msg=None):
    """Create fallback register HTML"""
    msg_html = f'<div class="alert alert-warning">{msg}</div>' if msg else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - QuantumVestAI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title text-center">Create Account</h2>
                            {msg_html}
                            <p class="text-center text-muted">Demo Mode - Use existing accounts to login</p>
                            <div class="text-center">
                                <a href="/auth/login" class="btn btn-primary">Back to Login</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def create_fallback_profile_html():
    """Create fallback profile HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile - QuantumVestAI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title">User Profile</h2>
                            <p>Profile page temporarily unavailable.</p>
                            <a href="/dashboard" class="btn btn-primary">Back to Dashboard</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def create_fallback_forgot_password_html():
    """Create fallback forgot password HTML"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forgot Password - QuantumVestAI</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h2 class="card-title text-center">Reset Password</h2>
                            <p class="text-center text-muted">Demo Mode - Use demo accounts to login</p>
                            <div class="text-center">
                                <a href="/auth/login" class="btn btn-primary">Back to Login</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
