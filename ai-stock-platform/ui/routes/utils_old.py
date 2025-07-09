from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
from ui.services.yahoo_finance import YahooFinanceService
API_URL = "http://quantumvestai-dev-api:8000"

# Router setup for utility endpoints
router = APIRouter(prefix="/utils", tags=["utilities"])

@router.get("/ticker-info")
async def get_ticker_info(
    ticker: str = Query(...),
    
):
    """Get basic information for a stock ticker"""
        return JSONResponse(
            content={"error": f"Could not retrieve ticker info: {str(e)}"},
            status_code=500
        )

@router.get("/search-tickers")
async def search_tickers(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=20),
    
):
    """Search for ticker symbols"""
        return JSONResponse(
            content={"error": f"Search failed: {str(e)}"},
            status_code=500
        )

@router.get("/market-indices")
async def get_market_indices(
    indices: Optional[str] = Query(None),  # Comma-separated list of index tickers
    
):
    """Get current market indices data"""
                results[ticker] = {"error": f"Could not retrieve data for {ticker}"}
                
        return JSONResponse(content=results)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to retrieve market indices: {str(e)}"},
            status_code=500
        )

@router.get("/historical-data")
async def get_historical_data(
    ticker: str = Query(...),
    period: str = Query("1y"),
    interval: str = Query("1d"),
    
):
    """Get historical price data for a ticker"""
        return JSONResponse(
            content={"error": f"Could not retrieve historical data: {str(e)}"},
            status_code=500
        )

@router.get("/stock-news")
async def get_stock_news(
    ticker: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    
):
    """Get news for a specific stock"""
        return JSONResponse(
            content={"error": f"Could not retrieve news: {str(e)}"},
            status_code=500
        )

# Helper functions that can be used across routes
def format_price(price: float, include_symbol: bool = True) -> str:
    """Format a price value with currency symbol"""
    if price is None:
        return "N/A"
    return f"${price:,.2f}" if include_symbol else f"{price:,.2f}"

def format_percent(percent: float, include_symbol: bool = True) -> str:
    """Format a percentage value"""
    if percent is None:
        return "N/A"
    return f"{percent:.2f}%" if include_symbol else f"{percent:.2f}"

def format_volume(volume: float) -> str:
    """Format a volume value with K, M, B suffixes"""
    if volume is None:
        return "N/A"
    
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return f"{volume:.0f}"
    elif volume:
