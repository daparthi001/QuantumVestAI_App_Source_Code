"""
Logger Module
Created: 2025-05-21 14:16:44
Author: daparthi001
Updated: 2025-06-14 20:28:31 by daparthi001
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
        log_level = level or getattr(settings, 'LOG_LEVEL', 'INFO')
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Create formatter with defaults if settings aren't available
        log_format = getattr(settings, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_date_format = getattr(settings, 'LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
        
        formatter = logging.Formatter(
            fmt=log_format,
            datefmt=log_date_format
        )
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Default log file settings
        log_file = getattr(settings, 'LOG_FILE', 'logs/app.log')
        log_max_bytes = getattr(settings, 'LOG_FILE_MAX_BYTES', 10 * 1024 * 1024)  # 10 MB
        log_backup_count = getattr(settings, 'LOG_FILE_BACKUP_COUNT', 5)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Add rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
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
    name=getattr(settings, 'PROJECT_NAME', 'app').lower().replace(' ', '_'),
    level=getattr(settings, 'LOG_LEVEL', 'INFO')
)

__all__ = ['logger', 'setup_logger']