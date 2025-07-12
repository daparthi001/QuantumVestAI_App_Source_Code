"""
QuantumVestAI Market Routes  
Updated: 2025-07-07 21:54:42
Author: hemanth9398
"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Setup router and templates
router = APIRouter(prefix="/market", tags=["market"])
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_templates(request: Request) -> Jinja2Templates:
    """Return app-level templates if available."""
    return getattr(request.app.state, "templates", templates)

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

@router.get("/", response_class=HTMLResponse)
async def market_overview(request: Request):
    """Market overview page (demo mode)"""
    try:
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
        
        data = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "overview": {
                "status": "available",
                "indices": list(DEMO_MARKET_DATA.get("indices", {}).values()),
                "summary": {
                    "advancing": 3500,
                    "advancing_percent": 55.0,
                    "declining": 2800,
                    "declining_percent": 44.0,
                    "total_volume": 1_500_000_000,
                    "total_market_cap": 50_000_000_000_000,
                    "new_highs": 120,
                    "new_lows": 45,
                    "market_mood": 20
                }
            },
            "sectors": {
                "status": "available",
                "data": [
                    {
                        "id": name.lower().replace(" ", "-"),
                        "name": name,
                        "change_percent": info.get("change_pct"),
                        "volume": info.get("volume")
                    }
                    for name, info in DEMO_MARKET_DATA.get("sectors", {}).items()
                ]
            },
            "movers": {
                "status": "available",
                "gainers": DEMO_MARKET_DATA.get("top_movers", {}).get("gainers", []),
                "losers": DEMO_MARKET_DATA.get("top_movers", {}).get("losers", [])
            },
            "sentiment": None,
            "user": None
        }

        return get_templates(request).TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "demo_mode": True,
                "data": data,
                "market_news": market_news,
                "page_title": "Market Overview - QuantumVestAI"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading market overview: {str(e)}")
        return get_templates(request).TemplateResponse(
            "market/overview.html",
            {
                "request": request,
                "demo_mode": True,
                "data": {
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "overview": None,
                    "sectors": None,
                    "movers": None,
                    "sentiment": None,
                    "user": None,
                },
                "market_news": [],
                "error": "Failed to load market data",
                "page_title": "Market Overview Error",
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
        
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
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
):
    """Market sentiment page"""
    try:
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
        
        return get_templates(request).TemplateResponse(
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
        return get_templates(request).TemplateResponse(
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
