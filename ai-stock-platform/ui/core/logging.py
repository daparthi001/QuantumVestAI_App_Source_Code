"""
Logging Configuration Module
Created: 2025-06-15 02:56:18
Author: daparthi001
"""
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logging(
    name: str = "app",
    level: str = "INFO",
    log_to_file: bool = True,
    log_file: str = "logs/app.log",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file
        log_file: Path to log file
        log_format: Log message format
        date_format: Date format for timestamps
        max_bytes: Maximum size for log file before rotation
        backup_count: Number of backup log files to keep
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        # Set log level
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(
            fmt=log_format,
            datefmt=date_format
        )
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Add file handler if requested
        if log_to_file:
            # Create logs directory if it doesn't exist
            log_dir = Path(log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Add rotating file handler
            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        logger.debug(
            "Logger initialized - Name: %s, Level: %s",
            name,
            level
        )
    
    return logger