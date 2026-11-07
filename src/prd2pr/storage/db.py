"""psycopg connection pool from PRD2PR_DATABASE_URL (or configured env var)."""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import urlparse

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

_pool: ConnectionPool | None = None


def _redact_url(url: str) -> str:
    """Return host:port (and db) without password for error messages."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "?"
        port = parsed.port or 5432
        db = (parsed.path or "/").lstrip("/") or "?"
        return f"{host}:{port}/{db}"
    except Exception:
        return "<unparseable>"


def get_database_url(url_env: str = "PRD2PR_DATABASE_URL") -> str:
    url = os.environ.get(url_env)
    if not url:
        raise RuntimeError(
            f"Database unreachable: environment variable {url_env} is not set. "
            f"Expected something like postgresql://user:***@localhost:5432/prd2pr"
        )
    return url


def init_pool(url_env: str = "PRD2PR_DATABASE_URL", pool_size: int = 5) -> ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool
    url = get_database_url(url_env)
    try:
        _pool = ConnectionPool(
            conninfo=url,
            min_size=1,
            max_size=pool_size,
            kwargs={"row_factory": dict_row},
            open=True,
        )
        # Fail fast if unreachable
        with _pool.connection() as conn:
            conn.execute("SELECT 1")
    except Exception as exc:
        host = _redact_url(url)
        raise RuntimeError(
            f"Database unreachable at {host}. Check that PostgreSQL is running "
            f"and {url_env} is correct (password never shown)."
        ) from exc
    return _pool


def get_pool() -> ConnectionPool:
    if _pool is None:
        return init_pool()
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def connection() -> Iterator[Connection]:
    pool = get_pool()
    with pool.connection() as conn:
        yield conn


def safe_host_from_env(url_env: str = "PRD2PR_DATABASE_URL") -> str:
    url = os.environ.get(url_env, "")
    if not url:
        return "(not set)"
    return _redact_url(url)


_VERSION_RE = re.compile(r"^(\d+)_")
