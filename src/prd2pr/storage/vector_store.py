"""Qdrant wrapper behind an interface (local mode under .prd2pr/qdrant/)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

COLLECTION = "chunks"
NAMESPACE = uuid.NAMESPACE_URL


def point_id(repo_id: int, chunk_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, f"{repo_id}:{chunk_id}"))


class VectorStore(Protocol):
    def ensure_collection(self, dim: int) -> None: ...
    def upsert_points(self, points: Sequence[dict[str, Any]]) -> None: ...
    def delete_by_chunk_ids(self, repo_id: int, chunk_ids: Sequence[str]) -> None: ...
    def delete_by_file(self, repo_id: int, file_path: str) -> None: ...
    def search(
        self,
        repo_id: int,
        vector: list[float],
        *,
        named: str,
        k: int = 10,
    ) -> list[dict[str, Any]]: ...


class QdrantVectorStore:
    def __init__(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self.client = QdrantClient(path=str(path))
        self._dim: int | None = None

    def ensure_collection(self, dim: int) -> None:
        self._dim = dim
        names = {c.name for c in self.client.get_collections().collections}
        if COLLECTION in names:
            return
        self.client.create_collection(
            collection_name=COLLECTION,
            vectors_config={
                "code": qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
                "summary": qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
            },
        )
        # Payload indexes are no-ops in local Qdrant mode; skip to avoid warnings.

    def upsert_points(self, points: Sequence[dict[str, Any]]) -> None:
        if not points:
            return
        qpoints: list[qm.PointStruct] = []
        for p in points:
            vectors: dict[str, list[float]] = {"code": p["code_vector"]}
            if p.get("summary_vector") is not None:
                vectors["summary"] = p["summary_vector"]
            elif self._dim:
                # Qdrant named vectors require all names on create; use zeros if no summary
                vectors["summary"] = [0.0] * self._dim
            qpoints.append(
                qm.PointStruct(
                    id=point_id(int(p["repo_id"]), p["chunk_id"]),
                    vector=vectors,
                    payload={
                        "repo_id": int(p["repo_id"]),
                        "chunk_id": p["chunk_id"],
                        "symbol_id": p.get("symbol_id"),
                        "file": p["file"],
                        "kind": p.get("kind"),
                        "start_line": p.get("start_line"),
                        "end_line": p.get("end_line"),
                        "language": p.get("language"),
                        "content_hash": p.get("content_hash"),
                    },
                )
            )
        self.client.upsert(collection_name=COLLECTION, points=qpoints)

    def delete_by_chunk_ids(self, repo_id: int, chunk_ids: Sequence[str]) -> None:
        if not chunk_ids:
            return
        ids = [point_id(repo_id, cid) for cid in chunk_ids]
        self.client.delete(
            collection_name=COLLECTION,
            points_selector=qm.PointIdsList(points=ids),
        )

    def delete_by_file(self, repo_id: int, file_path: str) -> None:
        self.client.delete(
            collection_name=COLLECTION,
            points_selector=qm.FilterSelector(
                filter=qm.Filter(
                    must=[
                        qm.FieldCondition(
                            key="repo_id", match=qm.MatchValue(value=repo_id)
                        ),
                        qm.FieldCondition(
                            key="file", match=qm.MatchValue(value=file_path)
                        ),
                    ]
                )
            ),
        )

    def search(
        self,
        repo_id: int,
        vector: list[float],
        *,
        named: str,
        k: int = 10,
    ) -> list[dict[str, Any]]:
        hits = self.client.search(
            collection_name=COLLECTION,
            query_vector=(named, vector),
            query_filter=qm.Filter(
                must=[
                    qm.FieldCondition(
                        key="repo_id", match=qm.MatchValue(value=repo_id)
                    )
                ]
            ),
            limit=k,
        )
        out: list[dict[str, Any]] = []
        for h in hits:
            payload = h.payload or {}
            out.append(
                {
                    "score": float(h.score),
                    "chunk_id": payload.get("chunk_id"),
                    "symbol_id": payload.get("symbol_id"),
                    "file": payload.get("file"),
                    "kind": payload.get("kind"),
                    "start_line": payload.get("start_line"),
                    "end_line": payload.get("end_line"),
                    "source": f"semantic:{named}",
                }
            )
        return out
