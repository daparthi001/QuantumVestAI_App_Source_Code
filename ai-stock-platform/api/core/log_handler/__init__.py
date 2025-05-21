"""
Simple Log Handler Module
Created: 2025-05-21 13:37:56
Author: daparthi001
"""
import sys
import logging
from pathlib import Path
from typing import Optional

from core.config.settings import settings

def get_logger(
    name: str = "quantumvestai",
    level: Optional[str] = None
) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name
        level: Log level (defaults to settings.LOG_LEVEL)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        log_level = level or settings.LOG_LEVEL
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Add file handler (simple file, no rotation)
        file_handler = logging.FileHandler("logs/app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(
            "Logger initialized - Name: %s, Level: %s",
            name,
            log_level
        )
    
    return logger

# Create default logger instance
logger = get_logger()

__all__ = ['logger', 'get_logger']