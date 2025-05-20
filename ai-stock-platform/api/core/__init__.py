"""
Core Package
Created: 2025-05-20 21:12:19
Author: daparthi001
"""
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from core.config.settings import Settings
from core.middleware import setup_middleware
from core.logging import setup_logging

# Initialize settings and logging
settings = Settings()
logger = setup_logging()

__all__ = ['settings', 'setup_middleware', 'logger']