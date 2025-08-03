"""
Middleware Package
Created: 2025-05-21 05:17:43
Author: daparthi001
"""
from fastapi import FastAPI

try:  # pragma: no cover - optional logging dependency
    from .logging_middleware import LoggingMiddleware
except Exception:  # pragma: no cover - fallback when logger not available
    LoggingMiddleware = None  # type: ignore


def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the application"""
    if LoggingMiddleware is not None:
        app.add_middleware(LoggingMiddleware)

__all__ = ["setup_middleware", "LoggingMiddleware"]
