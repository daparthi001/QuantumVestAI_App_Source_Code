from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
# Fix the import to use the local namespace
from routes.auth import get_current_user
from config.settings import settings
# Fix the import to use the local namespace
from services.api_client import APIClient
from services.yahoo_finance import YahooFinanceService
API_URL = "http://quantumvestai-dev-api:8000/api/v1"

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router setup
router = APIRouter(tags=["predictability"])

@router.get("/predictability", response_class=HTMLResponse)
async def predictability_page(
    request: Request, 
    ticker: str = Query(default="AAPL"), 
    timeframe: str = Query(default="1y"),
    model: str = Query(default="all"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Render the stock predictability analysis page
    """
    try:
        # Get stock info
        stock_info = YahooFinanceService.get_stock_info(ticker)
        
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
        
        # Call the predictability API
        predictability_data = api_client.get(
            "/api/predictability",
            params={"ticker": ticker, "timeframe": timeframe, "model": model}
        )
        
        # Get historical data for comparison
        historical_data = YahooFinanceService.get_historical_data(ticker, period=timeframe)
        
        # Render template with predictability data
        return templates.TemplateResponse(
            "predictability.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "timeframe": timeframe,
                "model": model,
                "stock_info": stock_info,
                "historical_data": historical_data.to_dict(orient="records") if not historical_data.empty else [],
                **predictability_data  # Unpack all API data into template context
            }
        )
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
        
        # Return template with error
        return templates.TemplateResponse(
            "predictability.html", 
            {
                "request": request,
                "user": current_user,
                "ticker": ticker,
                "timeframe": timeframe,
                "model": model,
                "error": error_message,
                # Default values for visualization
                "predictability_score": 78,  
                "volatility_score": 65,
                "pattern_score": 83,
                "stability_score": 75,
                "correlation_score": 88,
                "sentiment_score": 70,
                "model_accuracies": {
                    "lstm": 76,
                    "prophet": 82,
                    "xgboost": 79,
                    "ensemble": 85
                },
                "volatility_metrics": {"std_dev": "N/A", "atr": "N/A", "beta": "N/A"},
                "pattern_metrics": {"clarity": "N/A", "frequency": "N/A", "completion_rate": "N/A"},
                "stability_metrics": {"trend_strength": "N/A", "ma_crossovers": "N/A", "trend_duration": "N/A"},
                "correlation_metrics": {"sp500": "N/A", "sector": "N/A", "stability": "N/A"},
                "sentiment_distribution": {"positive": 60, "neutral": 30, "negative": 10}
            }
        )

@router.get("/predictability/ranking", response_class=HTMLResponse)
async def predictability_ranking_page(
    request: Request,
    sector: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=5, le=50),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Render the predictability ranking page
    """
    try:
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
            
        # Prepare query parameters
        params = {"limit": limit}
        if sector:
            params["sector"] = sector
            
        # Call the predictability ranking API
        ranking_data = api_client.get(
            "/api/predictability/ranking",
            params=params
        )
        
        # Get available sectors for filter
        sectors = api_client.get("/api/market/sectors")
        
        # Render template with ranking data
        return templates.TemplateResponse(
            "predictability_ranking.html", 
            {
                "request": request,
                "user": current_user,
                "sector": sector,
                "sectors": sectors,
                "limit": limit,
                **ranking_data
            }
        )
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
                
        # Try to get sectors list even if ranking fails
        sectors = []
        try:
            token = request.cookies.get("token") if current_user else None
            api_client = APIClient(token=token)
            sectors = api_client.get("/api/market/sectors")
        except:
            pass
        
        # Return template with error
        return templates.TemplateResponse(
            "predictability_ranking.html", 
            {
                "request": request,
                "user": current_user,
                "sector": sector,
                "sectors": sectors,
                "limit": limit,
                "rankings": [],
                "error": error_message
            }
        )

@router.get("/predictability/compare", response_class=HTMLResponse)
async def predictability_comparison_page(
    request: Request,
    tickers: str = Query(...),  # Comma-separated list of tickers
    timeframe: str = Query(default="1y"),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    Render the predictability comparison page for multiple stocks
    """
    try:
        # Split ticker string into list
        ticker_list = [t.strip() for t in tickers.split(",")]
        
        # Create API client with auth token if available
        token = request.cookies.get("token") if current_user else None
        api_client = APIClient(token=token)
        
        # Call the predictability comparison API
        comparison_data = api_client.get(
            "/api/predictability/compare",
            params={
                "tickers": ",".join(ticker_list),
                "timeframe": timeframe
            }
        )
        
        # Get stock info for each ticker
        stocks_info = {}
        for ticker in ticker_list:
            try:
                stocks_info[ticker] = YahooFinanceService.get_stock_info(ticker)
            except:
                stocks_info[ticker] = {"name": ticker, "error": "Could not fetch stock info"}
        
        # Render template with comparison data
        return templates.TemplateResponse(
            "predictability_comparison.html", 
            {
                "request": request,
                "user": current_user,
                "tickers": ticker_list,
                "timeframe": timeframe,
                "stocks_info": stocks_info,
                **comparison_data
            }
        )
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                if "detail" in error_json:
                    error_message = error_json["detail"]
            except:
                pass
        
        # Return template with error
        return templates.TemplateResponse(
            "predictability_comparison.html", 
            {
                "request": request,
                "user": current_user,
                "tickers": tickers.split(","),
                "timeframe": timeframe,
                "error": error_message
            }
        )