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

# Setup router
router = APIRouter(prefix="/api/v1", tags=["api"])
logger = logging.getLogger("quantumvestai.api_proxy")

# Get API URL from environment or use default
API_URL = os.environ.get("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

@router.get("/ticker-search")
async def ticker_search_proxy(request: Request):
    """Direct proxy for ticker search API endpoint"""
    try:
        # Demo ticker search
        query = request.query_params.get("q", "")
        demo_results = []
        
        if query:
            demo_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
            demo_results = [
                {
                    "symbol": ticker,
                    "name": f"{ticker} Corporation",
                    "exchange": "NASDAQ"
                }
                for ticker in demo_tickers if query.upper() in ticker
            ]
        
        return JSONResponse({
            "status": "success",
            "results": demo_results,
            "query": query
        })
        
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
        logger.info("Enabling advanced features in demo mode")
        
        return JSONResponse({
            "status": "success",
            "message": "Advanced features enabled successfully (demo mode)",
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
        logger.info("Getting user features in demo mode")
        
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
        "demo_mode": True
    }

# Generic API proxy for other endpoints
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def generic_api_proxy(request: Request, path: str):
    """Generic proxy for any API endpoint"""
    try:
        # In demo mode, return generic success responses
        method = request.method
        logger.info(f"Generic API proxy: {method} /{path} (demo mode)")
        
        return JSONResponse({
            "status": "success",
            "message": f"Demo response for {method} /{path}",
            "demo_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API proxy for /{path}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to proxy request to /{path}", "detail": str(e)},
            status_code=500
        )
