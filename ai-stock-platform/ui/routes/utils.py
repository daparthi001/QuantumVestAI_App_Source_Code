from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
from ui.services.yahoo_finance import YahooFinanceService
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Router setup for utility endpoints
router = APIRouter(prefix="/utils", tags=["utilities"])

@router.get("/ticker-info")
async def get_ticker_info(
    ticker: str = Query(...),
    
):
    """Get basic information for a stock ticker"""
    try:
        stock_info = YahooFinanceService.get_stock_info(ticker)
        return JSONResponse(content=stock_info)
    except Exception as e:
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
    try:
        results = YahooFinanceService.search_tickers(query, limit)
        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(
            content={"error": f"Search failed: {str(e)}"},
            status_code=500
        )

@router.get("/market-indices")
async def get_market_indices(
    indices: Optional[str] = Query(None),  # Comma-separated list of index tickers
    
):
    """Get current market indices data"""
    try:
        from core.config.constants import MARKET_INDICES
        
        # If specific indices are requested, use those
        index_tickers = indices.split(",") if indices else list(MARKET_INDICES.values())
        
        results = {}
        for ticker in index_tickers:
            try:
                index_data = YahooFinanceService.get_stock_info(ticker)
                # Extract only the necessary fields for indices
                results[ticker] = {
                    "name": index_data.get("shortName", ticker),
                    "price": index_data.get("regularMarketPrice", 0),
                    "change": index_data.get("regularMarketChange", 0),
                    "change_percent": index_data.get("regularMarketChangePercent", 0),
                    "previous_close": index_data.get("regularMarketPreviousClose", 0),
                    "open": index_data.get("regularMarketOpen", 0),
                    "day_high": index_data.get("regularMarketDayHigh", 0),
                    "day_low": index_data.get("regularMarketDayLow", 0)
                }
            except:
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
    try:
        data = YahooFinanceService.get_historical_data(ticker, period, interval)
        return JSONResponse(content=data.to_dict(orient="records"))
    except Exception as e:
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
    try:
        news = YahooFinanceService.get_stock_news(ticker, limit)
        return JSONResponse(content={"news": news})
    except Exception as e:
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
    elif volume