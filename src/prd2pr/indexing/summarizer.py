"""FR5 — LLM summaries with hash cache."""

from __future__ import annotations

import asyncio
from typing import Any

from prd2pr.config import LimitsConfig
from prd2pr.llm.client import LlmClient
from prd2pr.storage.pg_store import PgStore


def summarize_chunks(
    store: PgStore,
    repo_id: int,
    client: LlmClient,
    limits: LimitsConfig,
    chunks: list[dict[str, Any]] | None = None,
) -> int:
    """Summarize chunks that need it. Returns number of new summaries."""
    rows = chunks if chunks is not None else store.list_chunks(repo_id)
    need: list[tuple[str, str, str]] = []
    for c in rows:
        code = c.get("code") or ""
        nlines = code.count("\n") + (1 if code else 0)
        if nlines < limits.min_summary_lines:
            continue
        if c.get("summary") and c.get("summary_hash") == c.get("content_hash"):
            continue
        need.append((c["id"], c.get("header") or "", code))

    if not need:
        return 0

    summaries = asyncio.run(client.summarize_many(need))
    for cid, summary in summaries.items():
        # find content_hash
        ch = next(c["content_hash"] for c in rows if c["id"] == cid)
        store.update_chunk_summary(repo_id, cid, summary, ch)
    return len(summaries)
