"""
Authentication Dependencies for QuantumVestAI UI
Created: 2025-06-17 20:54:48
Author: daparthi001
"""
import os
import requests
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from datetime import datetime

logger = logging.getLogger("quantumvestai.auth")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

async def get_current_user(request: Request):
    """
    Extract and validate the user from the access token in cookies
    or emergency token for development
    """
    # Check for access token in cookies
    token = request.cookies.get("access_token")
    
    if not token:
        # Redirect to login if no token
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    # Handle emergency token (development only)
    if token.startswith("emergency_"):
        try:
            # Parse emergency token parts: emergency_username_timestamp
            parts = token.split("_")
            if len(parts) >= 2:
                username = parts[1]
                # You could check the timestamp expiry here
                
                # Return basic user info for development
                return {
                    "username": username,
                    "email": f"{username}@example.com",
                    "full_name": f"Dev User ({username})",
                    "role": "admin" if username == "daparthi001" else "user",
                    "token": token
                }
        except Exception as e:
            logger.warning(f"Invalid emergency token: {str(e)}")
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Validate token with API
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_V1_URL}/auth/validate",
            headers=headers,
            timeout=3
        )
        
        if response.status_code == 200:
            user_data = response.json()
            # Add token to user data for convenience
            user_data["token"] = token
            return user_data
    except Exception as e:
        logger.warning(f"Failed to validate token with API: {str(e)}")
    
    # If all validation fails, redirect to login
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

async def get_optional_current_user(request: Request):
    """
    Similar to get_current_user but doesn't redirect if no user is found
    Returns None instead
    """
    # Check for access token in cookies
    token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    # Handle emergency token (development only)
    if token.startswith("emergency_"):
        try:
            parts = token.split("_")
            if len(parts) >= 2:
                username = parts[1]
                return {
                    "username": username,
                    "email": f"{username}@example.com",
                    "full_name": f"Dev User ({username})",
                    "role": "admin" if username == "daparthi001" else "user",
                    "token": token
                }
        except Exception:
            return None
    
    # Validate token with API
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_V1_URL}/auth/validate",
            headers=headers,
            timeout=3
        )
        
        if response.status_code == 200:
            user_data = response.json()
            user_data["token"] = token
            return user_data
    except Exception:
        pass
    
    return None