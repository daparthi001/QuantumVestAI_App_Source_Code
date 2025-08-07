"""
WebSocket permissions handling module.
Created: 2025-08-05
Author: gayatri
"""
import logging
from typing import Dict, Any, Optional

from fastapi import HTTPException, status
from jose import jwt

# Set up logger
logger = logging.getLogger("api.websocket.permissions")

# Endpoints that should be accessible to free tier users
FREE_TIER_ENDPOINTS = [
    "/market-data",
    "/ws/market-data"
]

def check_websocket_permissions(
    token_payload: Dict[str, Any], 
    endpoint: str, 
    premium_param: Optional[str] = None
) -> bool:
    """
    Check if a user has permission to access a specific WebSocket endpoint.
    
    Args:
        token_payload: Decoded JWT payload
        endpoint: The WebSocket endpoint being accessed
        premium_param: Optional premium parameter to override role checks
        
    Returns:
        bool: True if access is allowed, False otherwise
    """
    # Always allow access to free tier endpoints regardless of role or token status
    if any(endpoint.endswith(free_endpoint) for free_endpoint in FREE_TIER_ENDPOINTS):
        logger.info(f"Allowing access to free-tier endpoint {endpoint}")
        return True
    
    # If premium parameter is provided and is 'true', allow access
    if premium_param and premium_param.lower() == 'true':
        logger.info(f"Allowing access due to premium parameter")
        return True
    
    # Get user role from token
    role = token_payload.get("role", "free")
    
    # Admin role can access everything
    if role == "admin":
        return True
    
    # Premium users can access premium endpoints
    if role == "premium" and endpoint.startswith("/premium"):
        return True
    
    # Basic users can access basic endpoints
    if role in ["basic", "premium"] and endpoint.startswith("/basic"):
        return True
    
    # CRITICAL FIX: Allow all authenticated users access to market data endpoints
    # Market data should be publicly accessible for all user roles
    if endpoint.endswith("/market-data") or "/market-data" in endpoint:
        logger.info(f"Allowing access to market data for role: {role}")
        return True
        
    # Default deny for unhandled cases
    logger.warning(f"Access denied to {endpoint} for role {role}")
    return False
