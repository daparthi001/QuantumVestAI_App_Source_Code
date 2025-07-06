from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
# Fix the import to use the local namespace
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
    
):
    """
    Render the stock predictability analysis page
    """
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
        
        # Return template with error
        return templates.TemplateResponse(
            "predictability.html", 
            {
                "request": request,
                "user": None,
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
    
):
    """
    Render the predictability ranking page
    """
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
                
        # Try to get sectors list even if ranking fails
        sectors = []
            pass
        
        # Return template with error
        return templates.TemplateResponse(
            "predictability_ranking.html", 
            {
                "request": request,
                "user": None,
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
    
):
    """
    Render the predictability comparison page for multiple stocks
    """
                stocks_info[ticker] = {"name": ticker, "error": "Could not fetch stock info"}
        
        # Render template with comparison data
        return templates.TemplateResponse(
            "predictability_comparison.html", 
            {
                "request": request,
                "user": None,
                "tickers": ticker_list,
                "timeframe": timeframe,
                "stocks_info": stocks_info,
                **comparison_data
            }
        )
    except Exception as e:
        error_message = str(e)
        if hasattr(e, "response") and hasattr(e.response, "json"):
                pass
        
        # Return template with error
        return templates.TemplateResponse(
            "predictability_comparison.html", 
            {
                "request": request,
                "user": None,
                "tickers": tickers.split(","),
                "timeframe": timeframe,
                "error": error_message
            }
        )