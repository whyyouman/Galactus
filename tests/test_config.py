"""M1: config validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from prd2pr.config import Prd2prConfig, load_config, write_default_config


def test_default_config_valid() -> None:
    cfg = Prd2prConfig()
    assert cfg.version == 1
    assert "typescript" in cfg.languages
    assert cfg.limits.max_file_kb == 500


def test_rejects_unknown_language() -> None:
    with pytest.raises(ValidationError):
        Prd2prConfig(languages=["go"])


def test_write_and_load_roundtrip(tmp_path: Path) -> None:
    write_default_config(tmp_path)
    cfg = load_config(tmp_path)
    assert cfg.llm.embedding_dim == 1536
    assert cfg.database.url_env == "PRD2PR_DATABASE_URL"
