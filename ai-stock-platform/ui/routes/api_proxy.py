"""
QuantumVestAI API Proxy Routes
Last Updated: 2025-06-18 22:24:29
Author: daparthi001
"""
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import requests
import logging
import os

# Setup router
router = APIRouter(prefix="/api/v1", tags=["api"])
logger = logging.getLogger(__name__)

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/ticker-search")
async def ticker_search_proxy(request: Request):
    """Direct proxy for ticker search API endpoint"""
    try:
        # Extract query parameters as string
        query_string = str(request.url.query)
        
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {}
        if token:
            headers["Authorization"] = token
        
        # Forward request directly to backend API
        api_endpoint = f"{API_V1_URL}/market/ticker-search"
        if query_string:
            api_endpoint += f"?{query_string}"
            
        logger.info(f"Proxying request to: {api_endpoint}")
        
        response = requests.get(
            api_endpoint,
            headers=headers,
            timeout=10
        )
        
        # Return API response as-is
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )
    except Exception as e:
        logger.error(f"Error in ticker search proxy: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to search tickers", "detail": str(e)},
            status_code=500
        )

@router.post("/users/features/advanced")
async def enable_advanced_features_proxy(request: Request):
    """Direct proxy for enabling advanced features"""
    try:
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        if not token:
            return JSONResponse(
                content={"error": "Authentication required"},
                status_code=401
            )
            
        headers = {"Authorization": token}
        
        # Forward request directly to backend API
        api_endpoint = f"{API_V1_URL}/users/features/advanced"
        
        # Get request body if any
        body = await request.body()
        data = {"enabled": True}
        
        logger.info(f"Enabling advanced features via API: {api_endpoint}")
        
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Advanced features enabled successfully!")
            
            # Update cached feature status
            # This ensures the UI immediately reflects the change
            cache_response = requests.post(
                f"{API_V1_URL}/cache/invalidate",
                headers=headers,
                json={"keys": ["user_features", "advanced_features"]},
                timeout=5
            )
            if cache_response.status_code != 200:
                logger.warning("Failed to invalidate feature cache")
        
        # Return API response as-is
        return JSONResponse(
            content=response.json() if response.content else {"status": "success"},
            status_code=response.status_code
        )
    except Exception as e:
        logger.error(f"Error enabling advanced features: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to enable advanced features", "detail": str(e)},
            status_code=500
        )

# Generic API proxy for other endpoints
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def generic_api_proxy(request: Request, path: str):
    """Generic proxy for any API endpoint"""
    try:
        # Extract query parameters as string
        query_string = str(request.url.query)
        
        # Get auth token from cookies
        token = request.cookies.get("access_token", "")
        headers = {}
        if token:
            headers["Authorization"] = token
            
        # Add any other headers from the original request
        for header_name, header_value in request.headers.items():
            if header_name.lower() not in ["host", "cookie"]:
                headers[header_name] = header_value
        
        # Determine method and prepare for forwarding
        method = request.method.lower()
        api_endpoint = f"{API_V1_URL}/{path}"
        if query_string:
            api_endpoint += f"?{query_string}"
            
        logger.info(f"Proxying {method.upper()} request to: {api_endpoint}")
        
        # Get request body if POST/PUT
        data = None
        if method in ["post", "put"]:
            content_type = request.headers.get("Content-Type", "")
            if "application/json" in content_type:
                data = await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                data = dict(await request.form())
            else:
                data = await request.body()
        
        # Forward the request with appropriate method
        if method == "get":
            response = requests.get(api_endpoint, headers=headers, timeout=10)
        elif method == "post":
            response = requests.post(api_endpoint, headers=headers, json=data, timeout=10)
        elif method == "put":
            response = requests.put(api_endpoint, headers=headers, json=data, timeout=10)
        elif method == "delete":
            response = requests.delete(api_endpoint, headers=headers, timeout=10)
        else:
            return JSONResponse(
                content={"error": f"Method {method} not supported"},
                status_code=405
            )
        
        # Return API response as-is
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )
    except Exception as e:
        logger.error(f"Error in API proxy for /{path}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to proxy request to /{path}", "detail": str(e)},
            status_code=500
        )