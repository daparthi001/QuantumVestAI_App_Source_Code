from fastapi import FastAPI, Depends
import logging
from api.routers import (
    auth, users, stocks, forecast, watchlist, 
    admin, sentiment, data, whitepaper
)
from api.core.config import settings
from api.core.security.rds import validate_rds_connection
from api.core.db_init import initialize_database

logger = logging.getLogger(__name__)

app = FastAPI(
    title="QuantumVestAI API",
    description="API for the QuantumVestAI trading platform",
    version="1.0.0",
)

# Include all routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(stocks.router, prefix="/api", tags=["Stocks"])
app.include_router(forecast.router, prefix="/api", tags=["Forecasts"])
app.include_router(watchlist.router, prefix="/api", tags=["Watchlist"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(sentiment.router, prefix="/api", tags=["Sentiment"])
app.include_router(data.router, prefix="/api", tags=["Data"])
app.include_router(whitepaper.router, prefix="/api", tags=["Whitepapers"])

@app.on_event("startup")
async def startup_event():
    """
    Validate database connection and run startup tasks.
    """
    logger.info("Starting QuantumVestAI API")
    
    # Validate RDS connection
    if validate_rds_connection():
        logger.info("Successfully connected to RDS database")
    else:
        logger.error("Failed to connect to RDS database")
    
    # Initialize database if needed
    if initialize_database():
        logger.info("Database initialization successful")
    else:
        logger.warning("Database initialization incomplete")

@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "ok", 
        "version": "1.0.0",
        "database": "connected" if validate_rds_connection() else "disconnected"
    }