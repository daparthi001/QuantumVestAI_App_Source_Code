"""
QuantumVestAI API Package
Created: 2025-06-19 07:11:20
Author: daparthi001
"""
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantumvestai_api")
logger.info("Initializing API package")

try:
    # Import app from main
    from main import app
    logger.info(f"Successfully imported app from main.py with {len(app.routes)} routes")
except ImportError as e:
    logger.error(f"Failed to import app from main.py: {e}")
    raise

# Export the app variable
__all__ = ['app']