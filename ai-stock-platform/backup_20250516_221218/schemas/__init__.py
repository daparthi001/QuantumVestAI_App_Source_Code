"""
Pydantic schemas for the QuantumVestAI API.

This package contains all the Pydantic models used for request validation,
response serialization, and data transfer objects.
"""

# Import main schemas for easier access
from api.schemas.user import UserCreate, UserUpdate, UserPrivate, UserPublic
from api.schemas.stock import StockInfo, StockPrice, StockSearch
from api.schemas.token import Token, TokenPayload
from api.schemas.forecast import ForecastCreate, ForecastResponse
from api.schemas.whitepaper import (
    WhitepaperCreate, 
    WhitepaperResponse, 
    WhitepaperAnalysisResponse
)