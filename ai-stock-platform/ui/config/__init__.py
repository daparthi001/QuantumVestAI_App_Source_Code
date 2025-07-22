# This file makes the config directory a proper Python package.
# It can be empty or can include package-level imports that should be available when importing the config package.

# Import settings directly from the API package to avoid ambiguity with
# the ``core`` compatibility package when both packages are on the path.


# This makes the settings available when importing from config directly
# Usage: from ui.config import settings
