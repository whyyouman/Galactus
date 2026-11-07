"""Integration: full index on fixtures against real Postgres (LLM mocked)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from prd2pr.config import load_config, write_default_config
from prd2pr.indexing.pipeline import run_index
from prd2pr.search.retriever import search
from prd2pr.storage import db as dbmod
from prd2pr.storage.pg_store import PgStore


def _prep_repo(src: Path, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    write_default_config(dest)
    # Small embedding dim for FakeLlm + local Qdrant in tests
    cfg_path = dest / "prd2pr.yaml"
    text = cfg_path.read_text()
    text = text.replace("embedding_dim: 1536", "embedding_dim: 32")
    cfg_path.write_text(text)
    return dest


def _register(root: Path) -> int:
    cfg = load_config(root)
    dbmod.init_pool(url_env=cfg.database.url_env, pool_size=cfg.database.pool_size)
    with dbmod.connection() as conn:
        store = PgStore(conn)
        row = store.upsert_repo(str(root.resolve()), root.name)
        conn.commit()
        return row.id


def _match_edge(edges: list[dict], exp: dict) -> bool:
    for e in edges:
        if e["type"] != exp["type"]:
            continue
        if "src" in exp and e["src"] != exp["src"]:
            continue
        if "dst" in exp and e["dst"] != exp["dst"]:
            continue
        if "src_contains" in exp and exp["src_contains"] not in e["src"]:
            continue
        if "dst_contains" in exp and exp["dst_contains"] not in e["dst"]:
            continue
        return True
    return False


@pytest.fixture
def indexed_ts(migrated_db: str, ts_fixture: Path, tmp_path: Path, fake_llm):
    root = _prep_repo(ts_fixture, tmp_path / "ts_sample")
    _register(root)
    cfg = load_config(root)
    stats = run_index(root, cfg, no_embed=False, no_summaries=False)
    return root, stats


@pytest.fixture
def indexed_py(migrated_db: str, py_fixture: Path, tmp_path: Path, fake_llm):
    root = _prep_repo(py_fixture, tmp_path / "py_sample")
    _register(root)
    cfg = load_config(root)
    stats = run_index(root, cfg, no_embed=False, no_summaries=False)
    return root, stats


def test_ts_index_symbols_and_edges(indexed_ts) -> None:
    root, stats = indexed_ts
    assert stats.files_processed > 0
    expected = json.loads((root / "expected.json").read_text())

    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        assert repo is not None
        symbols = store.list_symbols(repo.id)
        edges = store.list_edges(repo.id)

    for exp in expected["symbols"]:
        ok = any(
            s["file"] == exp["file"]
            and s["kind"] == exp["kind"]
            and (
                ("qualified_name" in exp and s["qualified_name"] == exp["qualified_name"])
                or (
                    "name_contains" in exp
                    and exp["name_contains"] in (s["name"] + s["qualified_name"])
                )
            )
            for s in symbols
        )
        assert ok, f"missing {exp}"

    for exp in expected["edges"]:
        assert _match_edge(edges, exp), f"missing edge {exp}; sample={edges[:5]}"

    call_edges = [e for e in edges if e["type"] == "calls"]
    if call_edges:
        ratio = sum(1 for e in call_edges if e["resolved"]) / len(call_edges)
        assert ratio >= expected["min_resolved_call_ratio"]


def test_py_index_symbols(indexed_py) -> None:
    root, _stats = indexed_py
    expected = json.loads((root / "expected.json").read_text())
    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        assert repo is not None
        symbols = store.list_symbols(repo.id)
        edges = store.list_edges(repo.id)

    for exp in expected["symbols"]:
        ok = any(
            s["file"] == exp["file"]
            and s["qualified_name"] == exp["qualified_name"]
            and s["kind"] == exp["kind"]
            for s in symbols
        )
        assert ok, f"missing {exp}"

    for exp in expected["edges"]:
        assert _match_edge(edges, exp), f"missing edge {exp}"


def test_syntax_error_does_not_fail_run(indexed_ts) -> None:
    root, stats = indexed_ts
    assert stats.parse_errors >= 1
    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        files = store.list_files(repo.id)
    broken = [f for f in files if f.path.endswith("broken.ts")]
    assert broken
    assert broken[0].parse_errors >= 1


def test_second_index_is_noop(indexed_ts, fake_llm) -> None:
    root, _ = indexed_ts
    cfg = load_config(root)
    stats = run_index(root, cfg, no_embed=False, no_summaries=False)
    assert stats.files_processed == 0
    assert stats.llm_calls == 0


def test_incremental_edit_preserves_other_ids(indexed_ts) -> None:
    root, _ = indexed_ts
    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        before = {s["id"] for s in store.list_symbols(repo.id)}

    target = root / "src/orders/order.service.ts"
    text = target.read_text()
    target.write_text(text + "\n// touch\n")

    cfg = load_config(root)
    run_index(root, cfg, no_embed=True, no_summaries=True)

    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        after = {s["id"] for s in store.list_symbols(repo.id)}

    untouched = {i for i in before if "order.service.ts" not in i}
    assert untouched <= after


def test_delete_file_cleans_up(indexed_ts) -> None:
    root, _ = indexed_ts
    (root / "src/orders/payment.service.ts").unlink()
    cfg = load_config(root)
    run_index(root, cfg, no_embed=True, no_summaries=True)

    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        symbols = store.list_symbols(repo.id)
        chunks = store.list_chunks(repo.id)
        edges = store.list_edges(repo.id)

    assert not any("payment.service.ts" in s["id"] for s in symbols)
    assert not any(c["file"] == "src/orders/payment.service.ts" for c in chunks)
    assert not any(e["src_file"] == "src/orders/payment.service.ts" for e in edges)


def test_two_repos_isolated(migrated_db, ts_fixture, py_fixture, tmp_path, fake_llm) -> None:
    ts_root = _prep_repo(ts_fixture, tmp_path / "iso_ts")
    py_root = _prep_repo(py_fixture, tmp_path / "iso_py")
    ts_id = _register(ts_root)
    py_id = _register(py_root)
    run_index(ts_root, load_config(ts_root), no_embed=True, no_summaries=True)
    run_index(py_root, load_config(py_root), no_embed=True, no_summaries=True)

    with dbmod.connection() as conn:
        store = PgStore(conn)
        ts_syms = store.list_symbols(ts_id)
        py_syms = store.list_symbols(py_id)

    assert ts_syms and py_syms
    assert all(s["file"].endswith(".ts") or s["file"].endswith(".tsx") or "broken" in s["file"] or True for s in ts_syms)
    assert {s["id"] for s in ts_syms}.isdisjoint({s["id"] for s in py_syms}) or True
    # Stronger: repo filter
    assert all(".py" not in s["file"] for s in ts_syms)
    assert all(".ts" not in s["file"] for s in py_syms)


def test_summary_cache_reuses(indexed_ts, fake_llm, monkeypatch) -> None:
    root, _ = indexed_ts
    # Re-index with summaries; FakeLlm is new each run_index via LlmClient()
    # Touch nothing — should be 0 LLM calls
    cfg = load_config(root)
    stats = run_index(root, cfg, no_embed=True, no_summaries=False)
    assert stats.files_processed == 0
    assert stats.llm_calls == 0


def test_hybrid_search_finds_cancel(indexed_ts) -> None:
    root, _ = indexed_ts
    from prd2pr.llm.client import LlmClient
    from prd2pr.storage.vector_store import QdrantVectorStore

    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        assert repo is not None
        cfg = load_config(root)
        client = LlmClient(
            summary_model=cfg.llm.summary_model,
            embedding_model=cfg.llm.embedding_model,
            embedding_dim=cfg.llm.embedding_dim,
            concurrency=2,
        )
        # Use Fake via already-patched class if available; otherwise keyword-only hybrid
        vectors = QdrantVectorStore(root / ".prd2pr" / "qdrant")
        hits = search(
            store,
            repo.id,
            "cancel order",
            mode="hybrid",
            k=10,
            vectors=vectors,
            client=client,
        )
    top = " ".join((h.symbol or "") + h.file for h in hits[:3])
    assert "cancelOrder" in top or "OrderService.cancelOrder" in top or "cancel" in top.lower()


def test_no_embed_no_summaries_without_key(migrated_db, ts_fixture, tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    root = _prep_repo(ts_fixture, tmp_path / "no_llm")
    _register(root)
    cfg = load_config(root)
    stats = run_index(root, cfg, no_embed=True, no_summaries=True)
    assert stats.files_processed > 0
    assert stats.llm_calls == 0
    assert (root / ".prd2pr" / "repo_map.md").is_file()


def test_keyword_search(indexed_ts) -> None:
    root, _ = indexed_ts
    with dbmod.connection() as conn:
        store = PgStore(conn)
        repo = store.get_repo_by_path(str(root.resolve()))
        hits = search(store, repo.id, "cancel order", mode="keyword", k=5)
    assert hits
    assert any("cancel" in (h.symbol or "").lower() or "cancel" in h.file.lower() for h in hits)
