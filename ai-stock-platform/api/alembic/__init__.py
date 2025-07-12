"""Alembic database migration components."""

# This lightweight package primarily stores the application's migration
# scripts under ``alembic/versions``.  When running the application we expect
# the real Alembic library to be installed so we can import helper modules like
# ``alembic.config`` and ``alembic.script``.  Since this directory shares the
# same name as the real package, importing ``alembic`` would normally resolve to
# this folder only.  To allow Python to also find the installed library we
# extend ``__path__`` into a namespace package before attempting the import.

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)  # type: ignore[misc]

try:  # Attempt to import the real library components
    from importlib import import_module

    import_module("alembic.config")  # type: ignore[unused-ignore]
except Exception as exc:  # pragma: no cover - import side effects
    raise ImportError("The Alembic library is required to run migrations") from exc