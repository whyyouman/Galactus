"""keyword, semantic, graph, hybrid (RRF) retrieval."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

from prd2pr.llm.client import LlmClient
from prd2pr.storage.pg_store import PgStore
from prd2pr.storage.vector_store import QdrantVectorStore

Mode = Literal["keyword", "semantic", "graph", "hybrid"]


@dataclass
class SearchHit:
    rank: int
    score: float
    symbol: str | None
    file: str
    start_line: int | None
    end_line: int | None
    source: str
    chunk_id: str | None = None


def _rrf(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank)


def keyword_search(store: PgStore, repo_id: int, query: str, k: int = 10) -> list[SearchHit]:
    rows = store.keyword_search(repo_id, query, k=k)
    hits: list[SearchHit] = []
    for i, r in enumerate(rows, start=1):
        hits.append(
            SearchHit(
                rank=i,
                score=float(r.get("score") or 0),
                symbol=r.get("symbol_id"),
                file=r["file"],
                start_line=r.get("start_line"),
                end_line=r.get("end_line"),
                source="keyword",
                chunk_id=r.get("id"),
            )
        )
    return hits


def semantic_search(
    store: PgStore,
    vectors: QdrantVectorStore,
    client: LlmClient,
    repo_id: int,
    query: str,
    k: int = 10,
) -> list[SearchHit]:
    qvec = asyncio.run(client.embed([query]))[0]
    code_hits = vectors.search(repo_id, qvec, named="code", k=k)
    sum_hits = vectors.search(repo_id, qvec, named="summary", k=k)
    merged: dict[str, SearchHit] = {}
    for src_hits in (code_hits, sum_hits):
        for i, h in enumerate(src_hits, start=1):
            cid = h.get("chunk_id") or ""
            score = float(h.get("score") or 0)
            if cid not in merged or score > merged[cid].score:
                merged[cid] = SearchHit(
                    rank=0,
                    score=score,
                    symbol=h.get("symbol_id"),
                    file=h.get("file") or "",
                    start_line=h.get("start_line"),
                    end_line=h.get("end_line"),
                    source=h.get("source") or "semantic",
                    chunk_id=cid,
                )
    ordered = sorted(merged.values(), key=lambda x: -x.score)[:k]
    for i, h in enumerate(ordered, start=1):
        h.rank = i
    return ordered


def graph_search(
    store: PgStore, repo_id: int, query: str, k: int = 10
) -> list[SearchHit]:
    kw = keyword_search(store, repo_id, query, k=1)
    if not kw:
        return []
    start = kw[0].symbol or kw[0].chunk_id or ""
    if not start:
        return kw
    # Prefer symbol id from chunk
    if kw[0].chunk_id:
        chunks = store.list_chunks(repo_id)
        for c in chunks:
            if c["id"] == kw[0].chunk_id and c.get("symbol_id"):
                start = c["symbol_id"]
                break
    neighbor_ids = store.graph_neighbors(repo_id, start, hops=2)
    symbols = {s["id"]: s for s in store.list_symbols(repo_id)}
    hits = [
        SearchHit(
            rank=1,
            score=kw[0].score,
            symbol=kw[0].symbol,
            file=kw[0].file,
            start_line=kw[0].start_line,
            end_line=kw[0].end_line,
            source="graph:seed",
            chunk_id=kw[0].chunk_id,
        )
    ]
    for i, nid in enumerate(neighbor_ids[: k - 1], start=2):
        sym = symbols.get(nid)
        if sym:
            hits.append(
                SearchHit(
                    rank=i,
                    score=1.0 / i,
                    symbol=nid,
                    file=sym["file"],
                    start_line=sym["start_line"],
                    end_line=sym["end_line"],
                    source="graph",
                )
            )
        else:
            hits.append(
                SearchHit(
                    rank=i,
                    score=1.0 / i,
                    symbol=nid,
                    file="",
                    start_line=None,
                    end_line=None,
                    source="graph",
                )
            )
    return hits


def hybrid_search(
    store: PgStore,
    vectors: QdrantVectorStore | None,
    client: LlmClient | None,
    repo_id: int,
    query: str,
    k: int = 10,
) -> list[SearchHit]:
    kw = keyword_search(store, repo_id, query, k=k)
    sem: list[SearchHit] = []
    if vectors is not None and client is not None:
        try:
            sem = semantic_search(store, vectors, client, repo_id, query, k=k)
        except Exception:  # noqa: BLE001
            sem = []

    scores: dict[str, float] = {}
    meta: dict[str, SearchHit] = {}

    def key_of(h: SearchHit) -> str:
        return h.symbol or h.chunk_id or f"{h.file}:{h.start_line}"

    for i, h in enumerate(kw, start=1):
        key = key_of(h)
        scores[key] = scores.get(key, 0.0) + _rrf(i)
        meta[key] = h
    for i, h in enumerate(sem, start=1):
        key = key_of(h)
        scores[key] = scores.get(key, 0.0) + _rrf(i)
        meta.setdefault(key, h)

    ordered_keys = sorted(scores.keys(), key=lambda x: -scores[x])[:k]
    hits: list[SearchHit] = []
    for i, key in enumerate(ordered_keys, start=1):
        base = meta[key]
        hits.append(
            SearchHit(
                rank=i,
                score=scores[key],
                symbol=base.symbol,
                file=base.file,
                start_line=base.start_line,
                end_line=base.end_line,
                source="hybrid",
                chunk_id=base.chunk_id,
            )
        )

    # Add 1-hop graph neighbors of top 5
    symbols = {s["id"]: s for s in store.list_symbols(repo_id)}
    existing = {key_of(h) for h in hits}
    for seed in hits[:5]:
        start = seed.symbol
        if not start:
            continue
        for nid in store.graph_neighbors(repo_id, start, hops=1):
            if nid in existing:
                continue
            sym = symbols.get(nid)
            hits.append(
                SearchHit(
                    rank=len(hits) + 1,
                    score=0.0,
                    symbol=nid,
                    file=sym["file"] if sym else "",
                    start_line=sym["start_line"] if sym else None,
                    end_line=sym["end_line"] if sym else None,
                    source="hybrid:graph",
                )
            )
            existing.add(nid)
            if len(hits) >= k + 5:
                break
    return hits[: max(k, len(hits))]


def search(
    store: PgStore,
    repo_id: int,
    query: str,
    *,
    mode: Mode = "hybrid",
    k: int = 10,
    vectors: QdrantVectorStore | None = None,
    client: LlmClient | None = None,
) -> list[SearchHit]:
    if mode == "keyword":
        return keyword_search(store, repo_id, query, k=k)
    if mode == "semantic":
        if vectors is None or client is None:
            raise RuntimeError("semantic search requires embeddings")
        return semantic_search(store, vectors, client, repo_id, query, k=k)
    if mode == "graph":
        return graph_search(store, repo_id, query, k=k)
    return hybrid_search(store, vectors, client, repo_id, query, k=k)
