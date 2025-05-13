from fastapi import APIRouter, HTTPException, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import yfinance as yf
from models.pipeline import run_ensemble
from models.prophet_model import run_prophet
from models.xgboost_model import run_xgboost
from models.lstm_model import run_lstm
from models.finbert_sentiment import get_finbert_sentiment
from routes.auth import get_current_user

router = APIRouter(tags=["webapi"])
templates = Jinja2Templates(directory="templates")

class ForecastRequest(BaseModel):
    ticker: str
    days: int = 7
    model: str = "ensemble"  # "ensemble", "prophet", "xgboost", "lstm"

@router.post("/api/forecast")
async def get_forecast(request: ForecastRequest) -> Dict[str, Any]:
    """
    Generate a price forecast for the specified ticker.
    """
    try:
        # Download historical data
        data = yf.download(request.ticker, period="2y")
        data = data.reset_index()
        
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {request.ticker}")
        
        # Get forecast based on model choice
        if request.model.lower() == "ensemble":
            forecast = run_ensemble(data, forecast_days=request.days)
        elif request.model.lower() == "prophet":
            forecast = run_prophet(data, forecast_days=request.days)
        elif request.model.lower() == "xgboost":
            forecast = run_xgboost(data, forecast_days=request.days)
        elif request.model.lower() == "lstm":
            lstm_forecast = run_lstm(data, forecast_days=request.days)
            # Create a DataFrame similar to other models' output
            dates = pd.date_range(start=data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=request.days)
            forecast = pd.DataFrame({'ds': dates, 'yhat': lstm_forecast})
        else:
            raise HTTPException(status_code=400, detail=f"Model '{request.model}' not supported")
            
        # Convert to list format for JSON response
        result = {
            "ticker": request.ticker,
            "model": request.model,
            "dates": forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
            "predictions": forecast['yhat'].tolist()
        }
        
        # Add sentiment analysis if available
        try:
            # Get recent news or social media sentiment
            sentiment = get_finbert_sentiment(f"Recent news about {request.ticker}")
            result["sentiment"] = sentiment
        except Exception as e:
            result["sentiment"] = {"label": "neutral", "score": 0.5}
            
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", response_class=HTMLResponse)
async def forecast_page(
    request: Request, 
    ticker: str = Query(...), 
    days: int = Query(7), 
    model: str = Query("ensemble"),
    current_user: dict = Depends(get_current_user)
):
    """
    Render forecast page with forecast data
    """
    try:
        # Create forecast request
        forecast_req = ForecastRequest(ticker=ticker, days=days, model=model)
        
        # Get forecast data
        forecast_data = await get_forecast(forecast_req)
        
        # Render template with forecast data
        return templates.TemplateResponse(
            "forecast.html", 
            {
                "request": request, 
                "forecast": forecast_data,
                "user": current_user
            }
        )
    except Exception as e:
        # Render error page
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "error": str(e),
                "user": current_user
            }
        )