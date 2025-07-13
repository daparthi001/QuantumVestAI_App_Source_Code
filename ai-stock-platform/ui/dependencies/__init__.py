# This file makes the dependencies directory a proper Python package.
# It allows for easier imports of dependency components throughout the application.
API_URL = "http://quantumvestai-dev-api:8000"
from ui.dependencies.common import (common_query_params, get_api_client,
                                    get_template_context, pagination_params)

# This allows importing these dependencies directly from the package# For example: from ui.dependencies import get_api_client, pagination_params
