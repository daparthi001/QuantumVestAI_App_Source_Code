"""Compatibility wrapper for APIClient.

This module allows imports of ``services.api_client`` to resolve
correctly even when Python loads the ``services`` package from the
``ai-stock-platform/api`` directory first. It simply forwards the
``APIClient`` class from the repository root ``services`` package.
"""
from __future__ import annotations

from importlib import util
from pathlib import Path
import sys

# Ensure repository root is on ``sys.path``

_root = Path(__file__).resolve().parents[3]
root_module = _root / "services" / "api_client.py"

if __name__ == "services.api_client":
    spec = util.spec_from_file_location("_root_services_api_client", root_module)
    module = util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    APIClient = module.APIClient  # type: ignore[attr-defined]
else:
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from services.api_client import APIClient  # type: ignore[F401]

__all__ = ["APIClient"]
