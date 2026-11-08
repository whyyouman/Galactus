# Galactus

Open-source **PRD-to-PR** tooling. This repository currently ships **Phase 1: the indexing engine**.

Given a path to a local TypeScript/JavaScript or Python repo, `prd2pr index` parses every source file once, extracts symbols, chunks and relationships, and stores them in:

- **PostgreSQL** — repos, files, symbols, chunks, edges + full-text keyword search
- **Qdrant (local)** — code and summary embeddings under `.prd2pr/qdrant/`

Later phases (PRD parsing, planning, code generation) query this index instead of reading the whole tree.

## Quickstart

```bash
# 1. Start Postgres + Galatus web UI
docker compose up -d --build
# UI → http://localhost:3000
# DB → localhost:5433

# 2. Install (Python 3.12+)
uv sync --all-extras

# 3. Point at the database
export PRD2PR_DATABASE_URL=postgresql://prd2pr:prd2pr@localhost:5433/prd2pr

# 4. Migrate, init, index (no API key needed)
uv run prd2pr db migrate
cd /path/to/your/repo
uv run prd2pr init
uv run prd2pr index --no-embed --no-summaries
uv run prd2pr status
uv run prd2pr search "cancel order" --mode keyword
```

With an LLM/embedding provider configured (e.g. `OPENAI_API_KEY`), omit `--no-embed` / `--no-summaries` to build semantic indexes. Any [LiteLLM](https://docs.litellm.ai/) model id works, including local `ollama/<model>`.

## CLI

| Command | Purpose |
|---------|---------|
| `prd2pr db migrate` | Create/upgrade schema |
| `prd2pr init [--repo PATH]` | Write `prd2pr.yaml`, register repo |
| `prd2pr index [--full] [--no-embed] [--no-summaries]` | Build / refresh indexes |
| `prd2pr status` | Counts, last commit, stale files |
| `prd2pr search "q" [--mode keyword\|semantic\|graph\|hybrid]` | Debug retrieval |

## Development

```bash
docker compose up -d --build
export PRD2PR_DATABASE_URL=postgresql://prd2pr:prd2pr@localhost:5433/prd2pr
export PRD2PR_TEST_DATABASE_URL=$PRD2PR_DATABASE_URL
uv sync --all-extras
uv run pytest
```

## Manual scale check

After indexing a real open-source repo (≥500 files) with `--no-embed --no-summaries`, record wall time and `prd2pr status` counts here:

| Repo | Files | Symbols | Chunks | Edges | Time |
|------|------:|--------:|-------:|------:|-----:|
| `tests/fixtures/ts_sample` (`--no-embed --no-summaries`) | 9 | 15 | 13 | 34 | ~0.05s |
| _(≥500-file open-source repo — fill in)_ | | | | | |

## Web UI (Next.js)

Static Galatus HTML ([`galatus-html/`](galatus-html/)) lives as a Next.js app under [`web/`](web/).

**With Docker** (recommended):

```bash
docker compose up -d --build
# → http://localhost:3000
```

**Local dev** (hot reload):

```bash
cd web && npm install && npm run dev
```

See [web/README.md](web/README.md) for routes.

## License

MIT — see [LICENSE](LICENSE).
