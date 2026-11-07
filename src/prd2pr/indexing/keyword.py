"""Step 5b: identifier splitting → identifiers column (tsvector generated)."""

from __future__ import annotations

from typing import Any

from prd2pr.indexing.chunker import collect_identifiers
from prd2pr.storage.pg_store import PgStore


def fill_identifiers_for_chunks(
    store: PgStore,
    repo_id: int,
    chunks: list[dict[str, Any]] | None = None,
) -> int:
    """Ensure identifiers are populated; returns number updated."""
    rows = chunks if chunks is not None else store.list_chunks(repo_id)
    updated = 0
    for c in rows:
        if c.get("identifiers"):
            continue
        name = None
        qn = None
        sid = c.get("symbol_id")
        if sid and "::" in sid:
            qn = sid.split("::", 1)[1]
            name = qn.split(".")[-1]
        ids = collect_identifiers(name, qn, c["file"], c.get("code") or "")
        store.update_chunk_identifiers(repo_id, c["id"], ids)
        updated += 1
    return updated
