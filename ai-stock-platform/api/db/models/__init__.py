"""
SQLAlchemy models for the QuantumVestAI database.

This package contains all the database models representing
tables in the QuantumVestAI application.
"""

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .stock import Stock, StockPrice, Alert
from .forecast import Forecast, ForecastModel
from .whitepaper import Whitepaper, WhitepaperAnalysis

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