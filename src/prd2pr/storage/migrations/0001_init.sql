CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE repos (
    id BIGSERIAL PRIMARY KEY,
    root_path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    last_indexed_commit TEXT,
    embed_model TEXT,
    embed_dim INTEGER,
    last_run_stats JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE files (
    repo_id BIGINT NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    language TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    size_bytes INTEGER,
    parse_errors INTEGER NOT NULL DEFAULT 0,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (repo_id, path)
);

CREATE TABLE symbols (
    repo_id BIGINT NOT NULL,
    id TEXT NOT NULL,
    file TEXT NOT NULL,
    name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('class','function','method','route','model')),
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    signature TEXT,
    docstring TEXT,
    parent_id TEXT,
    rank DOUBLE PRECISION NOT NULL DEFAULT 0,
    PRIMARY KEY (repo_id, id),
    FOREIGN KEY (repo_id, file) REFERENCES files(repo_id, path) ON DELETE CASCADE
);

CREATE TABLE chunks (
    repo_id BIGINT NOT NULL,
    id TEXT NOT NULL,
    symbol_id TEXT,
    file TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    header TEXT NOT NULL,
    code TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    summary TEXT,
    summary_hash TEXT,
    embedded_hash TEXT,
    identifiers TEXT NOT NULL DEFAULT '',
    search_tsv TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('simple', identifiers), 'A') ||
        setweight(to_tsvector('simple', coalesce(summary, '')), 'B')
    ) STORED,
    PRIMARY KEY (repo_id, id),
    FOREIGN KEY (repo_id, file) REFERENCES files(repo_id, path) ON DELETE CASCADE
);

CREATE TABLE edges (
    repo_id BIGINT NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN (
        'imports','calls','extends','handles_route','defines','uses_config'
    )),
    src_file TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (repo_id, src, dst, type)
);

CREATE INDEX idx_symbols_file ON symbols (repo_id, file);
CREATE INDEX idx_symbols_name ON symbols (repo_id, name);
CREATE INDEX idx_chunks_file ON chunks (repo_id, file);
CREATE INDEX idx_chunks_search ON chunks USING GIN (search_tsv);
CREATE INDEX idx_edges_dst ON edges (repo_id, dst);
CREATE INDEX idx_edges_srcfile ON edges (repo_id, src_file);
