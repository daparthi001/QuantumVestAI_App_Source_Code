"""
Market data routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
import requests
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

# Setup logging
logger = logging.getLogger(__name__)

# Setup templates - use relative path from project root
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API configuration
API_URL = os.getenv("API_URL", "http://quantumvestai-dev-api:8000/api/v1")

# Create router
router = APIRouter(tags=["market"])

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    auth_cookie = request.cookies.get("access_token")
    return bool(auth_cookie)

def get_user_from_request(request: Request) -> Optional[Dict]:
    """Extract user info from request"""
    if is_authenticated(request):
        return {
            "username": "demo",
            "email": "demo@quantumvestai.com",
            "role": "user",
            "is_authenticated": True
        }
    return None

def get_demo_market_data() -> Dict[str, Any]:
    """Generate comprehensive demo market data"""
    return {
        "market_indices": [
            {
                "symbol": "SPY",
                "name": "SPDR S&P 500 ETF",
                "price": 458.32,
                "change": 2.45,
                "change_percent": 0.54,
                "volume": "52.3M",
                "market_cap": "427.8B",
                "pe_ratio": 20.45,
                "dividend_yield": 1.47
            },
            {
                "symbol": "QQQ",
                "name": "Invesco QQQ ETF",
                "price": 391.87,
                "change": -1.23,
                "change_percent": -0.31,
                "volume": "34.7M",
                "market_cap": "265.4B",
                "pe_ratio": 25.68,
                "dividend_yield": 0.62
            },
            {
                "symbol": "IWM",
                "name": "iShares Russell 2000 ETF",
                "price": 198.45,
                "change": 0.87,
                "change_percent": 0.44,
                "volume": "18.9M",
                "market_cap": "14.2B",
                "pe_ratio": 18.92,
                "dividend_yield": 1.83
            },
            {
                "symbol": "DIA",
                "name": "SPDR Dow Jones ETF",
                "price": 375.23,
                "change": 1.54,
                "change_percent": 0.41,
                "volume": "3.2M",
                "market_cap": "28.7B",
                "pe_ratio": 22.15,
                "dividend_yield": 1.92
            }
        ],
        "sector_performance": [
            {"sector": "Technology", "change_percent": 1.87, "leader": "AAPL"},
            {"sector": "Healthcare", "change_percent": 0.45, "leader": "JNJ"},
            {"sector": "Financial", "change_percent": -0.23, "leader": "JPM"},
            {"sector": "Consumer Discretionary", "change_percent": 1.12, "leader": "AMZN"},
            {"sector": "Industrial", "change_percent": 0.78, "leader": "CAT"},
            {"sector": "Communication Services", "change_percent": -0.65, "leader": "GOOGL"},
            {"sector": "Consumer Staples", "change_percent": 0.33, "leader": "PG"},
            {"sector": "Energy", "change_percent": -1.45, "leader": "XOM"},
            {"sector": "Utilities", "change_percent": 0.12, "leader": "NEE"},
            {"sector": "Real Estate", "change_percent": -0.87, "leader": "AMT"},
            {"sector": "Materials", "change_percent": 0.56, "leader": "LIN"}
        ],
        "market_movers": {
            "gainers": [
                {"symbol": "NVDA", "name": "NVIDIA Corp", "change_percent": 4.87, "price": 875.42},
                {"symbol": "AMD", "name": "Advanced Micro Devices", "change_percent": 3.45, "price": 142.87},
                {"symbol": "GOOGL", "name": "Alphabet Inc", "change_percent": 2.46, "price": 142.56},
                {"symbol": "AAPL", "name": "Apple Inc", "change_percent": 1.87, "price": 182.31},
                {"symbol": "CRM", "name": "Salesforce Inc", "change_percent": 1.76, "price": 248.95}
            ],
            "losers": [
                {"symbol": "TSLA", "name": "Tesla Inc", "change_percent": -3.21, "price": 238.45},
                {"symbol": "NFLX", "name": "Netflix Inc", "change_percent": -2.87, "price": 485.67},
                {"symbol": "META", "name": "Meta Platforms", "change_percent": -1.95, "price": 511.24},
                {"symbol": "AMZN", "name": "Amazon.com Inc", "change_percent": -1.43, "price": 153.32},
                {"symbol": "MSFT", "name": "Microsoft Corp", "change_percent": -0.87, "price": 378.85}
            ]
        },
        "market_stats": {
            "total_volume": "4.2B",
            "advancing_stocks": 2847,
            "declining_stocks": 1923,
            "unchanged_stocks": 230,
            "new_highs": 145,
            "new_lows": 67,
            "volatility_index": 18.45,
            "fear_greed_index": 62
        }
    }

def get_demo_commodity_data() -> List[Dict[str, Any]]:
    """Generate demo commodity and forex data"""
    return [
        {
            "symbol": "GC=F",
            "name": "Gold",
            "price": 2023.45,
            "change": 12.87,
            "change_percent": 0.64,
            "unit": "USD/oz"
        },
        {
            "symbol": "CL=F", 
            "name": "Crude Oil",
            "price": 78.92,
            "change": -1.23,
            "change_percent": -1.53,
            "unit": "USD/barrel"
        },
        {
            "symbol": "SI=F",
            "name": "Silver", 
            "price": 24.87,
            "change": 0.45,
            "change_percent": 1.84,
            "unit": "USD/oz"
        },
        {
            "symbol": "EURUSD=X",
            "name": "EUR/USD",
            "price": 1.0876,
            "change": 0.0023,
            "change_percent": 0.21,
            "unit": "Rate"
        },
        {
            "symbol": "GBPUSD=X",
            "name": "GBP/USD",
            "price": 1.2645,
            "change": -0.0087,
            "change_percent": -0.68,
            "unit": "Rate"
        },
        {
            "symbol": "USDJPY=X",
            "name": "USD/JPY",
            "price": 149.23,
            "change": 0.67,
            "change_percent": 0.45,
            "unit": "Rate"
        }
    ]

def get_demo_market_news() -> List[Dict[str, Any]]:
    """Generate demo market news"""
    return [
        {
            "title": "Federal Reserve Signals Potential Rate Cuts Amid Economic Concerns",
            "summary": "Fed officials indicate a more accommodative monetary policy stance as economic data shows mixed signals.",
            "source": "Reuters",
            "timestamp": "2 hours ago",
            "category": "Federal Reserve",
            "impact": "high"
        },
        {
            "title": "Technology Earnings Season Kicks Off with Mixed Results",
            "summary": "Major tech companies report quarterly earnings with varied performance across the sector.",
            "source": "Bloomberg",
            "timestamp": "4 hours ago", 
            "category": "Earnings",
            "impact": "medium"
        },
        {
            "title": "AI Revolution Continues to Drive Market Optimism",
            "summary": "Artificial intelligence developments fuel investor confidence in technology and innovation stocks.",
            "source": "CNBC",
            "timestamp": "6 hours ago",
            "category": "Technology",
            "impact": "medium"
        },
        {
            "title": "Global Supply Chain Tensions Ease as Trade Routes Stabilize",
            "summary": "International shipping and logistics companies report improved conditions and reduced delays.",
            "source": "Financial Times",
            "timestamp": "8 hours ago",
            "category": "Global Trade", 
            "impact": "low"
        },
        {
            "title": "Energy Sector Faces Headwinds from Renewable Transition",
            "summary": "Traditional energy companies adapt business models as renewable energy adoption accelerates.",
            "source": "Wall Street Journal",
            "timestamp": "12 hours ago",
            "category": "Energy",
            "impact": "medium"
        }
    ]

@router.get("/", response_class=HTMLResponse)
async def market_overview(request: Request):
    """Main market overview page"""
    try:
        user = get_user_from_request(request)
        market_data = get_demo_market_data()
        commodity_data = get_demo_commodity_data()
        market_news = get_demo_market_news()
        
        # Market summary statistics
        market_summary = {
            "market_sentiment": "Bullish",
            "volatility_level": "Moderate",
            "trading_volume": "Above Average",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
        }
        
        context = {
            "request": request,
            "user": user,
            "market_data": market_data,
            "commodities": commodity_data,
            "news": market_news,
            "summary": market_summary,
            "page_title": "Market Overview - QuantumVestAI",
            "active_page": "market"
        }
        
        return templates.TemplateResponse("market/overview.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering market overview: {str(e)}")
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Market Overview Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Market Data Unavailable</h2>
                                    <p class="card-text">We're experiencing technical difficulties loading market data.</p>
                                    <div class="mt-3">
                                        <a href="/dashboard" class="btn btn-primary">Return to Dashboard</a>
                                        <a href="/" class="btn btn-secondary">Go Home</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.get("/sectors", response_class=HTMLResponse)
async def sector_analysis(request: Request):
    """Sector analysis page"""
    try:
        user = get_user_from_request(request)
        market_data = get_demo_market_data()
        
        # Enhanced sector data
        sector_details = []
        for sector in market_data["sector_performance"]:
            sector_details.append({
                "name": sector["sector"],
                "change_percent": sector["change_percent"],
                "leader": sector["leader"],
                "market_cap": f"${12.5 + len(sector['sector'])}T",  # Mock calculation
                "pe_ratio": 18.5 + (len(sector["sector"]) % 10),
                "dividend_yield": 1.2 + (len(sector["sector"]) % 5) * 0.3,
                "top_stocks": [
                    {"symbol": sector["leader"], "change": sector["change_percent"]},
                    {"symbol": f"{sector['leader'][:-1]}B", "change": sector["change_percent"] - 0.5},
                    {"symbol": f"{sector['leader'][:-1]}C", "change": sector["change_percent"] + 0.3}
                ]
            })
        
        context = {
            "request": request,
            "user": user,
            "sectors": sector_details,
            "page_title": "Sector Analysis - QuantumVestAI",
            "active_page": "market"
        }
        
        return templates.TemplateResponse("market/sectors.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering sector analysis: {str(e)}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sector Analysis Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Sector Analysis Unavailable</h2>
                                    <p class="card-text">Unable to load sector analysis at this time.</p>
                                    <div class="mt-3">
                                        <a href="/market" class="btn btn-primary">Back to Market</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.get("/commodities", response_class=HTMLResponse)
async def commodities_page(request: Request):
    """Commodities and forex page"""
    try:
        user = get_user_from_request(request)
        commodity_data = get_demo_commodity_data()
        
        # Separate commodities and forex
        commodities = [item for item in commodity_data if not item["symbol"].endswith("=X")]
        forex = [item for item in commodity_data if item["symbol"].endswith("=X")]
        
        context = {
            "request": request,
            "user": user,
            "commodities": commodities,
            "forex": forex,
            "page_title": "Commodities & Forex - QuantumVestAI",
            "active_page": "market"
        }
        
        return templates.TemplateResponse("market/commodities.html", context)
        
    except Exception as e:
        logger.error(f"Error rendering commodities page: {str(e)}")
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Commodities Error - QuantumVestAI</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h2 class="card-title text-danger">Commodities Data Unavailable</h2>
                                    <p class="card-text">Unable to load commodities and forex data.</p>
                                    <div class="mt-3">
                                        <a href="/market" class="btn btn-primary">Back to Market</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )

@router.get("/api/data")
async def market_data_api(
    request: Request,
    category: str = Query("all", description="Data category: all, indices, sectors, movers")
):
    """API endpoint for market data"""
    try:
        market_data = get_demo_market_data()
        
        if category == "indices":
            response_data = {"indices": market_data["market_indices"]}
        elif category == "sectors":
            response_data = {"sectors": market_data["sector_performance"]}
        elif category == "movers":
            response_data = {"movers": market_data["market_movers"]}
        else:
            response_data = market_data
        
        return JSONResponse(content={
            "success": True,
            "data": response_data,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in market data API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve market data"
        )

@router.get("/api/news")
async def market_news_api(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Number of news items"),
    category: str = Query("all", description="News category filter")
):
    """API endpoint for market news"""
    try:
        news_data = get_demo_market_news()
        
        # Filter by category if specified
        if category != "all":
            news_data = [item for item in news_data if item.get("category", "").lower() == category.lower()]
        
        # Limit results
        news_data = news_data[:limit]
        
        return JSONResponse(content={
            "success": True,
            "data": news_data,
            "count": len(news_data),
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in market news API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve market news"
        )

@router.get("/api/search")
async def market_search(
    request: Request,
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search market instruments"""
    try:
        query = query.upper().strip()
        
        # Demo search results
        all_instruments = [
            {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corp", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com Inc", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla Inc", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corp", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms", "type": "stock", "exchange": "NASDAQ"},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "type": "etf", "exchange": "NYSE"},
            {"symbol": "QQQ", "name": "Invesco QQQ ETF", "type": "etf", "exchange": "NASDAQ"},
            {"symbol": "GC=F", "name": "Gold Futures", "type": "commodity", "exchange": "COMEX"}
        ]
        
        # Filter results based on query
        results = []
        for instrument in all_instruments:
            if (query in instrument["symbol"] or 
                query.lower() in instrument["name"].lower()):
                results.append(instrument)
                if len(results) >= limit:
                    break
        
        return JSONResponse(content={
            "success": True,
            "data": results,
            "query": query,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in market search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Search failed"
        )

@router.get("/api/quote/{symbol}")
async def get_quote(request: Request, symbol: str):
    """Get real-time quote for a symbol"""
    try:
        symbol = symbol.upper().strip()
        
        # Demo quote data
        quotes = {
            "AAPL": {"price": 182.31, "change": 1.87, "change_percent": 1.04, "volume": "45.2M"},
            "MSFT": {"price": 378.85, "change": -2.15, "change_percent": -0.56, "volume": "28.7M"},
            "GOOGL": {"price": 142.56, "change": 3.42, "change_percent": 2.46, "volume": "32.1M"},
            "AMZN": {"price": 153.32, "change": 0.95, "change_percent": 0.62, "volume": "41.8M"},
            "TSLA": {"price": 238.45, "change": -4.67, "change_percent": -1.92, "volume": "67.3M"}
        }
        
        if symbol not in quotes:
            # Generate random quote for unknown symbols
            base_price = 100 + (len(symbol) * 10)
            quotes[symbol] = {
                "price": base_price,
                "change": round((base_price * 0.02) - 1, 2),
                "change_percent": round(((base_price * 0.02) - 1) / base_price * 100, 2),
                "volume": f"{15 + (len(symbol) % 5)}M"
            }
        
        quote_data = quotes[symbol]
        quote_data.update({
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "market_status": "open" if 9 <= datetime.now().hour <= 16 else "closed"
        })
        
        return JSONResponse(content={
            "success": True,
            "data": quote_data
        })
        
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quote for {symbol}"
        )