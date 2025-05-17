"""
Main FastAPI application module.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from api.core.config import settings
from api.core.logging import setup_logging
from api.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    ErrorHandlerMiddleware
)
from api.routers import (
    auth,
    users,
    stocks,
    forecast,
    watchlist,
    admin,
    sentiment,
    data,
    whitepaper
)

# Setup logging
logger = setup_logging()

app = FastAPI(
    title="QuantumVestAI API",
    description="API for the QuantumVestAI trading platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
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
    Run startup tasks.
    """
    logger.info("Starting up API server")
    # Add any startup tasks here

@app.on_event("shutdown")
async def shutdown_event():
    """
    Run shutdown tasks.
    """
    logger.info("Shutting down API server")
    # Add any cleanup tasks here

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}