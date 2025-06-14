"""
UI Services Module - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.services.
New code should import directly from services.
"""

from services.api_client import APIClient

__all__ = ['APIClient']