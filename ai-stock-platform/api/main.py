"""
Main API Module - Dedicated Health Endpoint Fix
Updated: 2025-06-19 04:08:15
Author: daparthi001
"""
import logging
import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime

# Import health check module directly
from health_check import get_health_data

# Import routers
from routers import (
    auth,
    stocks,
    predictions,
    users,
    watchlists,
    analytics,
    sentiment,
    backtest
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_api")

# Create FastAPI application
app = FastAPI(
    title="QuantumVestAI API",
    version="1.0.0",
    description="QuantumVestAI Stock Market Analysis Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Request ID and logging middleware
@app.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    # Generate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Track timing
    start_time = datetime.now()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    process_time = (datetime.now() - start_time).total_seconds()
    
    # Log response
    logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time:.3f}s")
    
    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )

# CRITICAL: Direct health endpoints
@app.get("/health", include_in_schema=False)
async def health_check():
    """Simple health check endpoint for ALB"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health_check():
    """API health check endpoint"""
    logger.info("API health check endpoint accessed")
    return await get_health_data()

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(stocks.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(watchlists.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(sentiment.router, prefix="/api/v1")
app.include_router(backtest.router, prefix="/api/v1")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("API starting up")
    logger.info(f"Registered paths: {[route.path for route in app.routes]}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )