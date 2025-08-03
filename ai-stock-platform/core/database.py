"""Minimal database utilities for test environment.

The full application exposes rich database helpers under ``core.database``
which establish real connections.  During unit tests we only need the
interface to exist so importing modules like ``api.main`` does not fail.
These placeholders provide the required callables without performing any
external operations.
"""

from __future__ import annotations

from typing import Any, Dict


def initialize_database() -> bool:
    """Pretend to initialise the database and return ``True`` to indicate
    success."""

    return True


def check_database_connection() -> bool:
    """Return ``True`` indicating the (mock) database is reachable."""

    return True


def get_database_health() -> Dict[str, Any]:
    """Return a basic health dictionary used by tests."""

    return {"connected": True, "last_error": None}


async_engine = None


async def create_db_and_tables() -> None:
    """Placeholder async function used during startup."""

    return None


async def get_db_session():  # pragma: no cover - simple async generator
    """Yield a dummy async session object."""

    yield None


__all__ = [
    "initialize_database",
    "check_database_connection",
    "get_database_health",
    "async_engine",
    "create_db_and_tables",
    "get_db_session",
]

