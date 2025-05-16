from fastapi import FastAPI
import logging
import os
from typing import Optional
from api.routers import (
    auth, users, stocks, forecast, watchlist, 
    admin, sentiment, data, whitepaper
)
from api.core.config import settings
from api.core.security.rds import validate_rds_connection
from api.core.db_init import initialize_database
from app.services.twitter_sentiment_scheduler import TwitterSentimentScheduler

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

# Create a global instance of the Twitter service
twitter_scheduler: Optional[TwitterSentimentScheduler] = None

@app.on_event("startup")
async def startup_events():
    # Initialize database
    initialize_database()
    
    # Check if Twitter credentials are configured
    twitter_credentials_configured = all([
        os.getenv("TWITTER_CONSUMER_KEY"),
        os.getenv("TWITTER_CONSUMER_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_SECRET")
    ])
    
    # Initialize Twitter sentiment scheduler if credentials are available
    global twitter_scheduler
    if twitter_credentials_configured:
        twitter_scheduler = TwitterSentimentScheduler()
        logger.info("Twitter sentiment scheduler started")
    else:
        twitter_scheduler = None
        logger.warning("Twitter integration disabled: missing API credentials")

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