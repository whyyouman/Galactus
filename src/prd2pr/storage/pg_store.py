"""All PostgreSQL access behind one class."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from psycopg import Connection, sql


@dataclass
class RepoRow:
    id: int
    root_path: str
    name: str
    last_indexed_commit: str | None
    embed_model: str | None
    embed_dim: int | None
    last_run_stats: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


@dataclass
class FileRow:
    repo_id: int
    path: str
    language: str
    content_hash: str
    size_bytes: int | None
    parse_errors: int
    indexed_at: datetime


class PgStore:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    # --- repos ---

    def get_repo_by_path(self, root_path: str) -> RepoRow | None:
        row = self.conn.execute(
            "SELECT * FROM repos WHERE root_path = %s",
            (root_path,),
        ).fetchone()
        return self._repo(row) if row else None

    def get_repo(self, repo_id: int) -> RepoRow | None:
        row = self.conn.execute(
            "SELECT * FROM repos WHERE id = %s",
            (repo_id,),
        ).fetchone()
        return self._repo(row) if row else None

    def upsert_repo(self, root_path: str, name: str) -> RepoRow:
        existing = self.get_repo_by_path(root_path)
        if existing:
            return existing
        row = self.conn.execute(
            """
            INSERT INTO repos (root_path, name)
            VALUES (%s, %s)
            RETURNING *
            """,
            (root_path, name),
        ).fetchone()
        assert row is not None
        return self._repo(row)

    def update_repo_stats(
        self,
        repo_id: int,
        *,
        last_indexed_commit: str | None = None,
        embed_model: str | None = None,
        embed_dim: int | None = None,
        last_run_stats: dict[str, Any] | None = None,
    ) -> None:
        self.conn.execute(
            """
            UPDATE repos SET
                last_indexed_commit = COALESCE(%s, last_indexed_commit),
                embed_model = COALESCE(%s, embed_model),
                embed_dim = COALESCE(%s, embed_dim),
                last_run_stats = COALESCE(%s::jsonb, last_run_stats),
                updated_at = now()
            WHERE id = %s
            """,
            (
                last_indexed_commit,
                embed_model,
                embed_dim,
                json.dumps(last_run_stats) if last_run_stats is not None else None,
                repo_id,
            ),
        )

    def try_advisory_lock(self, repo_id: int) -> bool:
        row = self.conn.execute(
            "SELECT pg_try_advisory_lock(%s) AS ok",
            (repo_id,),
        ).fetchone()
        return bool(row and row["ok"])

    def advisory_unlock(self, repo_id: int) -> None:
        self.conn.execute("SELECT pg_advisory_unlock(%s)", (repo_id,))

    # --- files ---

    def list_files(self, repo_id: int) -> list[FileRow]:
        rows = self.conn.execute(
            "SELECT * FROM files WHERE repo_id = %s ORDER BY path",
            (repo_id,),
        ).fetchall()
        return [self._file(r) for r in rows]

    def get_file_hashes(self, repo_id: int) -> dict[str, str]:
        rows = self.conn.execute(
            "SELECT path, content_hash FROM files WHERE repo_id = %s",
            (repo_id,),
        ).fetchall()
        return {r["path"]: r["content_hash"] for r in rows}

    def upsert_file(
        self,
        repo_id: int,
        path: str,
        language: str,
        content_hash: str,
        size_bytes: int | None,
        parse_errors: int = 0,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO files (repo_id, path, language, content_hash, size_bytes, parse_errors)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (repo_id, path) DO UPDATE SET
                language = EXCLUDED.language,
                content_hash = EXCLUDED.content_hash,
                size_bytes = EXCLUDED.size_bytes,
                parse_errors = EXCLUDED.parse_errors,
                indexed_at = now()
            """,
            (repo_id, path, language, content_hash, size_bytes, parse_errors),
        )

    def delete_file(self, repo_id: int, path: str) -> None:
        # Cascades to symbols/chunks via FK; edges by src_file cleaned separately
        self.conn.execute(
            "DELETE FROM edges WHERE repo_id = %s AND src_file = %s",
            (repo_id, path),
        )
        self.conn.execute(
            "DELETE FROM files WHERE repo_id = %s AND path = %s",
            (repo_id, path),
        )

    def delete_file_derived(self, repo_id: int, path: str) -> None:
        """Remove symbols, chunks, and outgoing edges for a file (keep file row)."""
        self.conn.execute(
            "DELETE FROM edges WHERE repo_id = %s AND src_file = %s",
            (repo_id, path),
        )
        self.conn.execute(
            "DELETE FROM chunks WHERE repo_id = %s AND file = %s",
            (repo_id, path),
        )
        self.conn.execute(
            "DELETE FROM symbols WHERE repo_id = %s AND file = %s",
            (repo_id, path),
        )

    # --- symbols ---

    def insert_symbols(self, repo_id: int, symbols: Sequence[dict[str, Any]]) -> None:
        if not symbols:
            return
        with self.conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO symbols (
                    repo_id, id, file, name, qualified_name, kind,
                    start_line, end_line, signature, docstring, parent_id, rank
                ) VALUES (
                    %(repo_id)s, %(id)s, %(file)s, %(name)s, %(qualified_name)s, %(kind)s,
                    %(start_line)s, %(end_line)s, %(signature)s, %(docstring)s,
                    %(parent_id)s, %(rank)s
                )
                """,
                [{**s, "repo_id": repo_id, "rank": s.get("rank", 0.0)} for s in symbols],
            )

    def list_symbols(self, repo_id: int, file: str | None = None) -> list[dict[str, Any]]:
        if file:
            rows = self.conn.execute(
                "SELECT * FROM symbols WHERE repo_id = %s AND file = %s ORDER BY start_line",
                (repo_id, file),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM symbols WHERE repo_id = %s ORDER BY file, start_line",
                (repo_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def update_symbol_ranks(self, repo_id: int, ranks: dict[str, float]) -> None:
        if not ranks:
            return
        with self.conn.cursor() as cur:
            cur.executemany(
                "UPDATE symbols SET rank = %s WHERE repo_id = %s AND id = %s",
                [(score, repo_id, sid) for sid, score in ranks.items()],
            )

    # --- chunks ---

    def insert_chunks(self, repo_id: int, chunks: Sequence[dict[str, Any]]) -> None:
        if not chunks:
            return
        with self.conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO chunks (
                    repo_id, id, symbol_id, file, start_line, end_line,
                    header, code, content_hash, summary, summary_hash,
                    embedded_hash, identifiers
                ) VALUES (
                    %(repo_id)s, %(id)s, %(symbol_id)s, %(file)s, %(start_line)s, %(end_line)s,
                    %(header)s, %(code)s, %(content_hash)s, %(summary)s, %(summary_hash)s,
                    %(embedded_hash)s, %(identifiers)s
                )
                """,
                [
                    {
                        **c,
                        "repo_id": repo_id,
                        "summary": c.get("summary"),
                        "summary_hash": c.get("summary_hash"),
                        "embedded_hash": c.get("embedded_hash"),
                        "identifiers": c.get("identifiers", ""),
                    }
                    for c in chunks
                ],
            )

    def list_chunks(self, repo_id: int, file: str | None = None) -> list[dict[str, Any]]:
        if file:
            rows = self.conn.execute(
                "SELECT * FROM chunks WHERE repo_id = %s AND file = %s",
                (repo_id, file),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM chunks WHERE repo_id = %s",
                (repo_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def update_chunk_summary(
        self, repo_id: int, chunk_id: str, summary: str, summary_hash: str
    ) -> None:
        self.conn.execute(
            """
            UPDATE chunks SET summary = %s, summary_hash = %s
            WHERE repo_id = %s AND id = %s
            """,
            (summary, summary_hash, repo_id, chunk_id),
        )

    def update_chunk_embedded(self, repo_id: int, chunk_id: str, embedded_hash: str) -> None:
        self.conn.execute(
            """
            UPDATE chunks SET embedded_hash = %s
            WHERE repo_id = %s AND id = %s
            """,
            (embedded_hash, repo_id, chunk_id),
        )

    def update_chunk_identifiers(self, repo_id: int, chunk_id: str, identifiers: str) -> None:
        self.conn.execute(
            """
            UPDATE chunks SET identifiers = %s
            WHERE repo_id = %s AND id = %s
            """,
            (identifiers, repo_id, chunk_id),
        )

    def keyword_search(
        self, repo_id: int, query: str, k: int = 10
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT c.*,
                   ts_rank_cd(c.search_tsv, websearch_to_tsquery('simple', %s)) AS score
            FROM chunks c
            WHERE c.repo_id = %s
              AND c.search_tsv @@ websearch_to_tsquery('simple', %s)
            ORDER BY score DESC
            LIMIT %s
            """,
            (query, repo_id, query, k),
        ).fetchall()
        return [dict(r) for r in rows]

    # --- edges ---

    def insert_edges(self, repo_id: int, edges: Sequence[dict[str, Any]]) -> None:
        if not edges:
            return
        with self.conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO edges (repo_id, src, dst, type, src_file, resolved)
                VALUES (%(repo_id)s, %(src)s, %(dst)s, %(type)s, %(src_file)s, %(resolved)s)
                ON CONFLICT (repo_id, src, dst, type) DO UPDATE SET
                    src_file = EXCLUDED.src_file,
                    resolved = EXCLUDED.resolved
                """,
                [
                    {
                        **e,
                        "repo_id": repo_id,
                        "resolved": e.get("resolved", True),
                    }
                    for e in edges
                ],
            )

    def list_edges(self, repo_id: int) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM edges WHERE repo_id = %s",
            (repo_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def mark_dangling_edges_unresolved(self, repo_id: int) -> int:
        """Edges whose dst is not an external: and not a known symbol/file → unresolved."""
        result = self.conn.execute(
            """
            UPDATE edges e SET resolved = FALSE
            WHERE e.repo_id = %s
              AND e.resolved = TRUE
              AND e.dst NOT LIKE 'external:%%'
              AND NOT EXISTS (
                  SELECT 1 FROM symbols s
                  WHERE s.repo_id = e.repo_id AND s.id = e.dst
              )
              AND NOT EXISTS (
                  SELECT 1 FROM files f
                  WHERE f.repo_id = e.repo_id AND f.path = e.dst
              )
            """,
            (repo_id,),
        )
        return result.rowcount or 0

    def graph_neighbors(
        self, repo_id: int, start_id: str, hops: int = 2
    ) -> list[str]:
        rows = self.conn.execute(
            """
            WITH RECURSIVE nbr(id, depth) AS (
                SELECT %s::text, 0
                UNION
                SELECT CASE WHEN e.src = n.id THEN e.dst ELSE e.src END, n.depth + 1
                FROM edges e
                JOIN nbr n ON e.src = n.id OR e.dst = n.id
                WHERE e.repo_id = %s AND e.resolved AND n.depth < %s
            )
            SELECT DISTINCT id FROM nbr WHERE id <> %s
            """,
            (start_id, repo_id, hops, start_id),
        ).fetchall()
        return [r["id"] for r in rows]

    # --- counts / status ---

    def counts(self, repo_id: int) -> dict[str, int]:
        def _count(table: str) -> int:
            row = self.conn.execute(
                sql.SQL("SELECT COUNT(*) AS n FROM {} WHERE repo_id = %s").format(
                    sql.Identifier(table)
                ),
                (repo_id,),
            ).fetchone()
            return int(row["n"]) if row else 0

        unresolved = self.conn.execute(
            """
            SELECT COUNT(*) AS n FROM edges
            WHERE repo_id = %s AND resolved = FALSE
            """,
            (repo_id,),
        ).fetchone()
        return {
            "files": _count("files"),
            "symbols": _count("symbols"),
            "chunks": _count("chunks"),
            "edges": _count("edges"),
            "unresolved_edges": int(unresolved["n"]) if unresolved else 0,
        }

    @staticmethod
    def _repo(row: Any) -> RepoRow:
        stats = row["last_run_stats"]
        if isinstance(stats, str):
            stats = json.loads(stats)
        return RepoRow(
            id=int(row["id"]),
            root_path=row["root_path"],
            name=row["name"],
            last_indexed_commit=row["last_indexed_commit"],
            embed_model=row["embed_model"],
            embed_dim=row["embed_dim"],
            last_run_stats=stats,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _file(row: Any) -> FileRow:
        return FileRow(
            repo_id=int(row["repo_id"]),
            path=row["path"],
            language=row["language"],
            content_hash=row["content_hash"],
            size_bytes=row["size_bytes"],
            parse_errors=int(row["parse_errors"]),
            indexed_at=row["indexed_at"],
        )
