"""Alembic database migration components."""

# This lightweight package primarily houses the migration scripts under
# ``alembic/versions``.  The real Alembic library provides the ``alembic``
# package with modules like ``alembic.config`` and ``alembic.script`` which our
# tests expect to import.  If the library isn't installed, importing this
# package should fail so that ``pytest.importorskip("alembic")`` correctly skips
# migration tests instead of raising obscure errors during import later on.
try:  # Attempt to import the real library components
    from importlib import import_module

    import_module("alembic.config")  # type: ignore[unused-ignore]
except Exception as exc:  # pragma: no cover - import side effects
    raise ImportError("The Alembic library is required to run migrations") from exc

