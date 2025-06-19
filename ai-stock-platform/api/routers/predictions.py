"""
ML Predictions Router
Created: 2025-06-19 03:09:13
Author: daparthi001
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from core.database import get_db_session
from core.models.response import StandardResponse
from ml.lstm_model import LSTMStockModel
from services.stock_service import StockService
from auth.dependencies import get_current_user
from models.user import User

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.get(
    "/{symbol}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Stock Price Prediction",
    description="Get price prediction for a specific stock symbol"
)
async def get_prediction(
    symbol: str,
    prediction_type: str = Query("next_day", description="Type of prediction: next_day, week_ahead, or month_ahead"),
    model_id: Optional[str] = Query(None, description="Specific model ID to use for prediction"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get price prediction for a stock"""
    # Validate prediction type
    valid_types = ["next_day", "week_ahead", "month_ahead"]
    if prediction_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prediction type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Map prediction type to days
    days_mapping = {
        "next_day": 1,
        "week_ahead": 7,
        "month_ahead": 30
    }
    days_ahead = days_mapping[prediction_type]
    
    # Use default model if none specified
    model_id = model_id or f"{symbol.lower()}_lstm_v1"
    
    try:
        # Get historical data for the stock
        stock_service = StockService(db)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)  # Need enough historical data
        
        historical_data = await stock_service.get_historical_prices(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if not historical_data or len(historical_data) < 60:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough historical data for {symbol} to make predictions"
            )
        
        # Create model instance
        model = LSTMStockModel(model_id=model_id)
        
        # Make prediction
        prediction = model.predict(historical_data, days_ahead=days_ahead)
        
        # Format the response
        result = {
            "symbol": symbol,
            "prediction_type": prediction_type,
            "model_version": model_id,
            "predictions": []
        }
        
        for i in range(len(prediction["dates"])):
            result["predictions"].append({
                "date": prediction["dates"][i],
                "predicted_price": prediction["predicted_prices"][i],
                "upper_bound": prediction["upper_bounds"][i],
                "lower_bound": prediction["lower_bounds"][i],
                "confidence": prediction["confidence_levels"][i]
            })
        
        return StandardResponse(
            status="success",
            message=f"Successfully generated {prediction_type} prediction for {symbol}",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prediction: {str(e)}"
        )