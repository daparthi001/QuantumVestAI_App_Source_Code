"""
API route modules for the QuantumVestAI API.

This package contains all the FastAPI router components that define
the API endpoints for the QuantumVestAI application.
"""

# Import all routers
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
from api.routers.stocks import router as stocks_router
from api.routers.forecast import router as forecast_router
from api.routers.watchlist import router as watchlist_router
from api.routers.admin import router as admin_router
from api.routers.sentiment import router as sentiment_router
from api.routers.data import router as data_router
from api.routers.whitepaper import router as whitepaper_router