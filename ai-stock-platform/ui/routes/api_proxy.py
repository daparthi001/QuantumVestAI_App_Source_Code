"""
<<<<<<< HEAD
API proxy routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
=======
QuantumVestAI API Proxy Routes
Updated: 2025-07-07 21:54:42
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from fastapi.responses import JSONResponse
<<<<<<< HEAD
from pathlib import Path
import requests
import logging
import os
import json
from typing import Any, Dict, Optional
=======
import logging
import os
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000")
API_V1_URL = f"{API_URL}/api/v1"

<<<<<<< HEAD
# Create router
router = APIRouter(prefix="/api", tags=["api_proxy"])

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def get_auth_headers(request: Request) -> Dict[str, str]:
    """Extract authentication headers from request"""
    headers = {"Content-Type": "application/json"}
    
    # Get token from cookie or header
    auth_cookie = request.cookies.get("access_token")
    auth_header = request.headers.get("authorization")
    
    if auth_cookie:
        headers["Authorization"] = auth_cookie
    elif auth_header:
        headers["Authorization"] = auth_header
    
    return headers

async def proxy_request(
    method: str,
    endpoint: str,
    request: Request,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """Generic proxy function for API requests"""
    try:
        url = f"{API_V1_URL}{endpoint}"
        headers = get_auth_headers(request)
        
        # Make request to backend API
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_data,
            timeout=timeout
        )
        
        # Return response data
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"message": "Success", "data": response.text}
        else:
            # Handle API errors
            try:
                error_data = response.json()
            except json.JSONDecodeError:
                error_data = {"detail": response.text or "API request failed"}
            
            raise HTTPException(
                status_code=response.status_code,
                detail=error_data.get("detail", "API request failed")
            )
            
    except requests.RequestException as e:
        logger.error(f"API proxy error for {method} {endpoint}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Backend API unavailable: {str(e)}"
        )
    except HTTPException:
        raise
=======
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
        
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    except Exception as e:
        logger.error(f"Unexpected error in API proxy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

<<<<<<< HEAD
@router.get("/health")
async def api_health_check(request: Request):
    """Check backend API health"""
    try:
        response_data = await proxy_request("GET", "/health", request, timeout=10)
        return JSONResponse(content={
            "proxy_status": "healthy",
            "backend_api": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException as e:
=======
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
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        return JSONResponse(
            content={
                "proxy_status": "healthy",
                "backend_api": {
                    "status": "unavailable",
                    "error": str(e.detail)
                },
                "timestamp": datetime.now().isoformat()
            },
            status_code=200  # Proxy is healthy even if backend is down
        )

<<<<<<< HEAD
@router.get("/market/data")
async def proxy_market_data(request: Request):
    """Proxy market data endpoint"""
    try:
        response_data = await proxy_request("GET", "/market/data", request)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        # Return demo data if API is unavailable
        logger.warning(f"API unavailable for market data, returning demo data: {e.detail}")
        
        demo_data = {
            "indices": [
                {"symbol": "SPY", "price": 458.32, "change": 2.45, "change_percent": 0.54},
                {"symbol": "QQQ", "price": 391.87, "change": -1.23, "change_percent": -0.31},
                {"symbol": "IWM", "price": 198.45, "change": 0.87, "change_percent": 0.44}
            ],
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.get("/stocks/{symbol}")
async def proxy_stock_data(request: Request, symbol: str):
    """Proxy stock data endpoint"""
    try:
        response_data = await proxy_request("GET", f"/stocks/{symbol}", request)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        # Return demo data if API is unavailable
        logger.warning(f"API unavailable for stock {symbol}, returning demo data: {e.detail}")
        
        demo_data = {
            "symbol": symbol.upper(),
            "price": 150.00 + len(symbol),
            "change": 1.25,
            "change_percent": 0.84,
            "volume": "1.2M",
            "market_cap": "500B",
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.get("/news")
async def proxy_market_news(request: Request):
    """Proxy market news endpoint"""
    try:
        response_data = await proxy_request("GET", "/news", request)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        # Return demo news if API is unavailable
        logger.warning(f"API unavailable for news, returning demo data: {e.detail}")
        
        demo_data = {
            "articles": [
                {
                    "title": "Market Update: Technology Stocks Rally",
                    "summary": "Tech stocks continue their upward momentum amid positive earnings reports.",
                    "source": "Financial News",
                    "timestamp": "2 hours ago"
                },
                {
                    "title": "Federal Reserve Policy Decision Expected",
                    "summary": "Investors await Fed decision on interest rates scheduled for next week.",
                    "source": "Economic Times",
                    "timestamp": "4 hours ago"
                }
            ],
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.get("/portfolio")
async def proxy_portfolio_data(request: Request):
    """Proxy portfolio data endpoint"""
    try:
        # Check authentication for portfolio data
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for portfolio data"
            )
        
        response_data = await proxy_request("GET", "/portfolio", request)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        if e.status_code == 401:
            raise e
        
        # Return demo portfolio if API is unavailable
        logger.warning(f"API unavailable for portfolio, returning demo data: {e.detail}")
        
        demo_data = {
            "total_value": 125000.00,
            "total_gain_loss": 15000.00,
            "positions": [
                {"symbol": "AAPL", "shares": 100, "value": 18231.00},
                {"symbol": "MSFT", "shares": 50, "value": 18942.50},
                {"symbol": "GOOGL", "shares": 75, "value": 10692.00}
            ],
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.post("/forecast/generate")
async def proxy_forecast_generation(request: Request):
    """Proxy forecast generation endpoint"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for forecast generation"
            )
        
        # Parse request body
        body = await request.json()
        
        response_data = await proxy_request("POST", "/forecast/generate", request, json_data=body)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        if e.status_code == 401:
            raise e
        
        # Return demo forecast if API is unavailable
        logger.warning(f"API unavailable for forecast, returning demo data: {e.detail}")
        
        symbol = (await request.json()).get("symbol", "AAPL")
        demo_data = {
            "symbol": symbol,
            "forecast_price": 200.00,
            "confidence": 75.5,
            "horizon": "30 days",
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.get("/search/stocks")
async def proxy_stock_search(request: Request):
    """Proxy stock search endpoint"""
    try:
        query_params = dict(request.query_params)
        response_data = await proxy_request("GET", "/search/stocks", request, params=query_params)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        # Return demo search results if API is unavailable
        logger.warning(f"API unavailable for search, returning demo data: {e.detail}")
        
        query = request.query_params.get("q", "")
        demo_data = {
            "results": [
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "MSFT", "name": "Microsoft Corp", "exchange": "NASDAQ"},
                {"symbol": "GOOGL", "name": "Alphabet Inc", "exchange": "NASDAQ"}
            ],
            "query": query,
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.post("/alerts")
async def proxy_create_alert(request: Request):
    """Proxy alert creation endpoint"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for alerts"
            )
        
        body = await request.json()
        response_data = await proxy_request("POST", "/alerts", request, json_data=body)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        if e.status_code == 401:
            raise e
        
        # Return demo success if API is unavailable
        logger.warning(f"API unavailable for alert creation, returning demo response: {e.detail}")
        
        return JSONResponse(content={
            "message": "Alert created successfully (demo mode)",
            "alert_id": f"demo_alert_{int(datetime.now().timestamp())}",
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        })

@router.get("/user/profile")
async def proxy_user_profile(request: Request):
    """Proxy user profile endpoint"""
    try:
        # Check authentication
        if not is_authenticated(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for profile data"
            )
        
        response_data = await proxy_request("GET", "/user/profile", request)
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        if e.status_code == 401:
            raise e
        
        # Return demo profile if API is unavailable
        logger.warning(f"API unavailable for profile, returning demo data: {e.detail}")
        
        demo_data = {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "full_name": "Demo User",
            "created_at": "2025-01-01T00:00:00Z",
            "status": "demo_mode",
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(content=demo_data)

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def generic_proxy(request: Request, path: str):
    """Generic proxy for any other API endpoints"""
    try:
        method = request.method
        query_params = dict(request.query_params)
        
        # Handle request body for POST/PUT/PATCH
        json_data = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                json_data = await request.json()
            except:
                json_data = None
        
        response_data = await proxy_request(
            method=method,
            endpoint=f"/{path}",
            request=request,
            params=query_params,
            json_data=json_data
        )
        
        return JSONResponse(content=response_data)
        
    except HTTPException as e:
        # Return appropriate error response
=======
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
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
        return JSONResponse(
            content={
                "error": "API proxy error",
                "detail": str(e.detail),
                "path": path,
                "method": request.method,
                "status": "error",
                "timestamp": datetime.now().isoformat()
            },
            status_code=e.status_code
        )