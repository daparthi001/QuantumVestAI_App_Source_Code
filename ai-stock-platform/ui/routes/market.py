"""
<<<<<<< HEAD
Market data routes for QuantumVestAI UI
Updated: 2025-07-07 21:49:53
=======
QuantumVestAI Market Routes  
Updated: 2025-07-07 21:54:42
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
Author: hemanth9398
"""

from fastapi import APIRouter, Request, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
<<<<<<< HEAD
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

=======
from typing import Optional, List
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup router and templates
router = APIRouter(prefix="/market", tags=["market"])
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Demo market data
DEMO_MARKET_DATA = {
    "indices": {
        "S&P 500": {
            "symbol": "^GSPC",
            "name": "S&P 500",
            "value": 4567.89,
            "change": 23.45,
            "change_pct": 0.52,
            "volume": "3.2B",
            "high_52w": 4650.00,
            "low_52w": 3800.00
        },
        "NASDAQ": {
            "symbol": "^IXIC", 
            "name": "NASDAQ Composite",
            "value": 14234.56,
            "change": -45.67,
            "change_pct": -0.32,
            "volume": "4.1B",
            "high_52w": 15500.00,
            "low_52w": 12000.00
        },
        "DOW": {
            "symbol": "^DJI",
            "name": "Dow Jones Industrial Average", 
            "value": 34567.12,
            "change": 156.78,
            "change_pct": 0.46,
            "volume": "345M",
            "high_52w": 36800.00,
            "low_52w": 32000.00
        }
    },
    "sectors": {
        "Technology": {"change_pct": 1.2, "leader": "AAPL", "volume": "15.2B"},
        "Healthcare": {"change_pct": -0.3, "leader": "JNJ", "volume": "8.1B"},
        "Finance": {"change_pct": 0.8, "leader": "JPM", "volume": "12.5B"},
        "Energy": {"change_pct": 2.1, "leader": "XOM", "volume": "9.8B"},
        "Consumer Discretionary": {"change_pct": 0.5, "leader": "AMZN", "volume": "11.3B"},
        "Consumer Staples": {"change_pct": -0.1, "leader": "PG", "volume": "5.7B"}
    },
    "top_movers": {
        "gainers": [
            {"symbol": "NVDA", "name": "NVIDIA Corp", "price": 245.67, "change": 12.34, "change_pct": 5.2, "volume": "45.2M"},
            {"symbol": "TSLA", "name": "Tesla Inc", "price": 189.34, "change": 6.92, "change_pct": 3.8, "volume": "87.3M"},
            {"symbol": "AMZN", "name": "Amazon.com Inc", "price": 145.23, "change": 4.18, "change_pct": 2.9, "volume": "41.5M"},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "price": 98.76, "change": 2.85, "change_pct": 2.9, "volume": "52.1M"},
            {"symbol": "NFLX", "name": "Netflix Inc", "price": 423.67, "change": 11.23, "change_pct": 2.7, "volume": "12.8M"}
        ],
        "losers": [
            {"symbol": "META", "name": "Meta Platforms Inc", "price": 298.45, "change": -6.45, "change_pct": -2.1, "volume": "34.7M"},
            {"symbol": "GOOGL", "name": "Alphabet Inc", "price": 134.56, "change": -1.62, "change_pct": -1.2, "volume": "32.1M"},
            {"symbol": "MSFT", "name": "Microsoft Corp", "price": 365.25, "change": -1.75, "change_pct": -0.48, "volume": "28.7M"},
            {"symbol": "AAPL", "name": "Apple Inc", "price": 185.50, "change": -0.95, "change_pct": -0.51, "volume": "45.2M"},
            {"symbol": "JPM", "name": "JPMorgan Chase", "price": 156.89, "change": -0.78, "change_pct": -0.49, "volume": "15.3M"}
        ]
    }
}

DEMO_STOCKS_DB = {
    "AAPL": {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 185.50,
        "change": 2.25,
        "change_pct": 1.23,
        "volume": "45.2M",
        "market_cap": "2.89T",
        "pe_ratio": 28.5,
        "eps": 6.51,
        "dividend_yield": 0.44,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "description": "Technology company that designs, develops, and sells consumer electronics, computer software, and online services."
    },
    "MSFT": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation", 
        "price": 365.25,
        "change": -1.75,
        "change_pct": -0.48,
        "volume": "28.7M",
        "market_cap": "2.71T",
        "pe_ratio": 31.2,
        "eps": 11.70,
        "dividend_yield": 0.72,
        "sector": "Technology", 
        "industry": "Software—Infrastructure",
        "description": "Technology corporation that develops, manufactures, licenses, supports, and sells computer software, consumer electronics, and personal computers."
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "price": 134.56,
        "change": 3.42,
        "change_pct": 2.61,
        "volume": "32.1M",
        "market_cap": "1.68T",
        "pe_ratio": 25.8,
        "eps": 5.21,
        "dividend_yield": 0.00,
        "sector": "Communication Services",
        "industry": "Internet Content & Information",
        "description": "Multinational technology company that specializes in Internet-related services and products."
    },
    "TSLA": {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "price": 189.34,
        "change": 6.92,
        "change_pct": 3.79,
        "volume": "87.3M",
        "market_cap": "601.2B",
        "pe_ratio": 45.6,
        "eps": 4.15,
        "dividend_yield": 0.00,
        "sector": "Consumer Cyclical",
        "industry": "Auto Manufacturers",
        "description": "Electric vehicle and clean energy company that designs, develops, manufactures, leases, and sells electric vehicles."
    }
}

>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
@router.get("/", response_class=HTMLResponse)
async def market_overview(request: Request):
    """Main market overview page"""
    try:
<<<<<<< HEAD
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
=======
        logger.info("Loading market overview in demo mode")
        
        # Market news
        market_news = [
            {
                "title": "Markets Rally on Strong Economic Data",
                "summary": "U.S. markets posted strong gains as economic indicators show continued growth momentum.",
                "source": "MarketWatch",
                "published_at": "2025-07-07T20:30:00Z",
                "sentiment": "positive"
            },
            {
                "title": "Tech Stocks Lead Market Higher",
                "summary": "Technology sector outperforms as AI adoption accelerates across industries.",
                "source": "CNBC", 
                "published_at": "2025-07-07T19:15:00Z",
                "sentiment": "positive"
            },
            {
                "title": "Federal Reserve Policy Update",
                "summary": "Fed maintains current interest rate stance amid stable inflation trends.",
                "source": "Reuters",
                "published_at": "2025-07-07T18:00:00Z",
                "sentiment": "neutral"
            }
        ]
        
        return templates.TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "demo_mode": True,
                "market_data": DEMO_MARKET_DATA,
                "market_news": market_news,
                "page_title": "Market Overview - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading market overview: {str(e)}")
        return templates.TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "demo_mode": True,
                "market_data": {"indices": {}, "sectors": {}, "top_movers": {}},
                "market_news": [],
                "error": "Failed to load market data",
                "page_title": "Market Overview Error"
            },
            status_code=500
        )

@router.get("/ticker/{ticker}", response_class=HTMLResponse)
async def ticker_details(
    request: Request,
    ticker: str,
    period: str = Query("1d", description="Time period: 1d, 5d, 1m, 3m, 6m, 1y")
):
    """Ticker details page"""
    try:
        ticker = ticker.upper()
        logger.info(f"Loading ticker details for {ticker}")
        
        # Get stock data
        if ticker in DEMO_STOCKS_DB:
            stock_data = DEMO_STOCKS_DB[ticker]
        else:
            # Generate demo data for any ticker
            stock_data = {
                "symbol": ticker,
                "name": f"{ticker} Corporation",
                "price": 100.00,
                "change": 1.50,
                "change_pct": 1.52,
                "volume": "10.5M",
                "market_cap": "500.0B",
                "pe_ratio": 22.5,
                "eps": 4.44,
                "dividend_yield": 1.25,
                "sector": "Technology",
                "industry": "Software",
                "description": f"{ticker} is a leading company in its sector."
            }
        
        # Generate chart data
        chart_data = []
        base_price = stock_data["price"]
        days = {"1d": 1, "5d": 5, "1m": 30, "3m": 90, "6m": 180, "1y": 365}.get(period, 30)
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime("%Y-%m-%d")
            price = base_price * (0.95 + (i * 0.003) + (0.02 * (i % 7 - 3) / 10))
            chart_data.append({
                "date": date,
                "price": round(price, 2),
                "volume": int(10000000 + (i * 50000))
            })
        
        # Technical indicators
        technical_indicators = {
            "rsi": 65.4,
            "macd": 2.15,
            "bb_upper": stock_data["price"] * 1.05,
            "bb_lower": stock_data["price"] * 0.95,
            "ma_20": stock_data["price"] * 0.98,
            "ma_50": stock_data["price"] * 0.96
        }
        
        return templates.TemplateResponse(
            "market/ticker_detail.html",
            {
                "request": request,
                "ticker": ticker,
                "period": period,
                "demo_mode": True,
                "stock_data": stock_data,
                "chart_data": chart_data,
                "technical_indicators": technical_indicators,
                "page_title": f"{ticker} - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading ticker details for {ticker}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": f"Unable to load data for {ticker}",
                "page_title": "Ticker Error"
            },
            status_code=500
        )

@router.get("/search")
async def ticker_search(
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
    request: Request,
    category: str = Query("all", description="Data category: all, indices, sectors, movers")
):
<<<<<<< HEAD
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
=======
    """Search for ticker symbols"""
    try:
        query = q.upper()
        results = []
        
        # Search in demo database
        for symbol, data in DEMO_STOCKS_DB.items():
            if query in symbol or query in data["name"].upper():
                results.append({
                    "symbol": symbol,
                    "name": data["name"],
                    "price": data["price"],
                    "change_pct": data["change_pct"],
                    "sector": data["sector"]
                })
        
        # Add generic results if not found
        if not results and len(query) >= 2:
            for i in range(min(3, limit)):
                results.append({
                    "symbol": f"{query}{i+1}",
                    "name": f"{query} Corporation {i+1}",
                    "price": 100.00 + i * 10,
                    "change_pct": (i - 1) * 0.5,
                    "sector": "Technology"
                })
        
        return JSONResponse({
            "status": "success",
            "results": results[:limit],
            "query": q,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in ticker search: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/sentiment", response_class=HTMLResponse)
async def market_sentiment(
    request: Request,
    period: str = Query("1w", description="Time period: 1d, 1w, 1m")
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
):
    """API endpoint for market news"""
    try:
<<<<<<< HEAD
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
=======
        sentiment_data = {
            "overall_sentiment": {
                "score": 72,
                "trend": "bullish",
                "confidence": 0.74,
                "change_24h": 3.2
            },
            "sector_sentiment": {
                "Technology": {"score": 78, "trend": "bullish", "volume": "high"},
                "Healthcare": {"score": 65, "trend": "neutral", "volume": "medium"},
                "Finance": {"score": 70, "trend": "bullish", "volume": "high"},
                "Energy": {"score": 82, "trend": "very_bullish", "volume": "very_high"},
                "Consumer": {"score": 68, "trend": "neutral", "volume": "medium"}
            },
            "news_sentiment": {
                "positive": 58,
                "neutral": 32, 
                "negative": 10
            },
            "fear_greed_index": 67,
            "vix": 18.5
        }
        
        return templates.TemplateResponse(
            "market/sentiment.html",
            {
                "request": request,
                "period": period,
                "demo_mode": True,
                "sentiment_data": sentiment_data,
                "page_title": "Market Sentiment - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading market sentiment: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Unable to load market sentiment data",
                "page_title": "Market Sentiment Error"
            },
            status_code=500
        )

@router.get("/api/data")
async def market_data_api(request: Request):
    """API endpoint for market data"""
    try:
        return JSONResponse({
            "status": "success",
            "data": DEMO_MARKET_DATA,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting market data API: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)

@router.get("/api/movers")
async def market_movers_api(
    request: Request,
    type: str = Query("gainers", description="Type: gainers, losers, active")
):
    """API endpoint for market movers"""
    try:
        if type in DEMO_MARKET_DATA["top_movers"]:
            data = DEMO_MARKET_DATA["top_movers"][type]
        else:
            data = DEMO_MARKET_DATA["top_movers"]["gainers"]
        
        return JSONResponse({
            "status": "success",
            "movers": data,
            "type": type,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market movers: {str(e)}")
        return JSONResponse({
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, status_code=500)
>>>>>>> af1ea02c566412749467c62f0937995df3769a5c
