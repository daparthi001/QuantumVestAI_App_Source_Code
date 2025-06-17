"""
Profile Controller for QuantumVestAI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import aiohttp
import logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from auth.dependencies import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path("/app/templates")))
logger = logging.getLogger("quantumvestai.profile_controller")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user: dict = Depends(get_current_user)):
    """Display user profile page"""
    try:
        profile_data = {
            "user": user
        }
        
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            # Get full user profile
            async with session.get(
                f"{API_V1_URL}/users/{user['username']}",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    user_details = await response.json()
                    profile_data["details"] = user_details
                else:
                    profile_data["details"] = user
            
            # Get user activity
            async with session.get(
                f"{API_V1_URL}/users/{user['username']}/activity",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    profile_data["activity"] = await response.json()
                else:
                    profile_data["activity"] = []
            
            # Get notification settings
            async with session.get(
                f"{API_V1_URL}/users/{user['username']}/notifications/settings",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    profile_data["notification_settings"] = await response.json()
                else:
                    profile_data["notification_settings"] = {"email": True, "push": False}
        
        return templates.TemplateResponse(
            "profile/index.html",
            {"request": request, "profile": profile_data}
        )
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, user: dict = Depends(get_current_user)):
    """Display user settings page"""
    try:
        settings_data = {
            "user": user
        }
        
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        async with aiohttp.ClientSession() as session:
            # Get user settings
            async with session.get(
                f"{API_V1_URL}/users/{user['username']}/settings",
                headers=headers,
                timeout=5
            ) as response:
                if response.status == 200:
                    settings_data["user_settings"] = await response.json()
                else:
                    settings_data["user_settings"] = {}
        
        return templates.TemplateResponse(
            "profile/settings.html",
            {"request": request, "settings": settings_data}
        )
    except Exception as e:
        logger.error(f"Settings error: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@router.post("/profile/update")
async def update_profile(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    bio: str = Form(""),
    avatar: UploadFile = File(None),
    user: dict = Depends(get_current_user)
):
    """Update user profile information"""
    try:
        headers = {"Authorization": f"Bearer {user.get('token', '')}"}
        
        # Prepare profile data
        profile_data = {
            "username": user["username"],
            "full_name": full_name,
            "email": email,
            "bio": bio
        }
        
        async with aiohttp.ClientSession() as session:
            # Update basic profile data
            async with session.put(
                f"{API_V1_URL}/users/{user['username']}",
                json=profile_data,
                headers=headers,
                timeout=5
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to update profile: {error_text}"
                    )
            
            # Upload avatar if provided
            if avatar and avatar.filename:
                form_data = aiohttp.FormData()
                form_data.add_field(
                    'avatar',
                    await avatar.read(),
                    filename=avatar.filename,
                    content_type=avatar.content_type
                )
                
                async with session.post(
                    f"{API_V1_URL}/users/{user['username']}/avatar",
                    data=form_data,
                    headers=headers,
                    timeout=10
                ) as avatar_response:
                    if avatar_response.status != 200:
                        logger.warning(f"Failed to upload avatar: {avatar_response.status}")
        
        return RedirectResponse(url="/profile?msg=Profile+updated+successfully", status_code=303)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))