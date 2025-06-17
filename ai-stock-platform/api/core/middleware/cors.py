"""
CORS Configuration for QuantumVestAI
Created: 2025-06-17 17:03:55
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
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app