"""Alembic database migration components."""

# This lightweight package primarily stores the application's migration
# scripts under ``alembic/versions``.  When running the application we expect
# the real Alembic library to be installed so helper modules like
# ``alembic.config`` and ``alembic.script`` are available.  Because this
# directory shares the package name, importing ``alembic`` would normally
# resolve to this folder only.  To allow Python to also find the installed
# library, we extend ``__path__`` into a namespace package.

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)  # type: ignore[misc]

# When the real Alembic library is installed, Python will discover its modules
# via the extended search path above.  If it's missing, importing things like
# ``alembic.config`` will fail normally.
