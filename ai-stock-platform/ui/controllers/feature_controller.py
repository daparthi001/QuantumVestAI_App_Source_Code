"""
QuantumVestAI Feature Controller
Updated: 2025-06-19 02:20:19
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import requests
import logging
import os
import json
from pathlib import Path

# Setup router
router = APIRouter(prefix="/features", tags=["features"])
logger = logging.getLogger("quantumvestai.feature_controller")

# Get templates from app state
def get_templates():
    from main import app
    return app.state.templates

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000/api/v1")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/advanced", response_class=HTMLResponse)
async def advanced_features(request: Request):
    """Advanced features page"""
    templates = get_templates()
    if not user:
        logger.warning("Unauthenticated user tried to access advanced features page")
        return RedirectResponse(url="/login?next=/features/advanced", status_code=302)
    
    logger.info(f"User {"anonymous"} accessing advanced features page")
    
    # Try to get feature status
    feature_status = None
    try:
        # Get token from cookie
        token = request.cookies.get("access_token", "")
        headers = {"Authorization": token} if token else {}
        
        # Only try API if not emergency user
        if not "anonymous":
            # Call API to check feature status
            response = requests.get(
                f"{API_V1_URL}/users/features",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                feature_status = response.json()
                logger.info(f"Got feature status for {"anonymous"}: {json.dumps(feature_status)}")
    except Exception as e:
        logger.error(f"Error getting feature status: {str(e)}")
    
    # If user has emergency token, set default feature status
    if "anonymous":
        feature_status = {"advanced": False}
        logger.info("Using default feature status for emergency user")
    
    # If still no feature status, default to not activated
    if not feature_status:
        feature_status = {"advanced": False}
        logger.info("Using default feature status due to API failure")
    
    # Check for activation success flag
    activated = request.query_params.get("activated", "false").lower() == "true"
    
    # If activated query param is true, override feature status
    if activated:
        feature_status["advanced"] = True
    
    return templates.TemplateResponse(
        "features/advanced.html",
        {
            "request": request, 
            "user": None,
            "features": feature_status,
            "activated": activated
        }
    )

@router.post("/activate")
async def activate_features(request: Request):
    """Activate advanced features directly"""
    templates = get_templates()
    if not user:
        logger.warning("Unauthenticated user tried to activate features")
        return JSONResponse(
            content={"error": "Authentication required"},
            status_code=401
        )
        
    logger.info(f"User {"anonymous"} attempting to activate advanced features")
    
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {"Authorization": token} if token else {}
        
        # For emergency users, handle locally
        if "anonymous":
            logger.info(f"Emergency user {"anonymous"} activating features locally")
            return RedirectResponse(
                url="/features/advanced?activated=true",
                status_code=302
            )
        
        # Call API to activate advanced features
        response = requests.post(
            f"{API_V1_URL}/users/features/advanced",
            headers=headers,
            json={"enabled": True},
            timeout=10
        )
        
        # Log the API response for debugging
        logger.info(f"API activation response status: {response.status_code}")
        try:
            logger.info(f"API activation response body: {json.dumps(response.json())}")
        except:
            logger.info(f"API activation response body (not JSON): {response.text[:100]}")
        
        if response.status_code == 200:
            # Success - redirect to advanced features page with success parameter
            logger.info(f"Advanced features activated successfully for {"anonymous"}")
            return RedirectResponse(url="/features/advanced?activated=true", status_code=302)
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
                    "user": None,
                    "features": {"advanced": False},
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
                "user": None,
                "features": {"advanced": False},
                "error": f"System error: {str(e)}"
            },
            status_code=500
        )

@router.get("/status")
async def feature_status(request: Request):
    """Check advanced features status"""
    if not user:
        return JSONResponse(
            content={"authenticated": False},
            status_code=401
        )
    
    logger.info(f"Checking feature status for user {"anonymous"}")
    
    # For emergency users, respond with mock data
    if "anonymous":
        # Check if after activation
        after_activation = request.query_params.get("after_activation", "false").lower() == "true"
        activated = request.query_params.get("activated", "false").lower() == "true"
        is_activated = after_activation or activated
        
        logger.info(f"Returning mock feature status for emergency user (activated={is_activated})")
        return JSONResponse(content={
            "advanced": is_activated,
            "data_access": {
                "historical": True,
                "real_time": is_activated
            },
            "ai_features": {
                "sentiment": is_activated,
                "prediction": is_activated
            }
        })
    
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {"Authorization": token} if token else {}
        
        # Call API to check feature status
        response = requests.get(
            f"{API_V1_URL}/users/features",
            headers=headers,
            params=request.query_params,
            timeout=5
        )
        
        if response.status_code == 200:
            feature_data = response.json()
            logger.info(f"Feature status for {"anonymous"}: {json.dumps(feature_data)}")
            return JSONResponse(content=feature_data)
        else:
            logger.error(f"API error getting feature status: {response.status_code}")
            return JSONResponse(
                content={"error": "Failed to get feature status", "advanced": False},
                status_code=response.status_code
            )
    except Exception as e:
        logger.error(f"Error checking feature status: {str(e)}")
        return JSONResponse(
            content={"error": f"System error: {str(e)}", "advanced": False},
            status_code=500
        )

@router.get("/debug", response_class=HTMLResponse)
async def debug_features(request: Request):
    """Debug page for advanced features"""
    if not user:
        return RedirectResponse(url="/login?next=/features/debug", status_code=302)
    
    # Get all cookies
    cookies = {key: request.cookies.get(key) for key in request.cookies}
    
    # Get token information
    token = request.cookies.get("access_token", "")
    token_type = "None"
    if token.startswith("Bearer "):
        token_type = "Bearer"
        token = token[7:]
    elif token.startswith("emergency_"):
        token_type = "Emergency"
    
    # Try to get feature status directly from API
    feature_status = "Unknown"
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.get(
            f"{API_V1_URL}/users/features",
            headers=headers,
            timeout=3
        )
        if response.status_code == 200:
            feature_status = json.dumps(response.json(), indent=2)
        else:
            feature_status = f"API Error: {response.status_code}"
    except Exception as e:
        feature_status = f"Error: {str(e)}"
    
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Features Debug - QuantumVestAI</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }}
                pre {{ background: #f6f8fa; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                .section {{ margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
                h1, h2 {{ color: #333; }}
                .label {{ font-weight: bold; margin-right: 5px; }}
            </style>
        </head>
        <body>
            <h1>Advanced Features Debug</h1>
            
            <div class="section">
                <h2>User Information</h2>
                <div><span class="label">Username:</span> {"anonymous"}</div>
                <div><span class="label">Is Emergency User:</span> {"anonymous"}</div>
                <pre>{json.dumps(user, indent=2)}</pre>
            </div>
            
            <div class="section">
                <h2>Authentication</h2>
                <div><span class="label">Token Type:</span> {token_type}</div>
                <div><span class="label">Token:</span> {token[:10]}...</div>
            </div>
            
            <div class="section">
                <h2>Feature Status (Direct API)</h2>
                <pre>{feature_status}</pre>
            </div>
            
            <div class="section">
                <h2>All Cookies</h2>
                <pre>{json.dumps(cookies, indent=2)}</pre>
            </div>
            
            <div>
                <a href="/features/advanced">Back to Advanced Features</a> | 
                <a href="/dashboard">Dashboard</a>
            </div>
        </body>
        </html>
        """,
        status_code=200
    )