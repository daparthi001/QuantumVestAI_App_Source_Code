"""
API Client - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.services.api_client.
New code should import directly from services.api_client.
"""

# Import directly from the module to avoid circular imports
# Use absolute import path to be explicit
import sys
import os

# Add the parent directory to sys.path if needed
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Get the APIClient class directly
from services.api_client import APIClient

__all__ = ['APIClient']