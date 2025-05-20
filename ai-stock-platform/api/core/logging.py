"""
Logging configuration for the API.
"""
import logging
import sys
from pathlib import Path
import json
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from core.config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for logs."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record.update(
            timestamp=record.created,
            level=record.levelname,
            logger=record.name
        )
        
        # Add request_id if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id

def setup_logging() -> logging.Logger:
    """Configure logging for the application."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("api")
    logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    )
    logger.addHandler(console_handler)
    
    # File handler for errors
    error_handler = logging.FileHandler(
        log_dir / "error.log"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    )
    logger.addHandler(error_handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(
        log_dir / "api.log"
    )
    file_handler.setFormatter(
        CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    )
    logger.addHandler(file_handler)
    
    return logger