"""M1: migrations are idempotent."""

from __future__ import annotations

from prd2pr.storage import db as dbmod
from prd2pr.storage.migrate import applied_versions, migrate, pending_migrations


def test_migrate_idempotent(test_database_url: str) -> None:
    dbmod.close_pool()
    # Session may already have migrated; ensure applied then re-run is a no-op
    first = migrate()
    assert applied_versions() == {1}
    assert pending_migrations() == []
    # Either this call applied v1, or a prior fixture did — both are fine
    assert first in ([1], [])

    second = migrate()
    assert second == []
    assert applied_versions() == {1}


def test_schema_tables_exist(migrated_db: str) -> None:
    dbmod.close_pool()
    dbmod.init_pool()
    with dbmod.connection() as conn:
        rows = conn.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        ).fetchall()
    names = {r["table_name"] for r in rows}
    assert {
        "schema_migrations",
        "repos",
        "files",
        "symbols",
        "chunks",
        "edges",
    } <= names
