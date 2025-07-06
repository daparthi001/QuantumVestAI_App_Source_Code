from fastapi import Depends, HTTPException, Query, Request
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from ui.services.api_client import APIClient
from core.config.constants import (
    USER_ROLE_ADMIN,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE
)
API_URL = "http://quantumvestai-dev-api:8000/api/v1"
# get_current_user function removed as per requirements

# get_current_active_user function removed as per requirements

# get_admin_user function removed as per requirements

async def get_api_client(request: Request) -> APIClient:
    """
    Dependency to get API client without authentication
    """
    return APIClient(token=None)

async def get_template_context(request: Request) -> Dict[str, Any]:
    """
    Dependency to get base template context for all templates
    """
    # Basic context without user info
    context = {
        "request": request,
        "user": None,
        "now": datetime.now(),
        "is_admin": False,
        "is_premium": False
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