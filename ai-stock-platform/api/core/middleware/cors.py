"""
CORS Configuration Middleware
Updated: 2025-06-19 03:05:06
Author: daparthi001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

def configure_cors(app: FastAPI) -> FastAPI:
    """Configure CORS for the FastAPI application."""
    
    origins = [
        # Frontend URL(s)
        settings.FRONTEND_URL,
        # Local development
        "http://localhost:3000",
        "http://localhost:8000",
        # Add any additional allowed origins
        "https://dev.quantumvestai.com",
        "https://quantumvestai.com",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=86400,  # Cache preflight requests for 24 hours
    )
    
    return app