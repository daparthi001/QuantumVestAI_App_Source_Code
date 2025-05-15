# This file makes the middleware directory a proper Python package.
# It allows for easier imports of middleware components throughout the application.

from ui.middleware.auth_middleware import (
    verify_token, 
    get_authenticated_user,
    require_auth,
    require_admin
)

from ui.middleware.error_handlers import (
    register_exception_handlers,
    handle_http_exception,
    handle_validation_exception,
    handle_not_found_exception,
    handle_internal_server_error
)

# This allows importing these functions directly from the middleware package
# For example: from ui.middleware import require_auth, handle_http_exception