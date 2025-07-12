"""
Error Handlers - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.middleware.error_handlers.
New code should import directly from middleware.error_handlers.
"""

# Import directly from the module to avoid circular imports
from middleware.error_handlers import (
    register_exception_handlers,
    setup_error_handlers,
    handle_http_exception,
    handle_validation_exception,
    handle_not_found_exception,
    handle_internal_server_error
)

__all__ = [
    'register_exception_handlers',
    'setup_error_handlers',
    'handle_http_exception',
    'handle_validation_exception',
    'handle_not_found_exception',
    'handle_internal_server_error'
]
