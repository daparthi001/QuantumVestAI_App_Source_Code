"""
QuantumVestAI Profile Controller
Last Updated: 2025-06-18 21:25:28
Author: daparthi001
"""
import logging
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
from services.api_client import APIClient
from core.config.settings import settings
API_URL = "http://quantumvestai-dev-api:8000/api/v1"
# Setup router and templates
router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger(__name__)

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Display user profile page"""
    return RedirectResponse(url="/login?next=/profile", status_code=302)
    except Exception as e:
        logger.error(f"Error loading profile page: {str(e)}")
        return templates.TemplateResponse(
            "profile/index.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load profile data"
            },
            status_code=500
        )

@router.get("/profile/settings", response_class=HTMLResponse)
async def profile_settings(request: Request):
    """Display user profile settings page"""
    return RedirectResponse(url="/login?next=/profile/settings", status_code=302)

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get user preferences
        preferences = api_client.get("/users/me/preferences")
        
        # Get user notification settings
        notifications = api_client.get("/users/me/notifications/settings")
        
        # Get user's features
        features = api_client.get_available_features()
        
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "preferences": preferences,
                "notifications": notifications,
                "features": features,
                "has_advanced_features": any(features.get("features", {}).get("advanced", {}).values())
            }
        )
    except Exception as e:
        logger.error(f"Error loading profile settings: {str(e)}")
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load settings"
            },
            status_code=500
        )

@router.post("/profile/update")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    bio: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None)
):
    """Update user profile information"""
    return RedirectResponse(url="/login", status_code=302)

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Prepare update data
        update_data = {
            "full_name": full_name,
            "bio": bio
        }
        
        # Handle profile image if provided
        if profile_image and profile_image.filename:
            # Implementation would depend on how file uploads are handled
            # This is a placeholder for the actual implementation
            pass
            
        # Update profile via API
        api_client.put("/users/me/profile", data=update_data)
        
        # Redirect with success message
        return RedirectResponse(url="/profile?updated=true", status_code=302)
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return templates.TemplateResponse(
            "profile/index.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to update profile"
            },
            status_code=500
        )

@router.post("/profile/update-preferences")
async def update_preferences(
    request: Request,
    theme: str = Form(...),
    language: str = Form(...),
    timezone: str = Form(...),
    dashboard_view: str = Form(...)
):
    """Update user preferences"""
    return RedirectResponse(url="/login", status_code=302)

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Prepare preferences data
        preferences_data = {
            "theme": theme,
            "language": language,
            "timezone": timezone,
            "dashboard_view": dashboard_view
        }
        
        # Update preferences via API
        api_client.put("/users/me/preferences", data=preferences_data)
        
        # Redirect with success message
        return RedirectResponse(url="/profile/settings?preferences_updated=true", status_code=302)
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to update preferences"
            },
            status_code=500
        )

@router.post("/profile/update-notifications")
async def update_notifications(
    request: Request,
    
):
    """Update user notification settings"""

    try:
        # Parse form data
        form_data = await request.form()
        notification_settings = {}
        
        # Extract notification preferences from form
        for key, value in form_data.items():
            if key.startswith("notification_"):
                setting_name = key.replace("notification_", "")
                notification_settings[setting_name] = value == "on"
        
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update notification settings via API
        api_client.put("/users/me/notifications/settings", data=notification_settings)
        
        # Redirect with success message
        return RedirectResponse(url="/profile/settings?notifications_updated=true", status_code=302)
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to update notification settings"
            },
            status_code=500
        )

@router.post("/profile/change-password")
async def change_password(
    request: Request,
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password"""

    # Verify passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "error": "New passwords don't match"
            },
            status_code=400
        )

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update password via API
        api_client.put("/users/me/password", data={
            "current_password": current_password,
            "new_password": new_password
        })
        
        # Redirect with success message
        return RedirectResponse(url="/profile/settings?password_changed=true", status_code=302)
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        
        error_message = "Failed to change password"
        if "current password is incorrect" in str(e).lower():
            error_message = "Current password is incorrect"
            
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "error": error_message
            },
            status_code=400
        )

@router.post("/activate-advanced-features")
async def activate_advanced_features(
    request: Request,
    
):
    """Activate advanced features for the current user"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Enable advanced features via API
        response = api_client.enable_advanced_features()
        
        # Log the activation
        logger.info(f"Advanced features activated for user {"anonymous"
        
        # Redirect to dashboard with success message
        return RedirectResponse(
            url="/dashboard?features_activated=true",
            status_code=302
        )
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to activate advanced features: {error_message}")
        
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        # Return to profile page with error
        return templates.TemplateResponse(
            "profile/settings.html",
            {
                "request": request,
                "user": None,
                "error": f"Failed to activate advanced features: {error_message}"
            },
            status_code=500
        )

@router.get("/advanced-features", response_class=HTMLResponse)
async def advanced_features_page(
    request: Request,
    
):
    """Display advanced features page"""

    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get user's features
        features = api_client.get_available_features()
        
        # Check if user has access to advanced features
        advanced_access = any(features.get("features", {}).get("advanced", {}).values())
        
        if not advanced_access:
            # If no access, redirect to upgrade page
            return RedirectResponse(url="/profile/upgrade?required=advanced", status_code=302)
        
        # Get available advanced features
        advanced_features = api_client.get("/features/advanced")
        
        return templates.TemplateResponse(
            "features/advanced.html",
            {
                "request": request,
                "user": None,
                "features": advanced_features
            }
        )
    except Exception as e:
        logger.error(f"Error loading advanced features page: {str(e)}")
        return templates.TemplateResponse(
            "features/advanced.html",
            {
                "request": request,
                "user": None,
                "error": "Failed to load advanced features"
            },
            status_code=500
        )