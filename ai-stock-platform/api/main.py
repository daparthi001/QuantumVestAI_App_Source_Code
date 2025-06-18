"""
QuantumVestAI API Main Module
Created: 2025-06-17 01:50:11
Updated: 2025-06-18 01:01:01
Author: daparthi001
"""
import os
import time
import logging
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from typing import Dict, Any

# Import routers from modules
from routers import (
    auth, 
    market, 
    stocks, 
    forecast, 
    portfolio, 
    watchlist, 
    news, 
    users
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("quantumvestai_api")

# Create FastAPI application
app = FastAPI(
    title="QuantumVestAI API",
    description="API for QuantumVestAI Platform",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:8080",
    "https://dev.quantumvestai.com",
    "https://app.quantumvestai.com",
    "https://quantumvestai.com",
    "*"  # Allow all origins for development - REMOVE IN PRODUCTION
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

security = HTTPBearer()

# Middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    
    logger.info(f"Request: {method} {path}")
    
    try:
        # Process the request and get the response
        response = await call_next(request)
        
        # Calculate the processing time
        process_time = time.time() - start_time
        
        # Add the processing time to the response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log the response status
        logger.info(f"Response: {method} {path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        return response
    except Exception as e:
        # Log any errors that occur during processing
        logger.error(f"Error processing request {method} {path}: {str(e)}")
        
        # Return a JSON error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": str(e)}
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "QuantumVestAI API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    # Add more comprehensive health checks here (DB, services, etc.)
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

# Preflight handler for CORS
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    return {}

# API v1 endpoint prefix
API_V1_PREFIX = "/api/v1"

# Include routers with versioned prefix
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(market.router, prefix=API_V1_PREFIX)
app.include_router(stocks.router, prefix=API_V1_PREFIX)
app.include_router(forecast.router, prefix=API_V1_PREFIX)
app.include_router(portfolio.router, prefix=API_V1_PREFIX)
app.include_router(watchlist.router, prefix=API_V1_PREFIX)
app.include_router(news.router, prefix=API_V1_PREFIX)
app.include_router(users.router, prefix=API_V1_PREFIX)

# Add development-only routes
if os.environ.get("ENVIRONMENT", "development") != "production":
    @app.get("/debug/routes")
    async def debug_routes():
        """Show all registered routes for debugging (Development only)"""
        routes = []
        
        for route in app.routes:
            route_info = {
                "path": getattr(route, "path", None),
                "name": getattr(route, "name", None),
                "methods": list(route.methods) if hasattr(route, "methods") and route.methods else []
            }
            routes.append(route_info)
        
        return {"routes": routes}
    
    @app.get("/debug/headers")
    async def debug_headers(request: Request):
        """Show request headers (Development only)"""
        return {"headers": dict(request.headers)}
    
    @app.post("/debug/echo")
    async def echo_payload(request: Request):
        """Echo back request body (Development only)"""
        try:
            body = await request.json()
            return {"echo": body}
        except:
            try:
                body = await request.body()
                return {"echo": str(body)}
            except:
                return {"echo": "Could not parse request body"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)