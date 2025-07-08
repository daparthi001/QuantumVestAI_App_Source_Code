"""
QuantumVestAI Settings Routes
Last Updated: 2025-07-07 21:44:54
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
from services.api_client import APIClient
from config.settings import settings
import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# API Configuration
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Router setup
router = APIRouter(prefix="/settings", tags=["settings"])

# Authentication dependency
def get_current_user(request: Request):
    """Get current user from session"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@router.get("/", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render user settings page"""
    try:
        # Check if user is authenticated
        user = request.session.get("user")
        if not user:
            # Demo mode - redirect to login with a message
            return RedirectResponse(url="/login?msg=Settings+require+authentication+(demo+mode)", status_code=302)
        
        # Demo user settings data
        user_settings = {
            "theme": user.get("theme", "dark"),
            "notification_enabled": user.get("notification_enabled", True),
            "email_notifications": user.get("email_notifications", True),
            "sms_notifications": user.get("sms_notifications", False),
            "push_notifications": user.get("push_notifications", True),
            "auto_logout": user.get("auto_logout", 30),  # minutes
            "two_factor_enabled": user.get("two_factor_enabled", False),
            "data_sharing": user.get("data_sharing", False),
            "marketing_emails": user.get("marketing_emails", True),
            "language": user.get("language", "en"),
            "timezone": user.get("timezone", "UTC"),
            "currency": user.get("currency", "USD"),
            "chart_type": user.get("chart_type", "candlestick"),
            "default_timeframe": user.get("default_timeframe", "1d"),
            "advanced_features": user.get("advanced_features", True),
            "api_access": user.get("api_access", False),
            "real_time_alerts": user.get("real_time_alerts", True)
        }
        
        # Available options
        available_options = {
            "themes": [
                {"value": "light", "name": "Light Theme"},
                {"value": "dark", "name": "Dark Theme"},
                {"value": "blue", "name": "Blue Theme"},
                {"value": "green", "name": "Green Theme"}
            ],
            "languages": [
                {"value": "en", "name": "English"},
                {"value": "es", "name": "Spanish"},
                {"value": "fr", "name": "French"},
                {"value": "de", "name": "German"},
                {"value": "zh", "name": "Chinese"}
            ],
            "timezones": [
                {"value": "UTC", "name": "UTC"},
                {"value": "America/New_York", "name": "Eastern Time"},
                {"value": "America/Los_Angeles", "name": "Pacific Time"},
                {"value": "Europe/London", "name": "London"},
                {"value": "Asia/Tokyo", "name": "Tokyo"},
                {"value": "Asia/Kolkata", "name": "India Standard Time"}
            ],
            "currencies": [
                {"value": "USD", "name": "US Dollar"},
                {"value": "EUR", "name": "Euro"},
                {"value": "GBP", "name": "British Pound"},
                {"value": "JPY", "name": "Japanese Yen"},
                {"value": "INR", "name": "Indian Rupee"}
            ],
            "chart_types": [
                {"value": "candlestick", "name": "Candlestick"},
                {"value": "line", "name": "Line Chart"},
                {"value": "area", "name": "Area Chart"},
                {"value": "ohlc", "name": "OHLC Bars"}
            ],
            "timeframes": [
                {"value": "1m", "name": "1 Minute"},
                {"value": "5m", "name": "5 Minutes"},
                {"value": "15m", "name": "15 Minutes"},
                {"value": "1h", "name": "1 Hour"},
                {"value": "1d", "name": "1 Day"},
                {"value": "1w", "name": "1 Week"}
            ]
        }
        
        return get_templates(request).TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": user,
                "settings": user_settings,
                "options": available_options,
                "page_title": "User Settings",
                "active_nav": "settings"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading settings page: {str(e)}")
        error_message = str(e)
        
        return get_templates(request).TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": None,
                "settings": {},
                "options": {"themes": [], "languages": [], "timezones": [], "currencies": []},
                "error": error_message,
                "page_title": "Settings Error"
            },
            status_code=500
        )

@router.post("/update", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    # Appearance Settings
    theme: str = Form(...),
    language: str = Form(...),
    timezone: str = Form(...),
    currency: str = Form(...),
    
    # Notification Settings
    notification_enabled: bool = Form(False),
    email_notifications: bool = Form(False),
    sms_notifications: bool = Form(False),
    push_notifications: bool = Form(False),
    marketing_emails: bool = Form(False),
    real_time_alerts: bool = Form(False),
    
    # Security Settings
    auto_logout: int = Form(30),
    two_factor_enabled: bool = Form(False),
    
    # Privacy Settings
    data_sharing: bool = Form(False),
    
    # Trading Settings
    chart_type: str = Form("candlestick"),
    default_timeframe: str = Form("1d"),
    advanced_features: bool = Form(False),
    api_access: bool = Form(False),
    
    current_user: dict = Depends(get_current_user)
):
    """Update user settings"""
    try:
        # Validate settings
        valid_themes = ["light", "dark", "blue", "green"]
        valid_languages = ["en", "es", "fr", "de", "zh"]
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "INR"]
        valid_chart_types = ["candlestick", "line", "area", "ohlc"]
        valid_timeframes = ["1m", "5m", "15m", "1h", "1d", "1w"]
        
        if theme not in valid_themes:
            raise HTTPException(status_code=400, detail="Invalid theme selection")
        if language not in valid_languages:
            raise HTTPException(status_code=400, detail="Invalid language selection")
        if currency not in valid_currencies:
            raise HTTPException(status_code=400, detail="Invalid currency selection")
        if chart_type not in valid_chart_types:
            raise HTTPException(status_code=400, detail="Invalid chart type selection")
        if default_timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail="Invalid timeframe selection")
        
        # Validate auto logout (between 5 and 120 minutes)
        if auto_logout < 5 or auto_logout > 120:
            raise HTTPException(status_code=400, detail="Auto logout must be between 5 and 120 minutes")
        
        # Update settings in session
        updated_settings = {
            "theme": theme,
            "language": language,
            "timezone": timezone,
            "currency": currency,
            "notification_enabled": notification_enabled,
            "email_notifications": email_notifications,
            "sms_notifications": sms_notifications,
            "push_notifications": push_notifications,
            "marketing_emails": marketing_emails,
            "real_time_alerts": real_time_alerts,
            "auto_logout": auto_logout,
            "two_factor_enabled": two_factor_enabled,
            "data_sharing": data_sharing,
            "chart_type": chart_type,
            "default_timeframe": default_timeframe,
            "advanced_features": advanced_features,
            "api_access": api_access
        }
        
        # Update user session with new settings
        for key, value in updated_settings.items():
            current_user[key] = value
        request.session["user"] = current_user
        
        # In demo mode, simulate successful update
        logger.info(f"Settings updated for user {current_user['id']}: {updated_settings}")
        
        # Get available options for template
        available_options = {
            "themes": [
                {"value": "light", "name": "Light Theme"},
                {"value": "dark", "name": "Dark Theme"},
                {"value": "blue", "name": "Blue Theme"},
                {"value": "green", "name": "Green Theme"}
            ],
            "languages": [
                {"value": "en", "name": "English"},
                {"value": "es", "name": "Spanish"},
                {"value": "fr", "name": "French"},
                {"value": "de", "name": "German"},
                {"value": "zh", "name": "Chinese"}
            ],
            "timezones": [
                {"value": "UTC", "name": "UTC"},
                {"value": "America/New_York", "name": "Eastern Time"},
                {"value": "America/Los_Angeles", "name": "Pacific Time"},
                {"value": "Europe/London", "name": "London"},
                {"value": "Asia/Tokyo", "name": "Tokyo"},
                {"value": "Asia/Kolkata", "name": "India Standard Time"}
            ],
            "currencies": [
                {"value": "USD", "name": "US Dollar"},
                {"value": "EUR", "name": "Euro"},
                {"value": "GBP", "name": "British Pound"},
                {"value": "JPY", "name": "Japanese Yen"},
                {"value": "INR", "name": "Indian Rupee"}
            ],
            "chart_types": [
                {"value": "candlestick", "name": "Candlestick"},
                {"value": "line", "name": "Line Chart"},
                {"value": "area", "name": "Area Chart"},
                {"value": "ohlc", "name": "OHLC Bars"}
            ],
            "timeframes": [
                {"value": "1m", "name": "1 Minute"},
                {"value": "5m", "name": "5 Minutes"},
                {"value": "15m", "name": "15 Minutes"},
                {"value": "1h", "name": "1 Hour"},
                {"value": "1d", "name": "1 Day"},
                {"value": "1w", "name": "1 Week"}
            ]
        }
        
        return get_templates(request).TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": current_user,
                "settings": updated_settings,
                "options": available_options,
                "success": "Settings updated successfully!",
                "page_title": "User Settings",
                "active_nav": "settings"
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        error_message = str(e)
        
        # Get current settings for error response
        current_settings = {
            "theme": current_user.get("theme", "dark"),
            "language": current_user.get("language", "en"),
            "timezone": current_user.get("timezone", "UTC"),
            "currency": current_user.get("currency", "USD"),
            "notification_enabled": current_user.get("notification_enabled", True),
            "email_notifications": current_user.get("email_notifications", True),
            "sms_notifications": current_user.get("sms_notifications", False),
            "push_notifications": current_user.get("push_notifications", True),
            "auto_logout": current_user.get("auto_logout", 30),
            "two_factor_enabled": current_user.get("two_factor_enabled", False),
            "data_sharing": current_user.get("data_sharing", False),
            "marketing_emails": current_user.get("marketing_emails", True),
            "chart_type": current_user.get("chart_type", "candlestick"),
            "default_timeframe": current_user.get("default_timeframe", "1d"),
            "advanced_features": current_user.get("advanced_features", True),
            "api_access": current_user.get("api_access", False),
            "real_time_alerts": current_user.get("real_time_alerts", True)
        }
        
        # Get available options for error response
        available_options = {
            "themes": [
                {"value": "light", "name": "Light Theme"},
                {"value": "dark", "name": "Dark Theme"},
                {"value": "blue", "name": "Blue Theme"},
                {"value": "green", "name": "Green Theme"}
            ],
            "languages": [{"value": "en", "name": "English"}],
            "timezones": [{"value": "UTC", "name": "UTC"}],
            "currencies": [{"value": "USD", "name": "US Dollar"}],
            "chart_types": [{"value": "candlestick", "name": "Candlestick"}],
            "timeframes": [{"value": "1d", "name": "1 Day"}]
        }
        
        return get_templates(request).TemplateResponse(
            "settings.html",
            {
                "request": request,
                "user": current_user,
                "settings": current_settings,
                "options": available_options,
                "error": f"Error updating settings: {error_message}",
                "page_title": "User Settings"
            },
            status_code=500
        )

@router.post("/reset")
async def reset_settings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Reset settings to default values"""
    try:
        # Default settings
        default_settings = {
            "theme": "dark",
            "language": "en",
            "timezone": "UTC",
            "currency": "USD",
            "notification_enabled": True,
            "email_notifications": True,
            "sms_notifications": False,
            "push_notifications": True,
            "marketing_emails": True,
            "real_time_alerts": True,
            "auto_logout": 30,
            "two_factor_enabled": False,
            "data_sharing": False,
            "chart_type": "candlestick",
            "default_timeframe": "1d",
            "advanced_features": True,
            "api_access": False
        }
        
        # Update user session with default settings
        for key, value in default_settings.items():
            current_user[key] = value
        request.session["user"] = current_user
        
        logger.info(f"Settings reset to defaults for user {current_user['id']}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Settings reset to default values successfully",
                "settings": default_settings
            }
        )
        
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Error resetting settings: {str(e)}"},
            status_code=500
        )

@router.get("/export")
async def export_settings(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Export user settings as JSON"""
    try:
        # Get current user settings
        user_settings = {
            "theme": current_user.get("theme", "dark"),
            "language": current_user.get("language", "en"),
            "timezone": current_user.get("timezone", "UTC"),
            "currency": current_user.get("currency", "USD"),
            "notification_enabled": current_user.get("notification_enabled", True),
            "email_notifications": current_user.get("email_notifications", True),
            "sms_notifications": current_user.get("sms_notifications", False),
            "push_notifications": current_user.get("push_notifications", True),
            "marketing_emails": current_user.get("marketing_emails", True),
            "real_time_alerts": current_user.get("real_time_alerts", True),
            "auto_logout": current_user.get("auto_logout", 30),
            "two_factor_enabled": current_user.get("two_factor_enabled", False),
            "data_sharing": current_user.get("data_sharing", False),
            "chart_type": current_user.get("chart_type", "candlestick"),
            "default_timeframe": current_user.get("default_timeframe", "1d"),
            "advanced_features": current_user.get("advanced_features", True),
            "api_access": current_user.get("api_access", False)
        }
        
        return JSONResponse(
            content={
                "success": True,
                "settings": user_settings,
                "exported_at": "2025-07-07T21:44:54Z",
                "user_id": current_user["id"]
            },
            headers={
                "Content-Disposition": f"attachment; filename=quantumvestai_settings_{current_user['id']}.json"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting settings: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Error exporting settings: {str(e)}"},
            status_code=500
        )

@router.post("/import")
async def import_settings(
    request: Request,
    settings_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Import user settings from JSON"""
    try:
        # Validate imported settings
        valid_keys = {
            "theme", "language", "timezone", "currency", "notification_enabled",
            "email_notifications", "sms_notifications", "push_notifications",
            "marketing_emails", "real_time_alerts", "auto_logout", "two_factor_enabled",
            "data_sharing", "chart_type", "default_timeframe", "advanced_features", "api_access"
        }
        
        # Filter and validate settings
        imported_settings = {}
        for key, value in settings_data.items():
            if key in valid_keys:
                imported_settings[key] = value
        
        # Update user session
        for key, value in imported_settings.items():
            current_user[key] = value
        request.session["user"] = current_user
        
        logger.info(f"Settings imported for user {current_user['id']}: {imported_settings}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Settings imported successfully",
                "imported_settings": imported_settings
            }
        )
        
    except Exception as e:
        logger.error(f"Error importing settings: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Error importing settings: {str(e)}"},
            status_code=500
        )

# Health check endpoint
@router.get("/health")
async def settings_health_check():
    """Settings service health check"""
    return {
        "status": "healthy",
        "service": "settings",
        "timestamp": "2025-07-07T21:44:54Z"
    }