"""Apply pending numbered .sql migration files."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from prd2pr.storage.db import connection, init_pool


def _migrations_dir() -> Path:
    # Prefer package resources; fall back to filesystem next to this file
    try:
        root = resources.files("prd2pr.storage") / "migrations"
        # Convert Traversable to Path when possible
        if hasattr(root, "joinpath"):
            # On disk install
            as_path = Path(str(root))
            if as_path.is_dir():
                return as_path
    except (TypeError, FileNotFoundError, ModuleNotFoundError):
        pass
    return Path(__file__).resolve().parent / "migrations"


def list_migration_files() -> list[tuple[int, Path]]:
    mig_dir = _migrations_dir()
    found: list[tuple[int, Path]] = []
    for path in sorted(mig_dir.glob("*.sql")):
        stem = path.stem  # e.g. 0001_init
        version_str = stem.split("_", 1)[0]
        if not version_str.isdigit():
            continue
        found.append((int(version_str), path))
    return found


def applied_versions() -> set[int]:
    with connection() as conn:
        # schema_migrations may not exist yet
        exists = conn.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'schema_migrations'
            ) AS ok
            """
        ).fetchone()
        if not exists or not exists["ok"]:
            return set()
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
        return {int(r["version"]) for r in rows}


def pending_migrations() -> list[tuple[int, Path]]:
    applied = applied_versions()
    return [(v, p) for v, p in list_migration_files() if v not in applied]


def has_pending_migrations() -> bool:
    return bool(pending_migrations())


def migrate(url_env: str = "PRD2PR_DATABASE_URL", pool_size: int = 5) -> list[int]:
    """Apply all pending migrations. Returns list of versions applied."""
    init_pool(url_env=url_env, pool_size=pool_size)
    applied_now: list[int] = []
    for version, path in pending_migrations():
        sql = path.read_text(encoding="utf-8")
        with connection() as conn:
            with conn.transaction():
                # First migration creates schema_migrations itself
                conn.execute(sql)
                # Ensure the version row exists (0001 creates the table but
                # may not insert its own version — we always record it)
                conn.execute(
                    """
                    INSERT INTO schema_migrations (version)
                    VALUES (%s)
                    ON CONFLICT (version) DO NOTHING
                    """,
                    (version,),
                )
        applied_now.append(version)
    return applied_now
