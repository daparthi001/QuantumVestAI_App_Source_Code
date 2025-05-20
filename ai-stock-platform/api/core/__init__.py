"""
Core Package
Created: 2025-05-20 21:42:17
Author: daparthi001
"""
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import settings first as it's needed by other modules
from core.config.settings import Settings

# Initialize settings
settings = Settings()

# Now import other modules that depend on settings
from core.middleware import setup_middleware
from core.logging import setup_logging, logger

__all__ = ['settings', 'setup_middleware', 'logger', 'setup_logging']