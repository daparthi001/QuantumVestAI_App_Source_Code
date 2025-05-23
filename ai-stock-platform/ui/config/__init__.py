# This file makes the config directory a proper Python package.
# It can be empty or can include package-level imports that should be available when importing the config package.

from core.config.settings import settings

# This makes the settings available when importing from config directly
# Usage: from ui.config import settings