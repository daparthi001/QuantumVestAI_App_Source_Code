"""
WebSocket Package
Created: 2025-05-20 04:36:10
Author: daparthi001
"""
"""Simplified exports for the local WebSocket utilities."""

# Only the connection manager exists in this module hierarchy. The
# previous implementation attempted to expose several classes that are not
# actually present in the repository which caused import errors when the
# package was initialised.

from .manager import ConnectionManager

__all__ = [
    "ConnectionManager",]
