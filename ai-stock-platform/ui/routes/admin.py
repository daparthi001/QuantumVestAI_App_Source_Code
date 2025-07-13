"""
QuantumVestAI Admin Routes
Last Updated: 2025-07-07 21:40:52
Author: hemanth9398
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import settings
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.api_client import APIClient

# Initialize logger and templates
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory=str(Path("templates")))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

router = APIRouter(tags=["admin"])

@router.get("/admin")
async def admin_page(request: Request):
    """Admin page (demo mode)"""
    return RedirectResponse(url="/login?msg=Admin+features+require+authentication+(demo+mode)", status_code=302)

# Admin access middleware
def admin_required(request: Request):
    """Verify the user has admin privileges"""
    # In demo mode, simulate admin check
    user = request.session.get("user")
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: dict = Depends(admin_required)):
    """Admin dashboard page"""
    try:
        # Demo admin dashboard data
        dashboard_data = {
            "total_users": 1247,
            "active_users": 892,
            "total_predictions": 15634,
            "api_calls_today": 3542,
            "system_health": "healthy",
            "models_active": 8,
            "error_rate": 0.02,
            "uptime": "99.8%",
            "recent_activities": [
                {"timestamp": "2025-07-07 21:35:00", "action": "User registration", "user": "user@example.com"},
                {"timestamp": "2025-07-07 21:30:00", "action": "Model retrained", "model": "LSTM_v2"},
                {"timestamp": "2025-07-07 21:25:00", "action": "Feature enabled", "feature": "advanced_charts"}
            ],
            "system_metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 34.1,
                "network_io": 125.6
            }
        }
        
        return get_templates(request).TemplateResponse(
            "admin/dashboard/index.html", 
            {
                "request": request, 
                "user": current_user, 
                "dashboard_data": dashboard_data,
                "page_title": "Admin Dashboard",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/dashboard/index.html", 
            {
                "request": request, 
                "user": current_user, 
                "error": error_message,
                "page_title": "Admin Dashboard Error"
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
        # Demo user data
        demo_users = [
            {
                "id": "user_001",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "role": "user",
                "status": "active",
                "created_at": "2025-01-15",
                "last_login": "2025-07-07",
                "advanced_features": True
            },
            {
                "id": "user_002", 
                "email": "jane.smith@example.com",
                "username": "janesmith",
                "role": "premium",
                "status": "active",
                "created_at": "2025-02-20",
                "last_login": "2025-07-06",
                "advanced_features": True
            },
            {
                "id": "user_003",
                "email": "mike.wilson@example.com", 
                "username": "mikewilson",
                "role": "user",
                "status": "inactive",
                "created_at": "2025-03-10",
                "last_login": "2025-06-15",
                "advanced_features": False
            }
        ]
        
        # Filter users based on search
        if search:
            demo_users = [u for u in demo_users if search.lower() in u["email"].lower() or search.lower() in u["username"].lower()]
        
        # Pagination logic
        total_users = len(demo_users)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_users = demo_users[start_idx:end_idx]
        total_pages = (total_users + size - 1) // size
        
        pagination = {
            "page": page,
            "size": size,
            "total": total_users,
            "pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
        
        return get_templates(request).TemplateResponse(
            "admin/users.html", 
            {
                "request": request, 
                "user": current_user, 
                "users": paginated_users,
                "pagination": pagination,
                "search": search,
                "page_title": "User Management",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading user management: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/users.html", 
            {
                "request": request, 
                "user": current_user, 
                "users": [], 
                "pagination": {"page": page, "size": size, "total": 0, "pages": 0},
                "error": error_message,
                "page_title": "User Management Error"
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
        # Demo user detail data
        user_detail_data = {
            "id": user_id,
            "email": "john.doe@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "role": "user",
            "status": "active",
            "created_at": "2025-01-15T10:30:00Z",
            "last_login": "2025-07-07T20:15:00Z",
            "advanced_features": True,
            "subscription": "premium",
            "api_calls_count": 1547,
            "predictions_count": 234,
            "portfolio_value": 125000.50,
            "activity_log": [
                {"timestamp": "2025-07-07 20:15:00", "action": "Login", "ip": "192.168.1.100"},
                {"timestamp": "2025-07-07 19:45:00", "action": "Stock prediction", "ticker": "AAPL"},
                {"timestamp": "2025-07-07 19:30:00", "action": "Portfolio update", "value": 125000.50}
            ]
        }
        
        return get_templates(request).TemplateResponse(
            "admin/user_detail.html", 
            {
                "request": request, 
                "user": current_user,
                "user_detail": user_detail_data,
                "page_title": f"User Details - {user_detail_data['username']}",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading user detail for {user_id}: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/user_detail.html", 
            {
                "request": request, 
                "user": current_user,
                "error": error_message,
                "page_title": "User Detail Error"
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
        # Validate role
        valid_roles = ["user", "premium", "admin"]
        if role not in valid_roles:
            return JSONResponse(
                content={"success": False, "message": f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
                status_code=400
            )
        
        # In demo mode, simulate successful update
        logger.info(f"Updated user {user_id} role to {role}")
        
        return JSONResponse(
            content={
                "success": True, 
                "message": f"User role updated to {role} successfully",
                "user_id": user_id,
                "new_role": role
            }
        )
    except Exception as e:
        logger.error(f"Error updating user role for {user_id}: {str(e)}")
        error_message = str(e)
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
        status = "active" if active else "inactive"
        
        # In demo mode, simulate successful update
        logger.info(f"Updated user {user_id} status to {status}")
        
        return JSONResponse(
            content={
                "success": True, 
                "message": f"User {status} successfully",
                "user_id": user_id,
                "new_status": status
            }
        )
    except Exception as e:
        logger.error(f"Error toggling user status for {user_id}: {str(e)}")
        error_message = str(e)
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
        feature_status = "enabled" if advanced_features else "disabled"
        
        # In demo mode, simulate successful update
        logger.info(f"Advanced features {feature_status} for user {user_id}")
        
        return JSONResponse(
            content={
                "success": True, 
                "message": f"Advanced features {feature_status} successfully",
                "user_id": user_id,
                "advanced_features": advanced_features
            }
        )
    except Exception as e:
        logger.error(f"Error toggling features for user {user_id}: {str(e)}")
        error_message = str(e)
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
        # Demo model data
        models_data = [
            {
                "id": "lstm_v2",
                "name": "LSTM Stock Predictor v2",
                "type": "LSTM",
                "status": "active",
                "accuracy": 0.847,
                "last_trained": "2025-07-05T14:30:00Z",
                "training_samples": 150000,
                "predictions_count": 5432
            },
            {
                "id": "transformer_v1",
                "name": "Transformer Market Analyzer",
                "type": "Transformer",
                "status": "training",
                "accuracy": 0.823,
                "last_trained": "2025-07-07T18:00:00Z",
                "training_samples": 200000,
                "predictions_count": 3241
            },
            {
                "id": "ensemble_v3",
                "name": "Ensemble Predictor v3",
                "type": "Ensemble",
                "status": "active",
                "accuracy": 0.891,
                "last_trained": "2025-07-06T09:15:00Z",
                "training_samples": 300000,
                "predictions_count": 8756
            }
        ]
        
        return get_templates(request).TemplateResponse(
            "admin/models.html", 
            {
                "request": request, 
                "user": current_user, 
                "models": models_data,
                "page_title": "Model Management",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading model management: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/models.html", 
            {
                "request": request, 
                "user": current_user, 
                "models": [],
                "error": error_message,
                "page_title": "Model Management Error"
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
        # In demo mode, simulate model retraining
        logger.info(f"Starting retraining for model {model_id}")
        
        return JSONResponse(
            content={
                "success": True, 
                "message": f"Model {model_id} retraining started successfully",
                "model_id": model_id,
                "status": "training",
                "estimated_completion": "2025-07-08T02:00:00Z"
            }
        )
    except Exception as e:
        logger.error(f"Error retraining model {model_id}: {str(e)}")
        error_message = str(e)
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
        # Demo API status data
        services_data = [
            {"name": "Authentication Service", "status": "healthy", "response_time": "45ms", "uptime": "99.9%"},
            {"name": "Prediction Service", "status": "healthy", "response_time": "120ms", "uptime": "99.7%"},
            {"name": "Data Service", "status": "warning", "response_time": "250ms", "uptime": "98.5%"},
            {"name": "Notification Service", "status": "healthy", "response_time": "30ms", "uptime": "99.8%"}
        ]
        
        metrics_data = {
            "uptime": "99.8%",
            "response_time": "98ms",
            "request_count": 15634,
            "error_rate": 0.02,
            "active_connections": 234,
            "cache_hit_rate": 0.87
        }
        
        logs_data = [
            {"timestamp": "2025-07-07 21:38:00", "level": "INFO", "service": "API", "message": "Health check completed"},
            {"timestamp": "2025-07-07 21:35:00", "level": "WARN", "service": "Data", "message": "Slow response detected"},
            {"timestamp": "2025-07-07 21:30:00", "level": "INFO", "service": "Auth", "message": "User authenticated successfully"}
        ]
        
        return get_templates(request).TemplateResponse(
            "admin/api_status.html", 
            {
                "request": request, 
                "user": current_user, 
                "services": services_data,
                "metrics": metrics_data,
                "logs": logs_data,
                "page_title": "API Status Dashboard",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading API status: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/api_status.html", 
            {
                "request": request, 
                "user": current_user, 
                "services": [],
                "metrics": {"uptime": "N/A", "response_time": "N/A", "request_count": 0, "error_rate": 0},
                "logs": [],
                "error": error_message,
                "page_title": "API Status Error"
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
        # Demo settings data
        settings_data = {
            "general": {
                "site_name": "QuantumVestAI",
                "maintenance_mode": False,
                "registration_enabled": True,
                "max_users": 10000,
                "session_timeout": 3600
            },
            "features": {
                "advanced_charts": True,
                "real_time_data": True,
                "portfolio_optimization": True,
                "sentiment_analysis": True,
                "custom_indicators": False
            },
            "api": {
                "rate_limit": 1000,
                "cache_ttl": 300,
                "max_connections": 500,
                "timeout": 30
            },
            "security": {
                "two_factor_required": False,
                "password_complexity": True,
                "session_security": True,
                "api_key_rotation": 30
            }
        }
        
        return get_templates(request).TemplateResponse(
            "admin/settings.html", 
            {
                "request": request, 
                "user": current_user, 
                "settings": settings_data,
                "page_title": "Admin Settings",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading admin settings: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/settings.html", 
            {
                "request": request, 
                "user": current_user, 
                "settings": {},
                "error": error_message,
                "page_title": "Admin Settings Error"
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
        # Get form data
        form_data = await request.form()
        
        # In demo mode, simulate settings update
        updated_settings = dict(form_data)
        logger.info(f"System settings updated: {updated_settings}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "System settings updated successfully",
                "updated_settings": updated_settings
            }
        )
    except Exception as e:
        logger.error(f"Error updating system settings: {str(e)}")
        error_message = str(e)
        return JSONResponse(
            content={"success": False, "message": error_message},
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
        # In demo mode, simulate feature toggle
        status = "enabled" if enabled else "disabled"
        logger.info(f"Feature {feature_name} {status}")
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Feature {feature_name} {status} successfully",
                "feature_name": feature_name,
                "enabled": enabled
            }
        )
    except Exception as e:
        logger.error(f"Error toggling feature {feature_name}: {str(e)}")
        error_message = str(e)
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
        # Demo features data
        features_data = {
            "available_features": [
                {
                    "name": "advanced_charts",
                    "display_name": "Advanced Charts",
                    "description": "Interactive candlestick and technical analysis charts",
                    "enabled": True,
                    "category": "visualization"
                },
                {
                    "name": "real_time_data",
                    "display_name": "Real-time Data",
                    "description": "Live market data updates",
                    "enabled": True,
                    "category": "data"
                },
                {
                    "name": "portfolio_optimization",
                    "display_name": "Portfolio Optimization",
                    "description": "AI-powered portfolio optimization algorithms",
                    "enabled": True,
                    "category": "analysis"
                },
                {
                    "name": "sentiment_analysis",
                    "display_name": "Sentiment Analysis",
                    "description": "Market sentiment analysis from news and social media",
                    "enabled": True,
                    "category": "analysis"
                },
                {
                    "name": "custom_indicators",
                    "display_name": "Custom Indicators",
                    "description": "Create and use custom technical indicators",
                    "enabled": False,
                    "category": "advanced"
                }
            ],
            "categories": ["visualization", "data", "analysis", "advanced"],
            "feature_usage_stats": {
                "advanced_charts": {"users": 456, "usage_percent": 67.2},
                "real_time_data": {"users": 623, "usage_percent": 91.8},
                "portfolio_optimization": {"users": 234, "usage_percent": 34.5},
                "sentiment_analysis": {"users": 345, "usage_percent": 50.9}
            }
        }
        
        return get_templates(request).TemplateResponse(
            "admin/features.html", 
            {
                "request": request, 
                "user": current_user,
                "features_data": features_data,
                "page_title": "Features Management",
                "active_nav": "admin"
            }
        )
    except Exception as e:
        logger.error(f"Error loading features management: {str(e)}")
        error_message = str(e)
        return get_templates(request).TemplateResponse(
            "admin/features.html", 
            {
                "request": request, 
                "user": current_user, 
                "error": error_message,
                "page_title": "Features Management Error"
            },
            status_code=500
        )

# Additional admin health check endpoint
@router.get("/health")
async def admin_health_check(current_user: dict = Depends(admin_required)):
    """Admin service health check"""
    return {
        "status": "healthy",
        "service": "admin",
        "timestamp": "2025-07-07T21:40:52Z",
        "user": current_user["username"] if current_user else "unknown"    }
