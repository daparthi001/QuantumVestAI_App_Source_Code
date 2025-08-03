"""
WebSocket Package
Created: 2025-05-20 04:36:10
Author: daparthi001
"""
"""Simplified exports for the local WebSocket utilities."""

# Only the connection manager existed initially in this module hierarchy.
# A small market data broadcaster is also exposed to support tests that need
# to push mock prices to connected clients.

from .manager import ConnectionManager
from .market import MarketWebSocketService

__all__ = [
    "ConnectionManager",
    "MarketWebSocketService",
]
