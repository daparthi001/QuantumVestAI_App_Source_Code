"""
API Client - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.services.api_client.
New code should import directly from services.api_client.
"""

# Deprecated compatibility layer. This file is no longer needed and is kept only for legacy import compatibility.
# Please import APIClient from 'ui.services.api_client' instead.

raise ImportError("'ui/ui/services/api_client.py' is deprecated. Import APIClient from 'ui.services.api_client' instead.")
