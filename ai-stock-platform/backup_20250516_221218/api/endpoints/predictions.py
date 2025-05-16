"""
API endpoints for ML predictions.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.crud import get_stock_by_ticker, get_stock_prices
from app.ml.models import ModelManager
from app.schemas.prediction import PredictionCreate, PredictionResponse

router = APIRouter()

@router.get("/stocks/{ticker}/forecast", response_model=PredictionResponse)
def get_stock_forecast(
    ticker: str,
    days: int = Query(5, ge=1, le=30),
    db: Session = Depends(deps.get_db),
):
    """
    Get forecast for a specific stock.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to forecast (1-30)
        db: Database session
        
    Returns:
        PredictionResponse: Forecast data
    """
    # Verify stock exists
    stock = get_stock_by_ticker(db=db, ticker=ticker)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock with ticker {ticker} not found")
    
    # Get historical data (90 days to ensure enough for model)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    historical_prices = get_stock_prices(
        db=db, 
        stock_id=stock.id,
        start_date=start_date,
        end_date=end_date
    )
    
    if not historical_prices or len(historical_prices) < 60:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient historical data for {ticker}. Need at least 60 days."
        )
    
    # Convert to DataFrame
    hist_df = pd.DataFrame([p.__dict__ for p in historical_prices])
    hist_df['date'] = pd.to_datetime(hist_df['date'])
    hist_df = hist_df.set_index('date')
    
    try:
        # Load model and make prediction
        model_manager = ModelManager(
            models_path='/app/models',
            s3_bucket=f"quantumvestai-models-{deps.get_settings().environment}"
        )
        
        predictions_df = model_manager.predict(ticker, hist_df, days_ahead=days)
        
        # Format response
        forecast_data = []
        for date, row in predictions_df.iterrows():
            forecast_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_price": float(row['predicted_close']),
            })
        
        # Get last actual price for reference
        last_actual = hist_df.iloc[-1]['adjusted_close']
        
        return {
            "ticker": ticker,
            "last_updated": datetime.now().isoformat(),
            "last_actual_price": float(last_actual),
            "last_actual_date": hist_df.index[-1].strftime("%Y-%m-%d"),
            "forecast_days": days,
            "forecast_data": forecast_data
        }
        
    except FileNotFoundError:
        # Model not found
        raise HTTPException(
            status_code=404, 
            detail=f"Prediction model for {ticker} not found. It may need to be trained first."
        )
    except Exception as e:
        # Other errors
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")


@router.get("/available-models")
def list_available_models():
    """
    List all available prediction models.
    
    Returns:
        Dict: Dictionary of available models by ticker
    """
    try:
        model_manager = ModelManager(
            models_path='/app/models',
            s3_bucket=f"quantumvestai-models-{deps.get_settings().environment}"
        )
        
        return model_manager.list_available_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")