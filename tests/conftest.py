"""Pytest fixtures — throwaway Postgres DB per test session."""

from __future__ import annotations

import os
import uuid
from collections.abc import Generator, Iterator
from pathlib import Path

import pytest
from psycopg import connect

from prd2pr.storage import db as dbmod
from prd2pr.storage.migrate import migrate

FIXTURES = Path(__file__).parent / "fixtures"


def _admin_url() -> str:
    url = os.environ.get("PRD2PR_TEST_DATABASE_URL")
    if not url:
        # Fall back to local docker-compose defaults
        url = "postgresql://prd2pr:prd2pr@localhost:5432/prd2pr"
    return url


@pytest.fixture(scope="session")
def test_database_url() -> Generator[str, None, None]:
    admin = _admin_url()
    db_name = f"prd2pr_test_{uuid.uuid4().hex[:8]}"
    # Connect to maintenance DB to create/drop
    # Strip path and use /postgres
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(admin)
    maint = urlunparse(parsed._replace(path="/postgres"))
    with connect(maint, autocommit=True) as conn:
        conn.execute(f'CREATE DATABASE "{db_name}"')
    test_url = urlunparse(parsed._replace(path=f"/{db_name}"))
    os.environ["PRD2PR_DATABASE_URL"] = test_url
    os.environ["PRD2PR_TEST_DATABASE_URL"] = test_url
    try:
        yield test_url
    finally:
        dbmod.close_pool()
        with connect(maint, autocommit=True) as conn:
            conn.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (db_name,),
            )
            conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')


@pytest.fixture(scope="session")
def migrated_db(test_database_url: str) -> str:
    dbmod.close_pool()
    migrate(url_env="PRD2PR_DATABASE_URL")
    return test_database_url


@pytest.fixture
def db_conn(migrated_db: str) -> Iterator:
    dbmod.close_pool()
    dbmod.init_pool(url_env="PRD2PR_DATABASE_URL")
    with dbmod.connection() as conn:
        yield conn
        conn.rollback()


@pytest.fixture
def ts_fixture() -> Path:
    return FIXTURES / "ts_sample"


@pytest.fixture
def py_fixture() -> Path:
    return FIXTURES / "py_sample"


@pytest.fixture
def fake_llm(monkeypatch: pytest.MonkeyPatch):
    """Deterministic fake embeddings + summaries (no network)."""
    import prd2pr.llm.client as client_mod

    class FakeLlm:
        def __init__(self, *args, **kwargs) -> None:
            self.summary_model = kwargs.get("summary_model", "fake")
            self.embedding_model = kwargs.get("embedding_model", "fake")
            self.embedding_dim = kwargs.get("embedding_dim", 8)
            self.concurrency = kwargs.get("concurrency", 8)
            self.total_tokens = 0
            self.total_cost = 0.0
            self.call_count = 0
            self.summary_calls = 0

        async def summarize(self, header: str, code: str) -> str:
            self.call_count += 1
            self.summary_calls += 1
            self.total_tokens += 10
            return f"Summary of {header.splitlines()[0] if header else 'code'}."

        async def embed(self, texts):
            self.call_count += 1
            self.total_tokens += len(texts)
            out = []
            for t in texts:
                # deterministic tiny vector from hash
                h = abs(hash(t)) % (10**8)
                vec = [((h >> i) & 255) / 255.0 for i in range(self.embedding_dim)]
                out.append(vec)
            return out

        async def summarize_many(self, items):
            results = {}
            for cid, h, c in items:
                results[cid] = await self.summarize(h, c)
            return results

        async def embed_many(self, texts, batch_size: int = 32):
            out = []
            for i in range(0, len(texts), batch_size):
                out.extend(await self.embed(texts[i : i + batch_size]))
            return out

    monkeypatch.setattr(client_mod, "LlmClient", FakeLlm)
    # Pipeline imports LlmClient into its own namespace
    import prd2pr.indexing.embedder as embedder_mod
    import prd2pr.indexing.pipeline as pipeline_mod
    import prd2pr.indexing.summarizer as summarizer_mod
    import prd2pr.search.retriever as retriever_mod

    monkeypatch.setattr(pipeline_mod, "LlmClient", FakeLlm)
    monkeypatch.setattr(summarizer_mod, "LlmClient", FakeLlm)
    monkeypatch.setattr(embedder_mod, "LlmClient", FakeLlm)
    monkeypatch.setattr(retriever_mod, "LlmClient", FakeLlm)
    return FakeLlm
