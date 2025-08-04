"""
Core Security Module Init File
Created: 2025-08-04
Author: gayatri
"""

# Re-export everything from the original security.py module to maintain compatibility
from core.security.tokens import create_access_token, validate_token
from core.security.authentication import (
    get_current_user,
    get_current_active_user,
    check_admin_role,
    verify_password,
    get_password_hash,
    pwd_context,
    oauth2_scheme
)