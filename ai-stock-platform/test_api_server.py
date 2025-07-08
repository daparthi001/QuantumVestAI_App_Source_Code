#!/usr/bin/env python3

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Minimal FastAPI setup
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.services.trending_stocks_service import TrendingStocksService

# Create FastAPI app
app = FastAPI(title="QuantumVestAI API - Trending Stocks Test")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
trending_service = TrendingStocksService()

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    return {
        "status": "success",
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

def create_error_response(message: str, error_code: str = "ERROR") -> Dict[str, Any]:
    return {
        "status": "error",
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {"message": "QuantumVestAI API - Trending Stocks Service"}

@app.get("/api/v1/stocks/trending")
async def get_trending_stocks(page: int = 1, limit: int = 10):
    """Get trending stocks with pagination"""
    try:
        result = await trending_service.get_trending_stocks(page=page, limit=limit)
        return create_success_response(data=result, message="Trending stocks retrieved successfully")
    except Exception as e:
        return create_error_response(message=f"Failed to fetch trending stocks: {str(e)}")

@app.get("/api/v1/stocks/trending/cache/status")
async def get_cache_status():
    """Get cache status"""
    try:
        status = trending_service.get_cache_status()
        return create_success_response(data=status, message="Cache status retrieved successfully")
    except Exception as e:
        return create_error_response(message=f"Failed to get cache status: {str(e)}")

@app.post("/api/v1/stocks/trending/cache/invalidate")
async def invalidate_cache():
    """Invalidate cache"""
    try:
        trending_service.invalidate_cache()
        return create_success_response(data={"message": "Cache invalidated"}, message="Cache invalidated successfully")
    except Exception as e:
        return create_error_response(message=f"Failed to invalidate cache: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting QuantumVestAI API Test Server...")
    print("Testing endpoints:")
    print("  GET /api/v1/stocks/trending")
    print("  GET /api/v1/stocks/trending/cache/status")
    print("  POST /api/v1/stocks/trending/cache/invalidate")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")