import yfinance as yf
from fastapi import APIRouter, Request, Query, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from ui.routes.auth import get_current_user
from core.config.settings import settings
from core.config.constants import (
    MODEL_ENSEMBLE, DEFAULT_FORECAST_DAYS, DEFAULT_TICKERS,
    MAX_FORECAST_DAYS, TECHNICAL_INDICATORS
)
from ui.services.api_client import APIClient
from ui.services.yahoo_finance import YahooFinanceService

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["forecast"])

@router.get("/ticker-search", response_class=HTMLResponse)
async def ticker_search_page(
    request: Request, 
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Render ticker search page"""
    return templates.TemplateResponse(
        "ticker_search.html", 
        {
            "request": request,
            "user": current_user,
            "popular_tickers": DEFAULT_TICKERS
        }
    )

@router.get("/ticker-suggestions", response_class=JSONResponse)
async def ticker_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=20)
):
    """Search for ticker symbols"""
    try:
        # Use YahooFinanceService to search for tickers
        results = YahooFinanceService.search_tickers(query, limit)
        return JSONResponse(content={"results": results})
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/forecast", response_class=HTMLResponse)
async def forecast_page(
    request: Request,
    ticker: str = Query(...),
    days: int = Query(DEFAULT_FORECAST_DAYS, ge=1, le=MAX_FORECAST_DAYS),
    model: str = Query(MODEL_ENSEMBLE),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Render stock forecast page"""
    try:
        # Get stock info using YahooFinanceService
        stock_info = YahooFinanceService.get_stock_info(ticker)
        
        # Get historical data for chart
        historical_data = YahooFinanceService.get_historical_data(ticker, period="1y")
        
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
        
        # Call forecast API
        forecast_data = api_client.get(
            "/api/forecast",
            params={"ticker": ticker, "days": days, "model": model}
        )
        
        # Get technical indicators
        technical_indicators = {}
        try:
            indicators_data = api_client.get(
                "/api/technical/indicators",
                params={"ticker": ticker, "indicators": ",".join(TECHNICAL_INDICATORS[:4])}
            )
            technical_indicators = indicators_data.get("indicators", {})
        except:
            # If indicators fail, continue without them
            pass
            
        # Get news for the stock
        news = YahooFinanceService.get_stock_news(ticker, limit=5)
        
        # Render template with forecast data
        return templates.TemplateResponse(
            "forecast.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "stock_info": stock_info,
                "days": days,
                "model": model,
                "forecast": forecast_data,
                "historical_data": historical_data.to_dict(orient="records") if not historical_data.empty else [],
                "technical_indicators": technical_indicators,
                "news": news
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "forecast.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "days": days,
                "model": model,
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/compare-models", response_class=HTMLResponse)
async def model_comparison_page(
    request: Request,
    ticker: str = Query(...),
    days: int = Query(DEFAULT_FORECAST_DAYS, ge=1, le=MAX_FORECAST_DAYS),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Render model comparison page"""
    try:
        # Get stock info
        stock_info = YahooFinanceService.get_stock_info(ticker)
        
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
        
        # Call comparison API
        comparison_data = api_client.get(
            "/api/forecast/compare",
            params={"ticker": ticker, "days": days}
        )
        
        # Render template with comparison data
        return templates.TemplateResponse(
            "model_comparison.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "days": days,
                "stock_info": stock_info,
                "comparison": comparison_data
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "model_comparison.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "days": days,
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/technical-analysis", response_class=HTMLResponse)
async def technical_analysis_page(
    request: Request,
    ticker: str = Query(...),
    timeframe: str = Query("1y"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Render technical analysis page"""
    try:
        # Get stock info
        stock_info = YahooFinanceService.get_stock_info(ticker)
        
        # Get historical data
        historical_data = YahooFinanceService.get_historical_data(ticker, period=timeframe)
        
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
        
        # Get technical indicators
        technical_data = api_client.get(
            "/api/technical/analysis",
            params={"ticker": ticker, "timeframe": timeframe}
        )
        
        # Render template with technical analysis data
        return templates.TemplateResponse(
            "technical_analysis.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "timeframe": timeframe,
                "stock_info": stock_info,
                "historical_data": historical_data.to_dict(orient="records") if not historical_data.empty else [],
                "technical_data": technical_data
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "technical_analysis.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "timeframe": timeframe,
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/backtest", response_class=HTMLResponse)
async def backtest_page(
    request: Request,
    ticker: str = Query(...),
    model: str = Query(MODEL_ENSEMBLE),
    period: str = Query("1y"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Render backtest analysis page"""
    # Check if user is logged in - backtest is a premium feature
    if not current_user:
        return RedirectResponse(url=f"/login?next=/backtest?ticker={ticker}", status_code=status.HTTP_303_SEE_OTHER)
    
    try:
        # Get stock info
        stock_info = YahooFinanceService.get_stock_info(ticker)
        
        # Create API client with auth token
        api_client = APIClient(token=request.cookies.get("token"))
        
        # Call backtest API
        backtest_data = api_client.get(
            "/api/forecast/backtest",
            params={"ticker": ticker, "model": model, "period": period}
        )
        
        # Render template with backtest data
        return templates.TemplateResponse(
            "backtest.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "model": model,
                "period": period,
                "stock_info": stock_info,
                "backtest": backtest_data
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "backtest.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "model": model,
                "period": period,
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )