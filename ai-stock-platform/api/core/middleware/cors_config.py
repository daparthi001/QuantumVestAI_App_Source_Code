"""
CORS Configuration for QuantumVestAI
Created: 2025-06-17 18:33:20
Author: daparthi001
"""

from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app):
    """Configure CORS for the FastAPI application"""
    origins = [
        "https://quantumvestai.com",
        "https://dev.quantumvestai.com",
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"  # For development only - remove in production
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,
    )

    return app