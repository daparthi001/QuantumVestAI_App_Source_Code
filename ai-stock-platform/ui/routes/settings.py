from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from services.api_client import APIClient
from config.settings import settings

API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["settings"])

@router.get("/", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_
):
    """Render user settings page"""
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Get user's current settings
        user_settings = api_client.get("/api/users/settings")
        
        # Get available themes
        themes = api_client.get("/api/users/themes")
        
        return templates.TemplateResponse(
            "settings.html", 
            {
                "request": request,
                "user": None,
                "settings": user_settings,
                "themes": themes
            }
        )
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return templates.TemplateResponse(
            "settings.html", 
            {
                "request": request,
                "user": None,
                "settings": {},
                "themes": [],
                "error": error_message
            }
        )

@router.post("/update", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    current_request: Request,
    theme: str = Form(...),
    notification_enabled: bool = Form(False),
    email_notifications: bool = Form(False)
):
    """Update user settings"""
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Update user settings
        api_client.put(
            "/api/users/settings",
            data={
                "theme": theme,
                "notification_enabled": notification_enabled,
                "email_notifications": email_notifications
            }
        )
        
        # Redirect to settings page with success message
        return RedirectResponse(url="/settings?updated=true", status_code=303)
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
        
        # Get available themes
        themes = []
        try:
            api_client = APIClient(token=request.cookies.get("token"))
            themes = api_client.get("/api/users/themes")
        except:
            pass
            
        return templates.TemplateResponse(
            "settings.html", 
            {
                "request": request,
                "user": None,
                "settings": {
                    "theme": theme,
                    "notification_enabled": notification_enabled,
                    "email_notifications": email_notifications
                },
                "themes": themes,
                "error": error_message
            }
        )