"""
QuantumVestAI API Proxy Routes
Updated: 2025-06-19 02:20:19
Author: daparthi001
"""
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import requests
import logging
import os
import json

# Setup router
router = APIRouter(prefix="/api/v1", tags=["api"])
logger = logging.getLogger("quantumvestai.api_proxy")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/ticker-search")
async def ticker_search_proxy(request: Request):
    """Direct proxy for ticker search API endpoint"""
        logger.error(f"Error in ticker search proxy: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to search tickers", "detail": str(e)},
            status_code=500
        )

@router.post("/users/features/advanced")
async def enable_advanced_features_proxy(request: Request):
    """Direct proxy for enabling advanced features"""
            request_body = {}
            
        # Set enabled to true if not specified
        if "enabled" not in request_body:
            request_body["enabled"] = True
        
        logger.info(f"Enabling advanced features via API: {api_endpoint}")
        logger.debug(f"Request body: {json.dumps(request_body)}")
        
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=request_body,
            timeout=10
        )
        
        # Log the entire response for debugging
        logger.debug(f"API response status: {response.status_code}")
            logger.debug(f"API response body: {response.text[:200]}")
        
        if response.status_code == 200:
            logger.info("Advanced features enabled successfully!")
            
            # Update cached feature status
            # This ensures the UI immediately reflects the change
                logger.warning(f"Cache invalidation failed: {str(cache_err)}")
        
        # Return API response as-is
            # If response is not JSON, return a generic success response
            logger.warning(f"Failed to parse JSON response: {str(json_err)}")
            return JSONResponse(
                content={"status": "success", "message": "Advanced features activated"},
                status_code=200
            )
    except Exception as e:
        logger.error(f"Error enabling advanced features: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to enable advanced features", "detail": str(e)},
            status_code=500
        )

@router.get("/users/features")
async def get_features_proxy(request: Request):
    """Direct proxy for getting user features"""
        logger.error(f"Error getting features status: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to get features status", "detail": str(e)},
            status_code=500
        )

# Generic API proxy for other endpoints
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def generic_api_proxy(request: Request, path: str):
    """Generic proxy for any API endpoint"""
            # If not JSON, return text response
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=response.headers.get("Content-Type", "text/plain")
            )
    except Exception as e:
        logger.error(f"Error in API proxy for /{path}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to proxy request to /{path}", "detail": str(e)},
            status_code=500
        )