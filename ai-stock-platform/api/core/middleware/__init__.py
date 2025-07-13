"""
Middleware Package
Created: 2025-05-21 05:17:43
Author: daparthi001
"""
from fastapi import FastAPI

from .logging_middleware import LoggingMiddleware


def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the application"""
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)

__all__ = ['setup_middleware']
