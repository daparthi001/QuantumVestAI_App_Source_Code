"""
SQLAlchemy models for the QuantumVestAI database.

This package contains all the database models representing
tables in the QuantumVestAI application.
"""

# Import all models to ensure they are registered with SQLAlchemy
from db.models.user import User
from db.models.stock import Stock, StockPrice
# Compatibility import for forecasts
from db.models.forecast import Forecast, ForecastModel
from db.models.whitepaper import Whitepaper, WhitepaperAnalysis
