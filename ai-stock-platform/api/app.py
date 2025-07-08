"""
API Application Entry Point
Created: 2025-06-17 00:07:14
Updated: 2025-06-17 03:18:36
Author: daparthi001
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy import text

# Import API components
from core.config import settings
from core.logger import logger
from db.session import engine, get_db
from routers import auth, users, stocks, alerts, watchlists, analytics

# Create API application
app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    version=settings.VERSION,
    description="QuantumVestAI API",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(watchlists.router, prefix="/watchlists", tags=["Watchlists"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(analytics.public_router, tags=["Analytics Public"])

@app.get("/")
async def api_root():
    """API Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "QuantumVestAI Stock Market Analysis API",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "version": settings.VERSION,
        "database": {
            "status": "connected"
        },
        "environment": settings.ENVIRONMENT
    }
    
    # Check database connection
    try:
        # Use text() to explicitly wrap the SQL query as required in the error message
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # No exception means database is connected
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["database"]["status"] = "disconnected"
        health_data["database"]["error"] = str(e)
    
    # Return health status
    return health_data

# Add startup event to verify database connection
@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup"""
    try:
        # Test database connection with properly wrapped SQL query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.error("Database connection failed: %s", str(e))
        # Don't raise exception here to allow app to start even with DB issues

# Log application startup complete
logger.info(
    "API startup complete - %s v%s",
    settings.PROJECT_NAME,
    settings.VERSION
)

if __name__ == "__main__":
    import uvicorn
    # Use the PORT from settings
    port = getattr(settings, "PORT", 8000)
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)