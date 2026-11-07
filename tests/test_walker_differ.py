"""M2: ignore rules, hashing, new/changed/deleted detection."""

from __future__ import annotations

from pathlib import Path

from prd2pr.config import Prd2prConfig
from prd2pr.indexing.differ import diff_files
from prd2pr.indexing.walker import WalkedFile, walk_repo


def test_ignore_node_modules_and_venv(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.ts").write_text("export const a = 1;\n")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.js").write_text("module.exports = 1;\n")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "x.py").write_text("x = 1\n")
    (tmp_path / ".env").write_text("SECRET=1\n")
    (tmp_path / "src" / "secret.pem").write_text("-----BEGIN-----\n")

    result = walk_repo(tmp_path, Prd2prConfig())
    paths = [f.path for f in result.files]
    assert paths == ["src/a.ts"]
    assert result.skipped >= 3


def test_extra_ignore_from_config(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.ts").write_text("export const a = 1;\n")
    (tmp_path / "src" / "b.generated.ts").write_text("export const b = 1;\n")
    cfg = Prd2prConfig(ignore=["**/*.generated.ts"])
    result = walk_repo(tmp_path, cfg)
    assert [f.path for f in result.files] == ["src/a.ts"]


def test_content_hash_stable(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print(1)\n")
    r1 = walk_repo(tmp_path, Prd2prConfig(languages=["python"]))
    r2 = walk_repo(tmp_path, Prd2prConfig(languages=["python"]))
    assert r1.files[0].content_hash == r2.files[0].content_hash
    assert len(r1.files[0].content_hash) == 64


def test_diff_new_changed_deleted() -> None:
    files = [
        WalkedFile("a.ts", Path("a.ts"), "typescript", "hash1", 10),
        WalkedFile("b.ts", Path("b.ts"), "typescript", "hash2b", 10),
    ]
    existing = {"b.ts": "hash2a", "c.ts": "hash3"}
    d = diff_files(files, existing)
    assert [f.path for f in d.new] == ["a.ts"]
    assert [f.path for f in d.changed] == ["b.ts"]
    assert d.deleted == ["c.ts"]
    assert d.unchanged == []


def test_diff_full_flags_all_changed() -> None:
    files = [WalkedFile("a.ts", Path("a.ts"), "typescript", "h", 1)]
    d = diff_files(files, {"a.ts": "h"}, full=True)
    assert len(d.changed) == 1
    assert not d.unchanged
