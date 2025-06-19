"""
QuantumVestAI Feature Controller
Last Updated: 2025-06-18 23:08:04
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
import os
from pathlib import Path
from controllers.auth_controller import get_current_user

# Setup router
router = APIRouter(prefix="/features", tags=["features"])
templates = Jinja2Templates(directory=str(Path("templates")))
logger = logging.getLogger(__name__)

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/advanced", response_class=HTMLResponse)
async def advanced_features(request: Request, user: dict = Depends(get_current_user)):
    """Advanced features page"""
    if not user:
        return RedirectResponse(url="/login?next=/features/advanced", status_code=302)
        
    return templates.TemplateResponse(
        "features/advanced.html",
        {"request": request, "user": user}
    )

@router.post("/activate")
async def activate_features(request: Request, user: dict = Depends(get_current_user)):
    """Activate advanced features directly"""
    if not user:
        return JSONResponse(
            content={"error": "Authentication required"},
            status_code=401
        )
        
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {"Authorization": token} if token else {}
        
        # Call API to activate features
        response = requests.post(
            f"{API_V1_URL}/users/features/advanced",
            headers=headers,
            json={"enabled": True},
            timeout=10
        )
        
        # Log the API response for debugging
        logger.info(f"API activation response: {response.status_code}, {response.text[:100]}")
        
        if response.status_code == 200:
            # Success - redirect to dashboard with success parameter
            return RedirectResponse(url="/dashboard?features_activated=true", status_code=302)
        else:
            # API error
            try:
                error_data = response.json()
                error_message = error_data.get("detail", "Failed to activate features")
            except:
                error_message = f"API error: {response.status_code}"
                
            logger.error(f"API error activating features: {error_message}")
            return templates.TemplateResponse(
                "features/advanced.html",
                {
                    "request": request,
                    "user": user,
                    "error": error_message
                },
                status_code=400
            )
    except Exception as e:
        logger.error(f"Error activating features: {str(e)}")
        return templates.TemplateResponse(
            "features/advanced.html",
            {
                "request": request,
                "user": user,
                "error": f"System error: {str(e)}"
            },
            status_code=500
        )

@router.get("/status")
async def feature_status(request: Request, user: dict = Depends(get_current_user)):
    """Check advanced features status"""
    if not user:
        return JSONResponse(
            content={"authenticated": False},
            status_code=401
        )
        
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {"Authorization": token} if token else {}
        
        # Call API to check feature status
        response = requests.get(
            f"{API_V1_URL}/users/features",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return JSONResponse(content=response.json())
        else:
            return JSONResponse(
                content={"error": "Failed to get feature status"},
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error checking feature status: {str(e)}")
        return JSONResponse(
            content={"error": f"System error: {str(e)}"},
            status_code=500
        )