"""
SQLAlchemy models for the QuantumVestAI database.

This package contains all the database models representing
tables in the QuantumVestAI application.
"""
from api.db.base import Base

__all__ = [
    "User",
    "Stock",
    "StockPrice",
    "Alert",  # Added Alert
    "Forecast", 
    "ForecastModel",
    "Whitepaper",
    "WhitepaperAnalysis"
]

# Import all models here
from .user import User
from .stock import Stock, StockPrice, Alert
from .forecast import Forecast, ForecastModel
from .whitepaper import Whitepaper, WhitepaperAnalysis

# Initialize relationships after all models are imported
User.watchlists.property
Stock.prices.property
Whitepaper.analyses.property