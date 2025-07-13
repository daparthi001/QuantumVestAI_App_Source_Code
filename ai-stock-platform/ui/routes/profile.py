"""
QuantumVestAI Profile Routes
Last Updated: 2025-07-07 21:42:27
Author: hemanth9398
"""
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import settings
from fastapi import (APIRouter, Depends, File, Form, HTTPException, Request,
                     UploadFile)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient

# Setup logging
logger = logging.getLogger(__name__)

# API Configuration
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

# Router setup
router = APIRouter(prefix="/profile", tags=["profile"])

# Authentication dependency (demo mode)
def get_current_user(request: Request):
    """Get current user from session (demo mode)"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@router.get("/", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Render user profile page"""
    try:
        # Check if user is authenticated
        user = request.session.get("user")
        if not user:
            # Demo mode - redirect to login with a message
            return RedirectResponse(url="/login?msg=Profile+requires+authentication+(demo+mode)", status_code=302)
        
        # Demo profile data
        profile_data = {
            "user_id": user.get("id", "demo_user_001"),
            "username": user.get("username", "hemanth9398"),
            "email": user.get("email", "hemanth9398@example.com"),
            "full_name": user.get("full_name", "Hemanth Kumar"),
            "bio": user.get("bio", "Software Developer and AI Enthusiast passionate about quantitative finance and machine learning."),
            "location": user.get("location", "Hyderabad, India"),
            "profile_image": user.get("profile_image", "/static/img/avatars/default.png"),
            "join_date": user.get("join_date", "2025-01-15"),
            "last_login": user.get("last_login", "2025-07-07T21:35:00Z"),
            "subscription_type": user.get("subscription_type", "Premium"),
            "total_predictions": user.get("total_predictions", 156),
            "portfolio_value": user.get("portfolio_value", 125000.50),
            "accuracy_rate": user.get("accuracy_rate", 0.847)
        }
        
        # Demo activity data
        activity_data = [
            {
                "timestamp": "2025-07-07T21:35:00Z",
                "action": "Stock Prediction",
                "details": "Predicted AAPL to reach $195.25",
                "type": "prediction"
            },
            {
                "timestamp": "2025-07-07T20:15:00Z", 
                "action": "Portfolio Update",
                "details": "Updated portfolio value to $125,000.50",
                "type": "portfolio"
            },
            {
                "timestamp": "2025-07-07T19:45:00Z",
                "action": "Watchlist Added",
                "details": "Added MSFT to watchlist",
                "type": "watchlist"
            },
            {
                "timestamp": "2025-07-07T18:30:00Z",
                "action": "Profile Updated",
                "details": "Updated bio information",
                "type": "profile"
            }
        ]
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "profile": profile_data,
                "activity": activity_data,
                "page_title": "User Profile",
                "active_nav": "profile"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading profile page: {str(e)}")
        error_message = str(e)
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": None,
                "profile": {},
                "activity": [],
                "error": error_message,
                "page_title": "Profile Error"
            },
            status_code=500
        )

@router.post("/update", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    full_name: str = Form(None),
    bio: str = Form(None),
    location: str = Form(None),
    profile_image: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Validate and process profile image upload
        profile_image_path = None
        if profile_image and profile_image.filename:
            # Validate file type
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            file_extension = Path(profile_image.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, and GIF are allowed.")
            
            # Create upload directory if it doesn't exist
            upload_dir = Path("static/uploads/profiles")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{current_user['id']}_{timestamp}{file_extension}"
            profile_image_path = upload_dir / filename
            
            # Save uploaded file
            with open(profile_image_path, "wb") as buffer:
                shutil.copyfileobj(profile_image.file, buffer)
            
            # Update path for web access
            profile_image_path = f"/static/uploads/profiles/{filename}"
        
        # Prepare update data
        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name.strip()
        if bio is not None:
            update_data["bio"] = bio.strip()
        if location is not None:
            update_data["location"] = location.strip()
        if profile_image_path:
            update_data["profile_image"] = profile_image_path
        
        # In demo mode, simulate successful update
        logger.info(f"Profile updated for user {current_user['id']}: {update_data}")
        
        # Update session data
        for key, value in update_data.items():
            current_user[key] = value
        request.session["user"] = current_user
        
        # Get updated profile data
        profile_data = {
            "user_id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name", ""),
            "bio": current_user.get("bio", ""),
            "location": current_user.get("location", ""),
            "profile_image": current_user.get("profile_image", "/static/img/avatars/default.png"),
            "join_date": current_user.get("join_date", "2025-01-15"),
            "last_login": current_user.get("last_login", "2025-07-07T21:35:00Z"),
            "subscription_type": current_user.get("subscription_type", "Premium"),
            "total_predictions": current_user.get("total_predictions", 156),
            "portfolio_value": current_user.get("portfolio_value", 125000.50),
            "accuracy_rate": current_user.get("accuracy_rate", 0.847)
        }
        
        # Demo activity data with new update entry
        activity_data = [
            {
                "timestamp": datetime.now().isoformat() + "Z",
                "action": "Profile Updated",
                "details": f"Updated profile information",
                "type": "profile"
            }
        ]
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": activity_data,
                "success": "Profile updated successfully!",
                "page_title": "User Profile",
                "active_nav": "profile"
            }
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        error_message = str(e)
        
        # Get current profile data for error response
        profile_data = {
            "user_id": current_user.get("id", ""),
            "username": current_user.get("username", ""),
            "email": current_user.get("email", ""),
            "full_name": current_user.get("full_name", ""),
            "bio": current_user.get("bio", ""),
            "location": current_user.get("location", ""),
            "profile_image": current_user.get("profile_image", "/static/img/avatars/default.png")
        }
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": [],
                "error": f"Error updating profile: {error_message}",
                "page_title": "User Profile"
            },
            status_code=500
        )

@router.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Validate password requirements
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Check if passwords match
        if new_password != confirm_password:
            # Get current profile data for error response
            profile_data = {
                "user_id": current_user.get("id", ""),
                "username": current_user.get("username", ""),
                "email": current_user.get("email", ""),
                "full_name": current_user.get("full_name", ""),
                "bio": current_user.get("bio", ""),
                "location": current_user.get("location", ""),
                "profile_image": current_user.get("profile_image", "/static/img/avatars/default.png")
            }
            
            return get_templates(request).TemplateResponse(
                "profile.html",
                {
                    "request": request,
                    "user": current_user,
                    "profile": profile_data,
                    "activity": [],
                    "error": "New passwords do not match",
                    "page_title": "User Profile"
                },
                status_code=400
            )
        
        # In demo mode, simulate password change validation
        # In real implementation, verify current_password against stored password
        demo_stored_password = "demo_password"  # This would be hashed in real implementation
        
        if current_password != demo_stored_password and current_password != "password":
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # In demo mode, simulate successful password change
        logger.info(f"Password changed for user {current_user['id']}")
        
        # Get profile data for success response
        profile_data = {
            "user_id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name", ""),
            "bio": current_user.get("bio", ""),
            "location": current_user.get("location", ""),
            "profile_image": current_user.get("profile_image", "/static/img/avatars/default.png"),
            "join_date": current_user.get("join_date", "2025-01-15"),
            "last_login": current_user.get("last_login", "2025-07-07T21:35:00Z"),
            "subscription_type": current_user.get("subscription_type", "Premium"),
            "total_predictions": current_user.get("total_predictions", 156),
            "portfolio_value": current_user.get("portfolio_value", 125000.50),
            "accuracy_rate": current_user.get("accuracy_rate", 0.847)
        }
        
        # Add password change to activity
        activity_data = [
            {
                "timestamp": datetime.now().isoformat() + "Z",
                "action": "Password Changed",
                "details": "Password updated successfully",
                "type": "security"
            }
        ]
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": activity_data,
                "success": "Password changed successfully!",
                "page_title": "User Profile",
                "active_nav": "profile"
            }
        )
        
    except HTTPException as e:
        # Get current profile data for error response
        profile_data = {
            "user_id": current_user.get("id", ""),
            "username": current_user.get("username", ""),
            "email": current_user.get("email", ""),
            "full_name": current_user.get("full_name", ""),
            "bio": current_user.get("bio", ""),
            "location": current_user.get("location", ""),
            "profile_image": current_user.get("profile_image", "/static/img/avatars/default.png")
        }
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": [],
                "error": e.detail,
                "page_title": "User Profile"
            },
            status_code=e.status_code
        )
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        error_message = str(e)
        
        # Get current profile data for error response
        profile_data = {
            "user_id": current_user.get("id", ""),
            "username": current_user.get("username", ""),
            "email": current_user.get("email", ""),
            "full_name": current_user.get("full_name", ""),
            "bio": current_user.get("bio", ""),
            "location": current_user.get("location", ""),
            "profile_image": current_user.get("profile_image", "/static/img/avatars/default.png")
        }
        
        return get_templates(request).TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": current_user,
                "profile": profile_data,
                "activity": [],
                "error": f"Error changing password: {error_message}",
                "page_title": "User Profile"
            },
            status_code=500
        )

@router.delete("/delete-account")
async def delete_account(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Delete user account (demo mode)"""
    try:
        # In demo mode, simulate account deletion
        logger.info(f"Account deletion requested for user {current_user['id']}")
        
        # Clear session
        request.session.clear()
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Account deleted successfully (demo mode)",
                "redirect_url": "/login?msg=Account+deleted+successfully"
            }
        )
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Error deleting account: {str(e)}"},
            status_code=500
        )

@router.get("/activity")
async def get_user_activity(
    request: Request,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get user activity history (API endpoint)"""
    try:
        # Demo activity data with pagination
        all_activities = [
            {
                "id": i,
                "timestamp": f"2025-07-{7-i//10:02d}T{20-(i%24):02d}:00:00Z",
                "action": ["Stock Prediction", "Portfolio Update", "Watchlist Added", "Profile Updated"][i % 4],
                "details": f"Activity {i} details",
                "type": ["prediction", "portfolio", "watchlist", "profile"][i % 4]
            }
            for i in range(1, 101)  # 100 demo activities
        ]
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        activities = all_activities[start_idx:end_idx]
        
        return JSONResponse(
            content={
                "success": True,
                "activities": activities,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(all_activities),
                    "has_next": end_idx < len(all_activities),
                    "has_prev": page > 1
                }
            }
        )
    except Exception as e:
        logger.error(f"Error fetching user activity: {str(e)}")
        return JSONResponse(
            content={"success": False, "message": f"Error fetching activity: {str(e)}"},
            status_code=500
        )

# Health check endpoint
@router.get("/health")
async def profile_health_check():
    """Profile service health check"""
    return {
        "status": "healthy",
        "service": "profile",
        "timestamp": "2025-07-07T21:42:27Z"
    }
