"""
Logger Module
Created: 2025-05-21 14:16:44
Author: daparthi001
"""
import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from core.config.settings import settings

def setup_logger(
    name: str = "app",
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        level: Optional log level override
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        log_level = level or settings.LOG_LEVEL
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=settings.LOG_FORMAT,
            datefmt=settings.LOG_DATE_FORMAT
        )
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(settings.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Add rotating file handler
        file_handler = RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=settings.LOG_FILE_MAX_BYTES,
            backupCount=settings.LOG_FILE_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.debug(
            "Logger initialized - Name: %s, Level: %s",
            name,
            log_level
        )
    
    return logger

# Create default logger instance
logger = setup_logger(
    name=settings.PROJECT_NAME.lower().replace(' ', '_'),
    level=settings.LOG_LEVEL
)

__all__ = ['logger', 'setup_logger']