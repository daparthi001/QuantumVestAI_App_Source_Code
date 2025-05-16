import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

class JsonFormatter(logging.Formatter):
    """Custom formatter that outputs log entries as JSON."""
    
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        """Initialize JsonFormatter."""
        super().__init__(fmt, datefmt, style, validate)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "client_ip"):
            log_data["client_ip"] = record.client_ip
        
        if hasattr(record, "method"):
            log_data["method"] = record.method
        
        if hasattr(record, "path"):
            log_data["path"] = record.path
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        if hasattr(record, "process_time"):
            log_data["process_time"] = record.process_time
        
        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": "".join(traceback.format_exception(*record.exc_info))
            }
        
        return json.dumps(log_data)

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up and return a logger with the specified configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s | %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    
    return logger