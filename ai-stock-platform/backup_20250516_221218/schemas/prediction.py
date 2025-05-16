"""
Schemas for ML predictions.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ForecastDataPoint(BaseModel):
    """A single data point in a forecast."""
    date: str
    predicted_price: float


class PredictionCreate(BaseModel):
    """Schema for creating a prediction."""
    ticker: str
    days: int = Field(5, ge=1, le=30)


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    ticker: str
    last_updated: str
    last_actual_price: float
    last_actual_date: str
    forecast_days: int
    forecast_data: List[ForecastDataPoint]