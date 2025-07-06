from fastapi import APIRouter, Request, Form, HTTPException
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
async def settings_page(request: Request):
    """Render user settings page (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Settings+require+authentication+(demo+mode)", status_code=302)

@router.post("/update", response_class=HTMLResponse)
async def update_settings(request: Request):
    """Update settings (demo mode)"""
    
    # Demo mode - redirect to login with a message
    return RedirectResponse(url="/login?msg=Settings+updates+require+authentication+(demo+mode)", status_code=302)
=======
async def settings_page(
    request: Request,
    request: Request
):
    """Render user settings page"""
    
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
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
    
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
        
        # Get available themes
        themes = []
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
