from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel

class ForecastPoint(BaseModel):
    date: datetime
    predicted_price: float
    confidence_upper: float
    confidence_lower: float
    confidence_level: float

class ForecastResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: datetime

class ModelComparisonResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
    timestamp: datetime

class PredictabilityResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: datetime

class BacktestResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: datetime

class RecommendationResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
    timestamp: datetime
