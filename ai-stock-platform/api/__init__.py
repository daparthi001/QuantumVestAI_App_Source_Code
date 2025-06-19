"""
API Package
Created: 2025-06-19 06:52:30
Author: daparthi001
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantumvestai_api")
logger.info("Loading api package")

# Import app from main.py in root directory
from main import app

logger.info(f"Imported app from main.py with {len(app.routes)} routes")

__all__ = ['app']