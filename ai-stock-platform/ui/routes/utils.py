"""
<<<<<<< HEAD
Utility routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import requests
import os
from datetime import datetime, timedelta
import json
import re

# Setup logging
logger = logging.getLogger(__name__)

# Setup templates - use relative path from project root
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

# Create router
router = APIRouter(tags=["utilities"])

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def validate_symbol(symbol: str) -> bool:
    """Validate stock symbol format"""
    if not symbol or len(symbol) > 10:
        return False
    # Allow letters, numbers, and basic symbols
    return bool(re.match(r'^[A-Z0-9\.\-]+$', symbol.upper()))

def get_demo_ticker_info(symbol: str) -> Dict[str, Any]:
    """Generate demo ticker information"""
    # Base data on symbol for consistency
    base_price = 50 + (len(symbol) * 20) + (ord(symbol[0]) % 100)
    
    return {
        "symbol": symbol.upper(),
        "name": f"{symbol.upper()} Corporation",
        "exchange": "NASDAQ" if len(symbol) <= 4 else "NYSE",
        "sector": ["Technology", "Healthcare", "Financial", "Consumer", "Industrial"][len(symbol) % 5],
        "industry": f"{symbol} Industry",
        "price": round(base_price, 2),
        "change": round((base_price * 0.02) - 1, 2),
        "change_percent": round(((base_price * 0.02) - 1) / base_price * 100, 2),
        "volume": f"{10 + (len(symbol) % 50)}M",
        "market_cap": f"{1 + (len(symbol) % 10)}.{len(symbol) % 10}B",
        "pe_ratio": round(15 + (len(symbol) % 20), 1),
        "dividend_yield": round((len(symbol) % 5) * 0.3, 2),
        "52_week_high": round(base_price * 1.3, 2),
        "52_week_low": round(base_price * 0.7, 2),
        "beta": round(0.8 + (len(symbol) % 10) * 0.1, 2),
        "eps": round(base_price / 20, 2),
        "description": f"{symbol.upper()} Corporation is a leading company in its sector, providing innovative solutions and services.",
        "website": f"https://www.{symbol.lower()}.com",
        "employees": (len(symbol) * 5000) + 10000,
        "founded": 2000 - (len(symbol) % 30),
        "headquarters": f"{symbol} City, {['CA', 'NY', 'TX', 'WA', 'FL'][len(symbol) % 5]}"
    }

def search_demo_tickers(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search demo ticker symbols"""
    # Common stock symbols for demo
    demo_symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE", "sector": "Financial"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "sector": "Healthcare"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "sector": "Financial"},
        {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE", "sector": "Financial"},
        {"symbol": "PG", "name": "Procter & Gamble Company", "exchange": "NYSE", "sector": "Consumer Staples"},
        {"symbol": "HD", "name": "The Home Depot Inc.", "exchange": "NYSE", "sector": "Consumer Discretionary"},
        {"symbol": "CVX", "name": "Chevron Corporation", "exchange": "NYSE", "sector": "Energy"},
        {"symbol": "PFE", "name": "Pfizer Inc.", "exchange": "NYSE", "sector": "Healthcare"}
    ]
    
    query_upper = query.upper()
    results = []
    
    for stock in demo_symbols:
        if (query_upper in stock["symbol"] or 
            query_upper.lower() in stock["name"].lower()):
            results.append(stock)
            if len(results) >= limit:
                break
    
    return results

@router.get("/ticker-info")
async def get_ticker_info(
    request: Request,
    ticker: str = Query(..., description="Stock ticker symbol"),
    detailed: bool = Query(False, description="Include detailed information")
):
    """Get comprehensive information for a stock ticker"""
    try:
        # Validate ticker symbol
        ticker = ticker.upper().strip()
        if not validate_symbol(ticker):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid ticker symbol format"
            )
        
        # Try to get data from API first
        try:
            response = requests.get(
                f"{API_URL}/stocks/{ticker}",
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                api_data = response.json()
                logger.info(f"Retrieved ticker info for {ticker} from API")
                return JSONResponse(content={
                    "success": True,
                    "data": api_data,
                    "source": "api"
                })
        
        except requests.RequestException as e:
            logger.warning(f"API unavailable for ticker {ticker}: {str(e)}")
        
        # Fall back to demo data
        ticker_info = get_demo_ticker_info(ticker)
        
        if not detailed:
            # Return basic info only
            basic_info = {
                "symbol": ticker_info["symbol"],
                "name": ticker_info["name"],
                "price": ticker_info["price"],
                "change": ticker_info["change"],
                "change_percent": ticker_info["change_percent"],
                "volume": ticker_info["volume"]
            }
            return JSONResponse(content={
                "success": True,
                "data": basic_info,
                "source": "demo"
            })
        
        return JSONResponse(content={
            "success": True,
            "data": ticker_info,
            "source": "demo"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticker info for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ticker information"
        )

@router.get("/search-tickers")
async def search_tickers(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    exchange: Optional[str] = Query(None, description="Filter by exchange")
):
    """Search for ticker symbols"""
    try:
        query = query.strip()
        if len(query) < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Search query must be at least 1 character"
            )
        
        # Try API search first
        try:
            params = {"q": query, "limit": limit}
            if exchange:
                params["exchange"] = exchange
            
            response = requests.get(
                f"{API_URL}/search/stocks",
                params=params,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                api_data = response.json()
                logger.info(f"Retrieved search results for '{query}' from API")
                return JSONResponse(content={
                    "success": True,
                    "data": api_data,
                    "source": "api"
                })
        
        except requests.RequestException as e:
            logger.warning(f"API unavailable for search '{query}': {str(e)}")
        
        # Fall back to demo search
        results = search_demo_tickers(query, limit)
        
        # Filter by exchange if specified
        if exchange:
            exchange_upper = exchange.upper()
            results = [r for r in results if r.get("exchange", "").upper() == exchange_upper]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "results": results,
                "query": query,
                "total": len(results)
            },
            "source": "demo"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching tickers for '{query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )

@router.get("/validate-symbol")
async def validate_ticker_symbol(
    request: Request,
    symbol: str = Query(..., description="Symbol to validate")
):
    """Validate if a ticker symbol exists and is tradeable"""
    try:
        symbol = symbol.upper().strip()
        
        # Basic format validation
        if not validate_symbol(symbol):
            return JSONResponse(content={
                "valid": False,
                "symbol": symbol,
                "reason": "Invalid symbol format",
                "suggestions": []
            })
        
        # Try to get data from API
        try:
            response = requests.get(
                f"{API_URL}/stocks/{symbol}",
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return JSONResponse(content={
                    "valid": True,
                    "symbol": symbol,
                    "source": "api",
                    "tradeable": True
                })
            elif response.status_code == 404:
                return JSONResponse(content={
                    "valid": False,
                    "symbol": symbol,
                    "reason": "Symbol not found",
                    "suggestions": search_demo_tickers(symbol, 3)
                })
        
        except requests.RequestException:
            logger.warning(f"API unavailable for symbol validation: {symbol}")
        
        # Demo validation - accept common symbols
        common_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]
        if symbol in common_symbols:
            return JSONResponse(content={
                "valid": True,
                "symbol": symbol,
                "source": "demo",
                "tradeable": True
            })
        
        # For demo, accept any properly formatted symbol
        return JSONResponse(content={
            "valid": True,
            "symbol": symbol,
            "source": "demo",
            "tradeable": True,
            "note": "Demo mode - symbol accepted for testing"
        })
        
    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {str(e)}")
        return JSONResponse(content={
            "valid": False,
            "symbol": symbol,
            "reason": "Validation error",
            "error": str(e)
        })

@router.get("/market-hours")
async def get_market_hours(
    request: Request,
    exchange: str = Query("NYSE", description="Exchange name"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """Get market hours for a specific exchange"""
    try:
        # Demo market hours data
        market_hours = {
            "NYSE": {
                "name": "New York Stock Exchange",
                "timezone": "America/New_York",
                "regular_hours": {
                    "open": "09:30",
                    "close": "16:00"
                },
                "pre_market": {
                    "open": "04:00",
                    "close": "09:30"
                },
                "after_hours": {
                    "open": "16:00",
                    "close": "20:00"
                }
            },
            "NASDAQ": {
                "name": "NASDAQ",
                "timezone": "America/New_York",
                "regular_hours": {
                    "open": "09:30",
                    "close": "16:00"
                },
                "pre_market": {
                    "open": "04:00",
                    "close": "09:30"
                },
                "after_hours": {
                    "open": "16:00",
                    "close": "20:00"
                }
            }
        }
        
        exchange_upper = exchange.upper()
        if exchange_upper not in market_hours:
            exchange_upper = "NYSE"  # Default fallback
        
        hours_data = market_hours[exchange_upper]
        
        # Determine market status
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_minutes = current_hour * 60 + current_minute
        
        # Convert market hours to minutes for comparison
        open_minutes = 9 * 60 + 30  # 9:30 AM
        close_minutes = 16 * 60     # 4:00 PM
        
        if current_time.weekday() >= 5:  # Weekend
            market_status = "closed"
            next_open = "Monday 9:30 AM"
        elif open_minutes <= current_time_minutes <= close_minutes:
            market_status = "open"
            next_open = None
        else:
            market_status = "closed"
            if current_time_minutes < open_minutes:
                next_open = "Today 9:30 AM"
            else:
                next_open = "Tomorrow 9:30 AM"
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "exchange": exchange_upper,
                "market_hours": hours_data,
                "current_status": market_status,
                "next_open": next_open,
                "current_time": current_time.isoformat(),
                "date_requested": date or current_time.strftime("%Y-%m-%d")
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting market hours: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get market hours"
        )

@router.get("/currency-converter")
async def convert_currency(
    request: Request,
    from_currency: str = Query("USD", description="Source currency"),
    to_currency: str = Query("EUR", description="Target currency"),
    amount: float = Query(1.0, ge=0, description="Amount to convert")
):
    """Convert between currencies"""
    try:
        # Demo exchange rates
        exchange_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.45
        }
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in exchange_rates or to_currency not in exchange_rates:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unsupported currency"
            )
        
        # Convert via USD
        usd_amount = amount / exchange_rates[from_currency]
        converted_amount = usd_amount * exchange_rates[to_currency]
        
        exchange_rate = exchange_rates[to_currency] / exchange_rates[from_currency]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "original_amount": amount,
                "converted_amount": round(converted_amount, 4),
                "exchange_rate": round(exchange_rate, 6),
                "timestamp": datetime.now().isoformat(),
                "source": "demo_rates"
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting currency: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Currency conversion failed"
        )

@router.get("/financial-calendar")
async def get_financial_calendar(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    event_type: Optional[str] = Query(None, description="Filter by event type")
):
    """Get financial calendar events"""
    try:
        # Demo calendar events
        demo_events = [
            {
                "date": "2025-01-15",
                "type": "earnings",
                "company": "JPMorgan Chase",
                "symbol": "JPM",
                "event": "Q4 Earnings Release",
                "time": "Before Market Open"
            },
            {
                "date": "2025-01-16",
                "type": "earnings",
                "company": "Goldman Sachs",
                "symbol": "GS",
                "event": "Q4 Earnings Release",
                "time": "Before Market Open"
            },
            {
                "date": "2025-01-22",
                "type": "fed",
                "company": "Federal Reserve",
                "symbol": "FED",
                "event": "FOMC Meeting Minutes",
                "time": "2:00 PM EST"
            },
            {
                "date": "2025-01-28",
                "type": "earnings",
                "company": "Apple Inc.",
                "symbol": "AAPL",
                "event": "Q1 Earnings Release",
                "time": "After Market Close"
            },
            {
                "date": "2025-01-30",
                "type": "earnings",
                "company": "Microsoft Corporation",
                "symbol": "MSFT",
                "event": "Q2 Earnings Release",
                "time": "After Market Close"
            }
        ]
        
        # Filter by event type if specified
        if event_type:
            demo_events = [e for e in demo_events if e["type"].lower() == event_type.lower()]
        
        # Filter by date range if specified
        if start_date:
            demo_events = [e for e in demo_events if e["date"] >= start_date]
        
        if end_date:
            demo_events = [e for e in demo_events if e["date"] <= end_date]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "events": demo_events,
                "total": len(demo_events),
                "start_date": start_date,
                "end_date": end_date,
                "event_type": event_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting financial calendar: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get financial calendar"
        )
=======
QuantumVestAI Utility Routes
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging
from datetime import datetime
from pathlib import Path

# Setup router
router = APIRouter(prefix="/utils", tags=["utils"])
logger = logging.getLogger(__name__)

# Templates setup
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/health")
async def health_check():
    """Health check endpoint for utility service"""
    return {
        "status": "healthy",
        "service": "utils",
        "timestamp": datetime.utcnow().isoformat(),
        "demo_mode": True,
        "version": "2.0.0",
        "author": "hemanth9398"
    }

@router.get("/api/version")
async def get_version_info():
    """Get version and build information"""
    try:
        return JSONResponse({
            "status": "success",
            "version": "2.0.0",
            "author": "hemanth9398",
            "updated": "2025-07-07 21:54:42",
            "build": {
                "environment": "demo",
                "features": ["auth", "dashboard", "forecast", "market", "watchlist", "predictability", "settings"],
                "demo_mode": True
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting version info: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/api/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    try:
        metrics = {
            "performance": {
                "cpu_usage": 23.5,
                "memory_usage": 67.2,
                "disk_usage": 45.8,
                "network_io": 125.6
            },
            "application": {
                "active_sessions": 156,
                "requests_per_minute": 450,
                "avg_response_time": 145.6,
                "error_rate": 0.02
            },
            "features": {
                "predictions_generated": 12450,
                "stocks_tracked": 5000,
                "alerts_active": 2340,
                "users_online": 89
            }
        }
        
        return JSONResponse({
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
