"""Load and validate prd2pr.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

DEFAULT_CONFIG_NAME = "prd2pr.yaml"


class LimitsConfig(BaseModel):
    max_file_kb: int = 500
    min_chunk_lines: int = 4
    max_chunk_lines: int = 120
    min_summary_lines: int = 6


class DatabaseConfig(BaseModel):
    url_env: str = "PRD2PR_DATABASE_URL"
    pool_size: int = 5


class LlmConfig(BaseModel):
    summary_model: str = "openai/gpt-4o-mini"
    embedding_model: str = "openai/text-embedding-3-small"
    embedding_dim: int = 1536
    concurrency: int = 8


class Prd2prConfig(BaseModel):
    version: int = 1
    languages: list[str] = Field(default_factory=lambda: ["typescript", "python"])
    ignore: list[str] = Field(default_factory=list)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LlmConfig = Field(default_factory=LlmConfig)
    summaries: bool = True
    repo_map_tokens: int = 4000

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, v: list[str]) -> list[str]:
        allowed = {"typescript", "javascript", "python"}
        for lang in v:
            if lang not in allowed:
                raise ValueError(f"unsupported language: {lang!r}; allowed: {sorted(allowed)}")
        return v


def default_config_dict() -> dict[str, Any]:
    return Prd2prConfig().model_dump()


def write_default_config(path: Path) -> Path:
    """Write a default prd2pr.yaml and return its path."""
    config_path = path / DEFAULT_CONFIG_NAME if path.is_dir() else path
    data = default_config_dict()
    # Prefer a readable YAML layout matching the PRD example
    text = yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
    config_path.write_text(text, encoding="utf-8")
    return config_path


def load_config(repo_path: Path) -> Prd2prConfig:
    """Load prd2pr.yaml from repo root; raise if missing or invalid."""
    config_path = repo_path / DEFAULT_CONFIG_NAME
    if not config_path.is_file():
        raise FileNotFoundError(
            f"No {DEFAULT_CONFIG_NAME} in {repo_path}. Run `prd2pr init` first."
        )
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return Prd2prConfig.model_validate(raw)


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from start (or cwd) looking for prd2pr.yaml."""
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / DEFAULT_CONFIG_NAME).is_file():
            return candidate
    return cur
