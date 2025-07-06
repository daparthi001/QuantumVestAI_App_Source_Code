from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from routes.auth import get_current_user
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
    current_user: dict = Depends(get_current_user)
):
    """Render user profile page"""
    if not current_user:
        return RedirectResponse(url="/login?next=/profile", status_code=302)
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Get user profile
        profile_data = api_client.get("/api/users/profile")
        
        # Get user activity
        activity_data = api_client.get("/api/users/activity")
        
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": activity_data
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
            "profile.html", 
            {
                "request": request,
                "user": current_user,
                "profile": {},
                "activity": [],
                "error": error_message
            }
        )

@router.post("/update", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
    full_name: str = Form(None),
    bio: str = Form(None),
    location: str = Form(None),
    profile_image: UploadFile = File(None)
):
    """Update user profile"""
    if not current_user:
        return RedirectResponse(url="/login?next=/profile", status_code=302)
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Prepare update data
        update_data = {
            "full_name": full_name,
            "bio": bio,
            "location": location
        }
        
        # Handle profile image upload
        if profile_image and profile_image.filename:
            # Create uploads directory if it doesn't exist
            upload_dir = Path("static/uploads/profile_images")
            upload_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate filename based on username
            file_extension = os.path.splitext(profile_image.filename)[1]
            username = current_user.get("username", "user")
            filename = f"{username}{file_extension}"
            file_path = upload_dir / filename
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(profile_image.file, buffer)
                
            # Add profile image path to update data
            update_data["profile_image"] = f"/static/uploads/profile_images/{filename}"
        
        # Update profile
        api_client.put("/api/users/profile", data=update_data)
        
        # Redirect back to profile page
        return RedirectResponse(url="/profile?updated=true", status_code=303)
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        # Try to get current profile data
        profile_data = {}
        activity_data = []
        try:
            api_client = APIClient(token=request.cookies.get("token"))
            profile_data = api_client.get("/api/users/profile")
            activity_data = api_client.get("/api/users/activity")
        except:
            pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": activity_data,
                "error": error_message
            }
        )

@router.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_user: dict = Depends(get_current_user),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password"""
    if not current_user:
        return RedirectResponse(url="/login?next=/profile", status_code=302)
    
    # Check if passwords match
    if new_password != confirm_password:
        # Try to get current profile data
        profile_data = {}
        activity_data = []
        try:
            api_client = APIClient(token=request.cookies.get("token"))
            profile_data = api_client.get("/api/users/profile")
            activity_data = api_client.get("/api/users/activity")
        except:
            pass
            
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": activity_data,
                "error": "New passwords do not match"
            }
        )
    
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Change password
        api_client.put(
            "/api/users/change-password",
            data={
                "current_password": current_password,
                "new_password": new_password
            }
        )
        
        # Redirect back to profile page
        return RedirectResponse(url="/profile?password_changed=true", status_code=303)
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        # Try to get current profile data
        profile_data = {}
        activity_data = []
        try:
            api_client = APIClient(token=request.cookies.get("token"))
            profile_data = api_client.get("/api/users/profile")
            activity_data = api_client.get("/api/users/activity")
        except:
            pass
                
        return templates.TemplateResponse(
            "profile.html", 
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": activity_data,
                "error": f"Error changing password: {error_message}"
            }
        )