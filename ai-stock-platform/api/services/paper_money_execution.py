"""Compatibility wrapper for PaperMoneyExecutionService."""
from __future__ import annotations

from pathlib import Path
import sys

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from services.paper_money_execution import PaperMoneyExecutionService  # type: ignore[F401]

__all__ = ["PaperMoneyExecutionService"]
