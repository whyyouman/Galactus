"""Orchestrates steps 1–7 with Rich progress output."""

from __future__ import annotations

import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from prd2pr.config import Prd2prConfig
from prd2pr.indexing.differ import DiffResult, diff_files
from prd2pr.indexing.embedder import embed_chunks
from prd2pr.indexing.extractor import extract_file
from prd2pr.indexing.graph import build_context, build_edges_for_file
from prd2pr.indexing.keyword import fill_identifiers_for_chunks
from prd2pr.indexing.parser import parse_file
from prd2pr.indexing.repo_map import build_repo_map
from prd2pr.indexing.summarizer import summarize_chunks
from prd2pr.indexing.walker import walk_repo
from prd2pr.llm.client import LlmClient
from prd2pr.storage.db import connection
from prd2pr.storage.migrate import has_pending_migrations
from prd2pr.storage.pg_store import PgStore
from prd2pr.storage.vector_store import QdrantVectorStore

console = Console()
logger = logging.getLogger("prd2pr")


@dataclass
class RunStats:
    files_walked: int = 0
    files_skipped: int = 0
    files_new: int = 0
    files_changed: int = 0
    files_deleted: int = 0
    files_unchanged: int = 0
    files_processed: int = 0
    symbols: int = 0
    chunks: int = 0
    edges: int = 0
    unresolved_edges: int = 0
    parse_errors: int = 0
    llm_tokens: int = 0
    llm_cost: float = 0.0
    llm_calls: int = 0
    duration_s: float = 0.0
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            **{k: v for k, v in self.__dict__.items() if k != "errors"},
            "errors": list(self.errors),
        }


def _git_head(repo: Path) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _write_jsonl_log(repo: Path, stats: RunStats) -> Path:
    log_dir = repo / ".prd2pr" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = log_dir / f"{ts}.jsonl"
    path.write_text(json.dumps(stats.as_dict()) + "\n", encoding="utf-8")
    return path


def run_index(
    repo_path: Path,
    config: Prd2prConfig,
    *,
    full: bool = False,
    no_embed: bool = False,
    no_summaries: bool = False,
) -> RunStats:
    started = time.perf_counter()
    stats = RunStats()
    repo_path = repo_path.resolve()

    if has_pending_migrations():
        raise RuntimeError(
            "Pending database migrations. Run `prd2pr db migrate` before indexing."
        )

    with connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(repo_path))
        if repo is None:
            raise RuntimeError(
                f"Repo {repo_path} is not registered. Run `prd2pr init` first."
            )
        repo_id = repo.id

        if not store.try_advisory_lock(repo_id):
            raise RuntimeError(
                f"Another prd2pr index is already running for repo_id={repo_id}."
            )

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                # 1. walk
                t = progress.add_task("walk", total=None)
                walked = walk_repo(repo_path, config)
                progress.update(t, completed=1, total=1)
                stats.files_walked = len(walked.files)
                stats.files_skipped = walked.skipped

                # 2. diff
                t = progress.add_task("diff", total=None)
                existing = store.get_file_hashes(repo_id)
                diff: DiffResult = diff_files(walked.files, existing, full=full)
                progress.update(t, completed=1, total=1)
                stats.files_new = len(diff.new)
                stats.files_changed = len(diff.changed)
                stats.files_deleted = len(diff.deleted)
                stats.files_unchanged = len(diff.unchanged)

                vector_store = QdrantVectorStore(repo_path / ".prd2pr" / "qdrant")

                # Cleanup deleted
                for path in diff.deleted:
                    try:
                        vector_store.delete_by_file(repo_id, path)
                    except Exception:  # noqa: BLE001
                        pass
                    store.delete_file(repo_id, path)

                # 3–4 parse + extract per file
                to_process = diff.to_process
                t = progress.add_task("parse+extract", total=max(len(to_process), 1))
                extractions: dict[str, Any] = {}
                sources: dict[str, str] = {}
                languages: dict[str, str] = {}

                for wf in to_process:
                    try:
                        raw_bytes = wf.abs_path.read_bytes()
                        sources[wf.path] = raw_bytes.decode("utf-8", errors="replace")
                        languages[wf.path] = wf.language
                        parsed = parse_file(raw_bytes, wf.language)
                        extraction = extract_file(wf.path, parsed, config.limits)
                        extractions[wf.path] = extraction
                        stats.parse_errors += extraction.parse_errors

                        # Per-file transaction: replace derived data + upsert file
                        with conn.transaction():
                            if wf.path in existing:
                                old_chunks = [
                                    c["id"]
                                    for c in store.list_chunks(repo_id, file=wf.path)
                                ]
                                store.delete_file_derived(repo_id, wf.path)
                                if old_chunks:
                                    try:
                                        vector_store.delete_by_chunk_ids(
                                            repo_id, old_chunks
                                        )
                                    except Exception:  # noqa: BLE001
                                        pass
                            store.upsert_file(
                                repo_id,
                                wf.path,
                                wf.language,
                                wf.content_hash,
                                wf.size_bytes,
                                parse_errors=extraction.parse_errors,
                            )
                            store.insert_symbols(repo_id, extraction.symbols)
                            store.insert_chunks(repo_id, extraction.chunks)
                        stats.files_processed += 1
                        stats.symbols += len(extraction.symbols)
                        stats.chunks += len(extraction.chunks)
                    except Exception as exc:  # noqa: BLE001
                        msg = f"{wf.path}: {exc}"
                        logger.exception(msg)
                        stats.errors.append(msg)
                        console.print(f"[yellow]skip[/yellow] {msg}")
                    progress.advance(t)

                # Refresh all symbols/files for graph context
                all_symbols = store.list_symbols(repo_id)
                all_files = [f.path for f in store.list_files(repo_id)]
                ctx = build_context(repo_path, all_symbols, all_files)

                # Collect changed chunk rows for 5a/5b
                changed_chunks: list[dict[str, Any]] = []
                for path in extractions:
                    changed_chunks.extend(store.list_chunks(repo_id, file=path))

                llm: LlmClient | None = None
                do_summaries = config.summaries and not no_summaries
                do_embed = not no_embed
                if do_summaries or do_embed:
                    llm = LlmClient(
                        summary_model=config.llm.summary_model,
                        embedding_model=config.llm.embedding_model,
                        embedding_dim=config.llm.embedding_dim,
                        concurrency=config.llm.concurrency,
                    )

                def step_keyword() -> None:
                    fill_identifiers_for_chunks(store, repo_id, changed_chunks or None)

                def step_graph() -> None:
                    all_edges: list[dict[str, Any]] = []
                    # Rebuild edges for processed files; also re-resolve dangling at end
                    for path, extraction in extractions.items():
                        edges = build_edges_for_file(
                            path,
                            languages[path],
                            extraction.raw,
                            ctx,
                            sources.get(path),
                        )
                        all_edges.extend(edges)
                    if all_edges:
                        store.insert_edges(repo_id, all_edges)
                    store.mark_dangling_edges_unresolved(repo_id)

                def step_summaries() -> None:
                    if not do_summaries or llm is None:
                        return
                    summarize_chunks(
                        store, repo_id, llm, config.limits, changed_chunks or None
                    )

                def step_embed() -> None:
                    if not do_embed or llm is None:
                        return
                    # Refresh chunks after summaries
                    chunks = changed_chunks or store.list_chunks(repo_id)
                    # re-read to get summaries
                    fresh: list[dict[str, Any]] = []
                    for c in chunks:
                        rows = [
                            x
                            for x in store.list_chunks(repo_id, file=c["file"])
                            if x["id"] == c["id"]
                        ]
                        fresh.extend(rows or [c])
                    # language map from DB
                    lang_map = {f.path: f.language for f in store.list_files(repo_id)}
                    embed_chunks(
                        store, vector_store, repo_id, llm, fresh, language_by_file=lang_map
                    )

                t = progress.add_task("keyword+graph+llm", total=3)
                # Same psycopg connection is not thread-safe — run serially.
                # (5a/5b/5c are independent logically; parallelism can return later
                # with per-step connections.)
                step_keyword()
                progress.advance(t)
                step_graph()
                progress.advance(t)
                step_summaries()
                step_embed()
                progress.advance(t)

                if llm:
                    stats.llm_tokens = llm.total_tokens
                    stats.llm_cost = llm.total_cost
                    stats.llm_calls = llm.call_count

                # 6. repo map
                t = progress.add_task("repo map", total=None)
                build_repo_map(store, repo_id, repo_path, config.repo_map_tokens)
                progress.update(t, completed=1, total=1)

                # 7. commit stats
                counts = store.counts(repo_id)
                stats.edges = counts["edges"]
                stats.unresolved_edges = counts["unresolved_edges"]
                # Prefer total DB counts for symbols/chunks when incremental
                if not to_process and not diff.deleted:
                    stats.symbols = counts["symbols"]
                    stats.chunks = counts["chunks"]

                stats.duration_s = time.perf_counter() - started
                store.update_repo_stats(
                    repo_id,
                    last_indexed_commit=_git_head(repo_path),
                    embed_model=None if no_embed else config.llm.embedding_model,
                    embed_dim=None if no_embed else config.llm.embedding_dim,
                    last_run_stats=stats.as_dict(),
                )
                conn.commit()
        finally:
            store.advisory_unlock(repo_id)

    _write_jsonl_log(repo_path, stats)
    _print_summary(stats)
    return stats


def _print_summary(stats: RunStats) -> None:
    table = Table(title="Index run summary")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    rows = [
        ("files walked", stats.files_walked),
        ("skipped", stats.files_skipped),
        ("new / changed / deleted / unchanged",
         f"{stats.files_new}/{stats.files_changed}/{stats.files_deleted}/{stats.files_unchanged}"),
        ("processed", stats.files_processed),
        ("symbols", stats.symbols),
        ("chunks", stats.chunks),
        ("edges (unresolved)", f"{stats.edges} ({stats.unresolved_edges})"),
        ("parse errors", stats.parse_errors),
        ("LLM calls / tokens", f"{stats.llm_calls} / {stats.llm_tokens}"),
        ("LLM cost est.", f"${stats.llm_cost:.4f}"),
        ("duration (s)", f"{stats.duration_s:.2f}"),
    ]
    for k, v in rows:
        table.add_row(k, str(v))
    console.print(table)
