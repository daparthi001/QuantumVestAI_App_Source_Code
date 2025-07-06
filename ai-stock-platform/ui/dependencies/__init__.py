# This file makes the dependencies directory a proper Python package.
# It allows for easier imports of dependency components throughout the application.
API_URL = "http://quantumvestai-dev-api:8000/api/v1"
from ui.dependencies.common import (
    get_current_user,
    get_current_active_user,
    get_admin_user,
    get_api_client,
    get_template_context,
    pagination_params,
    common_query_params
)

# This allows importing these dependencies directly from the package
# For example: from ui.dependencies import get_current_user, pagination_params