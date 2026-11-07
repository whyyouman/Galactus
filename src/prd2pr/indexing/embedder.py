"""Step 5a: embed chunks (+ summaries) → Qdrant."""

from __future__ import annotations

import asyncio
from typing import Any

from prd2pr.llm.client import LlmClient
from prd2pr.storage.pg_store import PgStore
from prd2pr.storage.vector_store import QdrantVectorStore


def embed_chunks(
    store: PgStore,
    vectors: QdrantVectorStore,
    repo_id: int,
    client: LlmClient,
    chunks: list[dict[str, Any]] | None = None,
    language_by_file: dict[str, str] | None = None,
) -> int:
    rows = chunks if chunks is not None else store.list_chunks(repo_id)
    need = [
        c
        for c in rows
        if c.get("embedded_hash") != c.get("content_hash")
    ]
    if not need:
        return 0

    vectors.ensure_collection(client.embedding_dim)

    code_texts = [f"{c.get('header', '')}\n{c.get('code', '')}" for c in need]
    code_vecs = asyncio.run(client.embed_many(code_texts))

    summary_texts = []
    summary_index: list[int] = []
    for i, c in enumerate(need):
        if c.get("summary"):
            summary_texts.append(c["summary"])
            summary_index.append(i)
    summary_vecs_map: dict[int, list[float]] = {}
    if summary_texts:
        svecs = asyncio.run(client.embed_many(summary_texts))
        for idx, vec in zip(summary_index, svecs, strict=True):
            summary_vecs_map[idx] = vec

    points: list[dict[str, Any]] = []
    lang_map = language_by_file or {}
    for i, c in enumerate(need):
        points.append(
            {
                "repo_id": repo_id,
                "chunk_id": c["id"],
                "symbol_id": c.get("symbol_id"),
                "file": c["file"],
                "kind": c.get("kind"),
                "start_line": c.get("start_line"),
                "end_line": c.get("end_line"),
                "language": lang_map.get(c["file"], ""),
                "content_hash": c.get("content_hash"),
                "code_vector": code_vecs[i],
                "summary_vector": summary_vecs_map.get(i),
            }
        )
        store.update_chunk_embedded(repo_id, c["id"], c["content_hash"])

    vectors.upsert_points(points)
    return len(points)
