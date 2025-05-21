"""
Application Logger Configuration
Created: 2025-05-21 05:28:53
Author: daparthi001
"""
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from core.config.settings import settings

def setup_logger(
    name: str = "quantumvest",
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure application logger
    
    Args:
        name: Logger name
        log_level: Optional log level override
        log_file: Optional log file path override
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Set up logger
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        level = log_level or settings.LOG_LEVEL
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Create formatters
        fmt = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt=settings.LOG_DATE_FORMAT
        )
        
        # File handler
        fh = RotatingFileHandler(
            log_file or settings.LOG_FILE,
            maxBytes=settings.LOG_FILE_MAX_BYTES,
            backupCount=settings.LOG_FILE_BACKUP_COUNT
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        
        logger.info(
            "Logger initialized - Name: %s, Level: %s, File: %s",
            name,
            level,
            log_file or settings.LOG_FILE
        )
    
    return logger

# Create default logger instance
logger = setup_logger()

__all__ = ['logger', 'setup_logger']