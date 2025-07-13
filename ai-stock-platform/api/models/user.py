"""
User Model Module
Created: 2025-05-19 03:27:22
Updated: 2025-05-21 15:48:25
Author: daparthi001
"""
"""Backward compatibility wrapper for the :mod:`db.models.user` model."""

# Export the User model used across the API
from db.models.user import User

__all__ = ["User"]
