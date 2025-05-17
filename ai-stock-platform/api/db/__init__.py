"""
SQLAlchemy models for the QuantumVestAI database.

This package contains all the database models representing
tables in the QuantumVestAI application.
"""

# Import all models to ensure they are registered with SQLAlchemy
from api.db.models.user import User
from api.db.models.stock import Stock, StockPrice
from api.db.models.forecast import Forecast, ForecastModel
from api.db.models.whitepaper import Whitepaper, WhitepaperAnalysis

__all__ = [
    "User",
    "Stock",
    "StockPrice",
    "Forecast",
    "ForecastModel",
    "Whitepaper",
    "WhitepaperAnalysis"
]