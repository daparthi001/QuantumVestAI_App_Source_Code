from fastapi import Depends, HTTPException, Query, Request
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from ui.routes.auth import get_current_user as auth_get_current_user
from ui.services.api_client import APIClient
from core.config.constants import (
    USER_ROLE_ADMIN,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE
)
API_URL = "http://quantumvestai-dev-api:8000/api/v1"
async def get_current_user(request: Request):
    """
    Dependency to get current authenticated user
    This is a wrapper around the auth module's get_current_user function
    """
    return await auth_get_current_user(request)

async def get_current_active_user(current_user: Dict = Depends(get_current_user)):
    """
    Dependency to get current active user, requiring authentication
    
    Raises:
        HTTPException: If user is not authenticated
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

async def get_admin_user(current_user: Dict = Depends(get_current_user)):
    """
    Dependency to get current user with admin role
    
    Raises:
        HTTPException: If user is not authenticated or not an admin
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user.get("role") != USER_ROLE_ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return current_user

async def get_api_client(request: Request) -> APIClient:
    """
    Dependency to get API client with authentication if available
    """
    current_user = await get_current_user(request)
    token = request.cookies.get("token") if current_user else None
    return APIClient(token=token)

async def get_template_context(request: Request) -> Dict[str, Any]:
    """
    Dependency to get base template context for all templates
    """
    current_user = await get_current_user(request)
    
    # Basic context with user info
    context = {
        "request": request,
        "user": current_user,
        "now": datetime.now(),
        "is_admin": current_user and current_user.get("role") == USER_ROLE_ADMIN,
        "is_premium": current_user and current_user.get("role") in ["admin", "premium"]
    }
    
    # Add any flash messages from the session
    if hasattr(request.session, "pop"):
        context["messages"] = request.session.pop("messages", [])
    
    return context

async def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page")
) -> Dict[str, int]:
    """
    Dependency for pagination parameters
    """
    return {"page": page, "size": size}

async def common_query_params(
    search: Optional[str] = Query(None, description="Search query"),
    sort: Optional[str] = Query(None, description="Sort field"),
    order: Optional[str] = Query("asc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page")
) -> Dict[str, Any]:
    """
    Dependency for common query parameters used in list endpoints
    """
    params = {
        "page": page,
        "size": size
    }
    
    if search:
        params["search"] = search
    
    if sort:
        params["sort"] = sort
        params["order"] = order
    
    return params