"""
QuantumVestAI Admin Routes
Last Updated: 2025-06-18 21:48:41
Author: daparthi001
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from routes.auth import get_current_user
from config.settings import settings
from services.api_client import APIClient

API_URL = "http://quantumvestai-dev-api:8000/api/v1"
# Admin role constant
USER_ROLE_ADMIN = "admin"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(prefix="/admin", tags=["admin"])

# Admin access middleware
def admin_required(current_user: dict = Depends(get_current_user)):
    """Verify the user has admin privileges"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if current_user.get("role") != USER_ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: dict = Depends(admin_required)):
    """Admin dashboard page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get system stats from API
        stats = api_client.get("/admin/stats")
        
        # Get recent user signups
        recent_users = api_client.get("/admin/users/recent", params={"limit": 5})
        
        # Get system health metrics
        health_metrics = api_client.get("/admin/health")
        
        # Get advanced features usage statistics
        features_stats = api_client.get("/admin/features/stats")
        
        return templates.TemplateResponse(
            "admin/dashboard/index.html", 
            {
                "request": request, 
                "user": current_user, 
                "stats": stats,
                "recent_users": recent_users,
                "health_metrics": health_metrics,
                "features_stats": features_stats
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
            "admin/dashboard/index.html", 
            {
                "request": request, 
                "user": current_user, 
                "error": error_message
            },
            status_code=500
        )

@router.get("/users", response_class=HTMLResponse)
async def user_management(
    request: Request, 
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=5, le=100),
    search: str = Query(None),
    current_user: dict = Depends(admin_required)
):
    """User management page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Prepare query parameters
        params = {"page": page, "size": size}
        if search:
            params["search"] = search
            
        # Get users from API
        users_data = api_client.get("/admin/users", params=params)
        
        return templates.TemplateResponse(
            "admin/users.html", 
            {
                "request": request, 
                "user": current_user, 
                "users": users_data.get("items", []), 
                "pagination": users_data.get("pagination", {}),
                "search": search
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
            "admin/users.html", 
            {
                "request": request, 
                "user": current_user, 
                "users": [], 
                "pagination": {"page": page, "size": size, "total": 0, "pages": 0},
                "error": error_message
            },
            status_code=500
        )

@router.get("/users/{user_id}", response_class=HTMLResponse)
async def user_detail(
    request: Request,
    user_id: str,
    current_user: dict = Depends(admin_required)
):
    """User detail page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get user details from API
        user_details = api_client.get(f"/admin/users/{user_id}")
        
        # Get user activity
        user_activity = api_client.get(f"/admin/users/{user_id}/activity")
        
        # Get user's feature usage
        feature_usage = api_client.get(f"/admin/users/{user_id}/features")
        
        return templates.TemplateResponse(
            "admin/user_detail.html", 
            {
                "request": request, 
                "user": current_user,
                "user_details": user_details,
                "user_activity": user_activity,
                "feature_usage": feature_usage
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
            "admin/user_detail.html", 
            {
                "request": request, 
                "user": current_user,
                "error": error_message
            },
            status_code=500
        )

@router.post("/users/{user_id}/update-role")
async def update_user_role(
    user_id: str,
    role: str = Form(...),
    current_user: dict = Depends(admin_required),
    request: Request = None
):
    """Update user role"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update user role via API
        api_client.put(f"/admin/users/{user_id}/role", data={"role": role})
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: str,
    active: bool = Form(...),
    current_user: dict = Depends(admin_required),
    request: Request = None
):
    """Activate or deactivate a user"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update user status via API
        api_client.put(f"/admin/users/{user_id}/status", data={"active": active})
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.post("/users/{user_id}/toggle-features")
async def toggle_user_features(
    user_id: str,
    advanced_features: bool = Form(...),
    current_user: dict = Depends(admin_required),
    request: Request = None
):
    """Enable or disable advanced features for a user"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update user features via API
        api_client.put(f"/admin/users/{user_id}/features", data={
            "advanced_features": advanced_features
        })
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.get("/models", response_class=HTMLResponse)
async def model_management(
    request: Request, 
    current_user: dict = Depends(admin_required)
):
    """Model management page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get models from API
        models = api_client.get("/admin/models")
        
        # Get training status
        training_status = api_client.get("/admin/models/training-status")
        
        return templates.TemplateResponse(
            "admin/models.html", 
            {
                "request": request, 
                "user": current_user, 
                "models": models,
                "training_status": training_status
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
            "admin/models.html", 
            {
                "request": request, 
                "user": current_user, 
                "models": [],
                "error": error_message
            },
            status_code=500
        )

@router.post("/models/{model_id}/retrain")
async def retrain_model(
    model_id: str,
    request: Request,
    current_user: dict = Depends(admin_required)
):
    """Retrain a model"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Retrain model via API
        response = api_client.post(f"/admin/models/{model_id}/retrain")
        
        return JSONResponse(content={"success": True, "job_id": response.get("job_id")})
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.get("/api-status", response_class=HTMLResponse)
async def api_status_page(
    request: Request, 
    current_user: dict = Depends(admin_required)
):
    """API status dashboard"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get API status from API
        status_data = api_client.get("/admin/status")
        
        # Get API logs
        logs = api_client.get("/admin/logs", params={"limit": 100})
        
        return templates.TemplateResponse(
            "admin/api_status.html", 
            {
                "request": request, 
                "user": current_user, 
                **status_data,
                "logs": logs
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
            "admin/api_status.html", 
            {
                "request": request, 
                "user": current_user, 
                "services": [],
                "metrics": {"uptime": "N/A", "response_time": "N/A", "request_count": 0, "error_rate": 0},
                "logs": [],
                "error": error_message
            },
            status_code=500
        )

@router.get("/settings", response_class=HTMLResponse)
async def admin_settings_page(
    request: Request, 
    current_user: dict = Depends(admin_required)
):
    """Admin settings page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get system settings from API
        system_settings = api_client.get("/admin/settings")
        
        # Get feature settings
        feature_settings = api_client.get("/admin/features/settings")
        
        return templates.TemplateResponse(
            "admin/settings.html", 
            {
                "request": request, 
                "user": current_user, 
                "settings": system_settings,
                "feature_settings": feature_settings
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
            "admin/settings.html", 
            {
                "request": request, 
                "user": current_user, 
                "settings": {},
                "error": error_message
            },
            status_code=500
        )

@router.post("/settings/update")
async def update_system_settings(
    request: Request,
    current_user: dict = Depends(admin_required)
):
    """Update system settings"""
    try:
        # Parse form data
        form_data = await request.form()
        settings_data = {k: v for k, v in form_data.items()}
        
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update settings via API
        api_client.put("/admin/settings", data=settings_data)
        
        # Redirect back to settings page with success message
        return RedirectResponse(url="/admin/settings?success=true", status_code=303)
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        # Create API client to fetch current settings
        api_client = APIClient(token=request.cookies.get("access_token"))
        system_settings = {}
        
        try:
            system_settings = api_client.get("/admin/settings")
        except:
            pass
            
        return templates.TemplateResponse(
            "admin/settings.html", 
            {
                "request": request, 
                "user": current_user, 
                "settings": system_settings,
                "error": error_message
            },
            status_code=500
        )

@router.post("/features/toggle")
async def toggle_feature_availability(
    request: Request,
    feature_name: str = Form(...),
    enabled: bool = Form(...),
    current_user: dict = Depends(admin_required)
):
    """Toggle feature availability"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Update feature settings via API
        api_client.put("/admin/features/settings", data={
            "feature_name": feature_name,
            "enabled": enabled
        })
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        return JSONResponse(
            content={"success": False, "message": error_message},
            status_code=500
        )

@router.get("/features", response_class=HTMLResponse)
async def features_management(
    request: Request, 
    current_user: dict = Depends(admin_required)
):
    """Advanced features management page"""
    try:
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Get features usage statistics
        usage_stats = api_client.get("/admin/features/stats")
        
        # Get feature settings
        feature_settings = api_client.get("/admin/features/settings")
        
        # Get feature usage by user
        usage_by_user = api_client.get("/admin/features/usage", params={"limit": 10})
        
        return templates.TemplateResponse(
            "admin/features.html", 
            {
                "request": request, 
                "user": current_user, 
                "usage_stats": usage_stats,
                "feature_settings": feature_settings,
                "usage_by_user": usage_by_user
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
            "admin/features.html", 
            {
                "request": request, 
                "user": current_user, 
                "error": error_message
            },
            status_code=500
        )