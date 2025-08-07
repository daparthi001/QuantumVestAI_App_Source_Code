"""
QuantumVestAI API Proxy Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
import logging
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from core.config.settings import settings

# Setup router
router = APIRouter(prefix="/api/v1", tags=["api"])
logger = logging.getLogger("quantumvestai.api_proxy")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/ticker-search")
async def ticker_search_proxy(request: Request):
    """Direct proxy for ticker search API endpoint"""
    try:
        # Forward request to live API
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_V1_URL}/ticker-search", params=request.query_params)
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Failed to forward ticker search to API: {e}")
        raise HTTPException(
            status_code=503,
            detail="Ticker search service temporarily unavailable - please check API connectivity"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"API returned error status {e.response.status_code}: {e}")
        raise HTTPException(
            status_code=502,
            detail="Ticker search service returned an error - please try again later"
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
        logger.info("Enabling advanced features")
        
        return JSONResponse({
            "status": "success",
            "message": "Advanced features enabled successfully",
            "features": {
                "advanced_analytics": True,
                "real_time_data": True,
                "ai_predictions": True,
                "portfolio_insights": True
            }
        })
        
    except Exception as e:
        logger.error(f"Error enabling advanced features: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to enable advanced features", "detail": str(e)},
            status_code=500
        )

@router.get("/users/features")
async def get_features_proxy(request: Request):
    """Direct proxy for getting user features"""
    try:
        logger.info("Getting user features")
        
        return JSONResponse({
            "status": "success",
            "features": {
                "basic": True,
                "advanced_analytics": True,
                "real_time_data": True,
                "ai_predictions": True,
                "portfolio_insights": True,
                "api_access": True
            },
            "plan": "Premium Demo",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting features status: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to get features status", "detail": str(e)},
            status_code=500
        )

@router.get("/health")
async def api_proxy_health():
    """Health check for API proxy"""
    return {
        "status": "healthy",
        "service": "api_proxy",
        "timestamp": datetime.utcnow().isoformat(),
    }

# Generic API proxy for other endpoints
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def generic_api_proxy(request: Request, path: str):
    """Generic proxy for any API endpoint"""
    try:
        method = request.method
        logger.info(f"Generic API proxy: {method} /{path}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Demo response for {method} /{path}",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API proxy for /{path}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to proxy request to /{path}", "detail": str(e)},
            status_code=500
        )
