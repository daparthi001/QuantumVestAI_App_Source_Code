from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from services.api_client import APIClient
from config.settings import settings
import os
import shutil
from pathlib import Path
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["profile"])

@router.get("/", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    request: Request
):
    """Render user profile page"""
    
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": None,
                "profile": {},
                "activity": [],
                "error": error_message
            }
        )

@router.post("/update", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    current_request: Request,
    full_name: str = Form(None),
    bio: str = Form(None),
    location: str = Form(None),
    profile_image: UploadFile = File(None)
):
    """Update user profile"""
    
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        # Try to get current profile data
        profile_data = {}
        activity_data = []
            pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": None,
                "profile": profile_data,
                "activity": activity_data,
                "error": error_message
            }
        )

@router.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password"""
    
    # Check if passwords match
    if new_password != confirm_password:
        # Try to get current profile data
        profile_data = {}
        activity_data = []
            pass
            
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": None,
                "profile": profile_data,
                "activity": activity_data,
                "error": "New passwords do not match"
            }
        )
    
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        # Try to get current profile data
        profile_data = {}
        activity_data = []
            pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": None,
                "profile": profile_data,
                "activity": activity_data,
                "error": f"Error changing password: {error_message}"
            }
        )