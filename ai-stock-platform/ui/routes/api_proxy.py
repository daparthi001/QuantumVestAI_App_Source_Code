"""
QuantumVestAI API Proxy Routes
Last Updated: 2025-06-18 22:05:54
Author: daparthi001
"""
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from services.api_client import APIClient
import logging
from typing import Dict, Any, Optional

# Setup router
router = APIRouter(prefix="/api/v1", tags=["api"])
logger = logging.getLogger(__name__)

@router.get("/ticker-search")
async def ticker_search_proxy(request: Request):
    """Proxy for ticker search API endpoint"""
    try:
        # Extract query parameters
        query_params = dict(request.query_params)
        
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Forward request to backend API
        search_results = api_client.get("/market/ticker-search", params=query_params)
        
        # Return API response as-is
        return JSONResponse(content=search_results)
    except Exception as e:
        logger.error(f"Error in ticker search proxy: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to search tickers", "detail": str(e)},
            status_code=500
        )

@router.get("/market/data")
async def market_data_proxy(request: Request):
    """Proxy for market data API endpoint"""
    try:
        # Extract query parameters
        query_params = dict(request.query_params)
        
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Forward request to backend API
        market_data = api_client.get("/market/data", params=query_params)
        
        # Return API response as-is
        return JSONResponse(content=market_data)
    except Exception as e:
        logger.error(f"Error in market data proxy: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to fetch market data", "detail": str(e)},
            status_code=500
        )

@router.get("/forecast/ticker/{ticker}")
async def forecast_ticker_proxy(request: Request, ticker: str):
    """Proxy for forecast ticker API endpoint"""
    try:
        # Extract query parameters
        query_params = dict(request.query_params)
        
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("access_token"))
        
        # Forward request to backend API
        forecast_data = api_client.get(f"/forecast/ticker/{ticker}", params=query_params)
        
        # Return API response as-is
        return JSONResponse(content=forecast_data)
    except Exception as e:
        logger.error(f"Error in forecast ticker proxy for {ticker}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to fetch forecast for {ticker}", "detail": str(e)},
            status_code=500
        )

@router.get("/users/feature-access")
async def feature_access_proxy(request: Request):
    """Proxy for feature access API endpoint"""
    try:
        # Extract query parameters
        query_params = dict(request.query_params)
        if "feature" not in query_params:
            raise HTTPException(status_code=400, detail="Feature parameter is required")
            
        # Create API client with auth token
        token = request.cookies.get("access_token")
        if not token:
            return JSONResponse(content={"available": False})
            
        api_client = APIClient(token=token)
        
        # Forward request to backend API
        feature_access = api_client.get("/users/feature-access", params=query_params)
        
        # Return API response as-is
        return JSONResponse(content=feature_access)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in feature access proxy: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to check feature access", "detail": str(e)},
            status_code=500
        )

@router.get("/features/advanced")
async def advanced_features_proxy(request: Request):
    """Proxy for advanced features API endpoint"""
    try:
        # Create API client with auth token
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        api_client = APIClient(token=token)
        
        # Forward request to backend API
        advanced_features = api_client.get("/features/advanced")
        
        # Return API response as-is
        return JSONResponse(content=advanced_features)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in advanced features proxy: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to fetch advanced features", "detail": str(e)},
            status_code=500
        )

# Generic API proxy for other endpoints
@router.get("/{path:path}")
async def generic_api_proxy(request: Request, path: str):
    """Generic proxy for any API endpoint"""
    try:
        # Extract query parameters
        query_params = dict(request.query_params)
        
        # Create API client with auth token
        token = request.cookies.get("access_token")
        api_client = APIClient(token=token)
        
        # Log the proxy request
        logger.debug(f"Proxying API request to /{path}")
        
        # Forward request to backend API
        response_data = api_client.get(f"/{path}", params=query_params)
        
        # Return API response as-is
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error in API proxy for /{path}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to proxy request to /{path}", "detail": str(e)},
            status_code=500
        )