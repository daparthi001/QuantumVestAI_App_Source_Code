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
    from .main import app
    logger.info(
        "Successfully imported app from api.main with %d routes", len(app.routes)
    )
except Exception as e:  # pragma: no cover - optional dependency may be missing
    logger.error(f"Failed to import app from api.main: {e}")
    app = None
# Export the app variable__all__ = ['app']