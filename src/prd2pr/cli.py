"""Typer CLI: db migrate, init, index, status, search."""

from __future__ import annotations

from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from prd2pr import __version__
from prd2pr.config import (
    DEFAULT_CONFIG_NAME,
    find_repo_root,
    load_config,
    write_default_config,
)
from prd2pr.storage.db import close_pool, connection, init_pool
from prd2pr.storage.migrate import migrate as run_migrate
from prd2pr.storage.pg_store import PgStore

app = typer.Typer(
    name="prd2pr",
    help="PRD-to-PR indexing engine",
    no_args_is_help=True,
)
db_app = typer.Typer(help="Database commands")
app.add_typer(db_app, name="db")
console = Console()


def _load_env_files() -> None:
    """Load .env from cwd and parents (does not override existing env vars)."""
    seen: set[Path] = set()
    candidates = [Path.cwd(), *Path.cwd().resolve().parents]
    # Also try package checkout root (…/Galactus) when installed editable
    try:
        pkg_root = Path(__file__).resolve().parents[2]
        candidates.append(pkg_root)
    except IndexError:
        pass
    for base in candidates:
        env_path = (base / ".env").resolve()
        if env_path in seen or not env_path.is_file():
            continue
        seen.add(env_path)
        load_dotenv(env_path, override=False)


def _resolve_repo(repo: Path | None) -> Path:
    if repo is not None:
        return repo.resolve()
    return find_repo_root().resolve()


@app.callback()
def main_callback() -> None:
    """prd2pr — index a local repo for PRD-driven planning."""
    _load_env_files()


@db_app.command("migrate")
def db_migrate() -> None:
    """Create/upgrade tables in PostgreSQL."""
    try:
        applied = run_migrate()
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    if applied:
        console.print(f"[green]Applied migrations:[/green] {applied}")
    else:
        console.print("[green]Migrations up to date.[/green]")


@app.command("init")
def init_cmd(
    repo: Path | None = typer.Option(
        None, "--repo", help="Path to the repository root"
    ),
) -> None:
    """Write prd2pr.yaml and register the repo (repo_id)."""
    root = (repo or Path.cwd()).resolve()
    if not root.is_dir():
        console.print(f"[red]Not a directory: {root}[/red]")
        raise typer.Exit(1)

    config_path = root / DEFAULT_CONFIG_NAME
    if not config_path.exists():
        write_default_config(root)
        console.print(f"Wrote {config_path}")
    else:
        console.print(f"Config already exists: {config_path}")

    config = load_config(root)
    try:
        init_pool(url_env=config.database.url_env, pool_size=config.database.pool_size)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    with connection() as conn:
        store = PgStore(conn)
        row = store.upsert_repo(str(root), root.name)
        conn.commit()
    console.print(f"[green]Registered repo_id={row.id}[/green] path={row.root_path}")


@app.command("index")
def index_cmd(
    repo: Path | None = typer.Option(None, "--repo"),
    full: bool = typer.Option(False, "--full", help="Rebuild all files"),
    no_embed: bool = typer.Option(False, "--no-embed"),
    no_summaries: bool = typer.Option(False, "--no-summaries"),
) -> None:
    """Run the indexing pipeline."""
    from prd2pr.indexing.pipeline import run_index

    root = _resolve_repo(repo)
    try:
        config = load_config(root)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    try:
        init_pool(url_env=config.database.url_env, pool_size=config.database.pool_size)
        run_index(
            root,
            config,
            full=full,
            no_embed=no_embed,
            no_summaries=no_summaries or not config.summaries,
        )
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    finally:
        close_pool()


@app.command("status")
def status_cmd(
    repo: Path | None = typer.Option(None, "--repo"),
) -> None:
    """Show counts, last indexed commit, stale files."""
    root = _resolve_repo(repo)
    try:
        config = load_config(root)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    try:
        init_pool(url_env=config.database.url_env, pool_size=config.database.pool_size)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    from prd2pr.indexing.differ import diff_files
    from prd2pr.indexing.walker import walk_repo

    with connection() as conn:
        store = PgStore(conn)
        row = store.get_repo_by_path(str(root))
        if row is None:
            console.print("[red]Repo not registered. Run prd2pr init.[/red]")
            raise typer.Exit(1)
        counts = store.counts(row.id)
        hashes = store.get_file_hashes(row.id)
        walked = walk_repo(root, config)
        diff = diff_files(walked.files, hashes)

    table = Table(title=f"Status — {root.name} (repo_id={row.id})")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("root", row.root_path)
    table.add_row("last_indexed_commit", row.last_indexed_commit or "(none)")
    table.add_row("embed_model", row.embed_model or "(none)")
    table.add_row("files", str(counts["files"]))
    table.add_row("symbols", str(counts["symbols"]))
    table.add_row("chunks", str(counts["chunks"]))
    table.add_row("edges", str(counts["edges"]))
    table.add_row("unresolved_edges", str(counts["unresolved_edges"]))
    table.add_row("stale (changed)", str(len(diff.changed)))
    table.add_row("new on disk", str(len(diff.new)))
    table.add_row("deleted since index", str(len(diff.deleted)))
    console.print(table)


@app.command("search")
def search_cmd(
    query: str = typer.Argument(..., help="Search query"),
    repo: Path | None = typer.Option(None, "--repo"),
    k: int = typer.Option(10, "--k"),
    mode: str = typer.Option(
        "hybrid", "--mode", help="keyword|semantic|graph|hybrid"
    ),
) -> None:
    """Debug retrieval quality."""
    from prd2pr.llm.client import LlmClient
    from prd2pr.search.retriever import search
    from prd2pr.storage.vector_store import QdrantVectorStore

    root = _resolve_repo(repo)
    try:
        config = load_config(root)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if mode not in ("keyword", "semantic", "graph", "hybrid"):
        console.print(f"[red]Unknown mode: {mode}[/red]")
        raise typer.Exit(1)

    try:
        init_pool(url_env=config.database.url_env, pool_size=config.database.pool_size)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    vectors = QdrantVectorStore(root / ".prd2pr" / "qdrant")
    client = LlmClient(
        summary_model=config.llm.summary_model,
        embedding_model=config.llm.embedding_model,
        embedding_dim=config.llm.embedding_dim,
        concurrency=config.llm.concurrency,
    )

    with connection() as conn:
        store = PgStore(conn)
        row = store.get_repo_by_path(str(root))
        if row is None:
            console.print("[red]Repo not registered.[/red]")
            raise typer.Exit(1)
        try:
            hits = search(
                store,
                row.id,
                query,
                mode=mode,  # type: ignore[arg-type]
                k=k,
                vectors=vectors,
                client=client,
            )
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Search failed: {exc}[/red]")
            raise typer.Exit(1) from exc

    table = Table(title=f"search ({mode}) — {query!r}")
    table.add_column("#", justify="right")
    table.add_column("score", justify="right")
    table.add_column("symbol")
    table.add_column("location")
    table.add_column("source")
    for h in hits:
        loc = h.file
        if h.start_line is not None:
            loc = f"{h.file}:{h.start_line}-{h.end_line}"
        table.add_row(
            str(h.rank),
            f"{h.score:.4f}",
            (h.symbol or "")[:60],
            loc,
            h.source,
        )
    console.print(table)


@app.command("version")
def version_cmd() -> None:
    console.print(__version__)


if __name__ == "__main__":
    app()
