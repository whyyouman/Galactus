"""Step 1: walk folder → file list (filtered) + content hash."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pathspec

from prd2pr.config import Prd2prConfig

BUILTIN_IGNORES = [
    "node_modules/",
    "dist/",
    "build/",
    ".git/",
    ".venv/",
    "__pycache__/",
    "*.min.js",
    "*.lock",
    "package-lock.json",
    ".prd2pr/",
    ".env*",
    "*.pem",
    "*.key",
    "secrets.*",
]

EXT_LANGUAGE: dict[str, str] = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".py": "python",
}


@dataclass
class WalkedFile:
    path: str  # relative, / separators
    abs_path: Path
    language: str
    content_hash: str
    size_bytes: int


@dataclass
class WalkResult:
    files: list[WalkedFile]
    skipped: int


def _load_gitignore(root: Path) -> pathspec.PathSpec:
    patterns: list[str] = list(BUILTIN_IGNORES)
    gi = root / ".gitignore"
    if gi.is_file():
        patterns.extend(gi.read_text(encoding="utf-8", errors="replace").splitlines())
    return pathspec.PathSpec.from_lines("gitignore", patterns)


def _is_binary(data: bytes) -> bool:
    if b"\x00" in data[:8192]:
        return True
    return False


def walk_repo(root: Path, config: Prd2prConfig) -> WalkResult:
    root = root.resolve()
    gitignore = _load_gitignore(root)
    extra = pathspec.PathSpec.from_lines("gitignore", config.ignore) if config.ignore else None
    max_bytes = config.limits.max_file_kb * 1024

    allowed_langs = set(config.languages)
    # javascript maps to typescript adapter; treat both as allowed if either listed
    if "typescript" in allowed_langs:
        allowed_langs.add("javascript")
    if "javascript" in allowed_langs:
        allowed_langs.add("typescript")

    files: list[WalkedFile] = []
    skipped = 0

    for abs_path in root.rglob("*"):
        if not abs_path.is_file():
            continue
        rel = abs_path.relative_to(root).as_posix()
        if gitignore.match_file(rel) or (extra and extra.match_file(rel)):
            skipped += 1
            continue
        lang = EXT_LANGUAGE.get(abs_path.suffix.lower())
        if lang is None or lang not in allowed_langs:
            skipped += 1
            continue
        try:
            size = abs_path.stat().st_size
        except OSError:
            skipped += 1
            continue
        if size > max_bytes:
            skipped += 1
            continue
        try:
            data = abs_path.read_bytes()
        except OSError:
            skipped += 1
            continue
        if _is_binary(data):
            skipped += 1
            continue
        content_hash = hashlib.sha256(data).hexdigest()
        files.append(
            WalkedFile(
                path=rel,
                abs_path=abs_path,
                language=lang,
                content_hash=content_hash,
                size_bytes=size,
            )
        )

    files.sort(key=lambda f: f.path)
    return WalkResult(files=files, skipped=skipped)
