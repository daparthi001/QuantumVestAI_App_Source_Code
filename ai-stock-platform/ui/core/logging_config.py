"""
Independent Logging Configuration
Created to fix circular dependency issues between logging and settings

This module provides logging configuration that doesn't depend on the settings module,
preventing bootstrap issues and circular dependencies.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any


def get_independent_logging_config(base_dir: Path = None, log_level: str = None) -> Dict[str, Any]:
    """
    Get logging configuration that's independent of the settings module.
    
    Args:
        base_dir: Base directory for log files (optional)
        log_level: Log level override (optional)
        
    Returns:
        Dictionary containing logging configuration
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent
    
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Ensure logs directory exists
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": str(logs_dir / "app.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "quantumvestai": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "quantumvestai_ui": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }


def setup_independent_logging(base_dir: Path = None, log_level: str = None) -> None:
    """
    Set up logging configuration independently of settings module.
    
    Args:
        base_dir: Base directory for log files (optional)
        log_level: Log level override (optional)
    """
    import logging.config
    
    config = get_independent_logging_config(base_dir, log_level)
    logging.config.dictConfig(config)
    
    logger = logging.getLogger("quantumvestai_ui")
    logger.info("Independent logging configuration applied successfully")


def get_logger(name: str) -> "logging.Logger":
    """
    Get a logger with the appropriate configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    import logging
    return logging.getLogger(f"quantumvestai.{name}")