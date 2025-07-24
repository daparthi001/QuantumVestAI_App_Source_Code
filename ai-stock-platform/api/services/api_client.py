"""Compatibility wrapper for APIClient.

This module allows imports of ``services.api_client`` to resolve
correctly even when Python loads the ``services`` package from the
``ai-stock-platform/api`` directory first. It simply forwards the
``APIClient`` class from the repository root ``services`` package.
"""
from __future__ import annotations

from pathlib import Path
import sys

# Ensure repository root is on ``sys.path``
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from services.api_client import APIClient  # type: ignore[F401]

__all__ = ["APIClient"]
