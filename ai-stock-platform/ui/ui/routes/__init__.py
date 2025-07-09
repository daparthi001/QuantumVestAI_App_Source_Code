"""Compatibility layer for legacy imports.

This module re-exports objects from :mod:`ui.routes` so that code importing
``ui.routes.*`` continues to function.
"""
from ...routes.auth import *  # noqa: F401,F403
from ...routes.admin import *  # noqa: F401,F403
from ...routes.forecast import *  # noqa: F401,F403
from ...routes.predictability import *  # noqa: F401,F403
from ...routes.watchlist import *  # noqa: F401,F403
