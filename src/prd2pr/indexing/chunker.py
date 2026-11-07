"""Chunk text + context header."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from prd2pr.config import LimitsConfig
from prd2pr.indexing.ids import chunk_id, file_chunk_id
from prd2pr.indexing.languages.base import RawImport, RawSymbol


@dataclass
class ChunkDraft:
    id: str
    symbol_id: str | None
    file: str
    start_line: int
    end_line: int
    header: str
    code: str
    content_hash: str
    kind: str


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_header(
    file: str,
    symbol: RawSymbol | None,
    import_names: list[str],
) -> str:
    lines = [f"File: {file}"]
    if symbol and symbol.parent_name:
        lines.append(f"Class: {symbol.parent_name}")
    if symbol:
        lines.append(f"Symbol: {symbol.signature or symbol.qualified_name}")
    if import_names:
        lines.append(f"Imports: {', '.join(import_names[:20])}")
    return "\n".join(lines)


def _split_on_statements(code: str, max_lines: int) -> list[tuple[int, int, str]]:
    """Split code into parts of at most max_lines, on blank-line / statement boundaries.

    Returns list of (start_offset_lines, end_offset_lines, text) 0-based offsets within code.
    """
    lines = code.splitlines(keepends=True)
    if len(lines) <= max_lines:
        return [(0, len(lines), code)]
    parts: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        end = min(i + max_lines, len(lines))
        # Prefer break on blank line near the end
        if end < len(lines):
            for j in range(end - 1, i + max_lines // 2, -1):
                if lines[j].strip() == "":
                    end = j + 1
                    break
        part = "".join(lines[i:end])
        parts.append((i, end, part))
        i = end
    return parts


def chunk_symbols(
    file: str,
    source_text: str,
    symbols: list[RawSymbol],
    imports: list[RawImport],
    limits: LimitsConfig,
) -> list[ChunkDraft]:
    import_names: list[str] = []
    for imp in imports:
        import_names.extend(imp.names or [imp.module])

    lines = source_text.splitlines(keepends=True)
    chunks: list[ChunkDraft] = []
    small: list[RawSymbol] = []

    def body_of(sym: RawSymbol) -> str:
        # Convert byte range via line numbers for simplicity
        start_idx = max(0, sym.start_line - 1)
        end_idx = min(len(lines), sym.end_line)
        return "".join(lines[start_idx:end_idx])

    for sym in symbols:
        nlines = sym.end_line - sym.start_line + 1
        if nlines < limits.min_chunk_lines:
            small.append(sym)
            continue
        code = body_of(sym)
        header = build_header(file, sym, import_names)
        # Symbol id without @line for primary; overloads handled upstream
        sid = f"{file}::{sym.qualified_name}"
        if nlines > limits.max_chunk_lines:
            for part_i, (off0, off1, part_code) in enumerate(
                _split_on_statements(code, limits.max_chunk_lines)
            ):
                cid = chunk_id(sid, part_i)
                start_line = sym.start_line + off0
                end_line = sym.start_line + off1 - 1
                chunks.append(
                    ChunkDraft(
                        id=cid,
                        symbol_id=sid,
                        file=file,
                        start_line=start_line,
                        end_line=end_line,
                        header=header,
                        code=part_code,
                        content_hash=_sha(part_code),
                        kind=sym.kind,
                    )
                )
        else:
            chunks.append(
                ChunkDraft(
                    id=chunk_id(sid, 0),
                    symbol_id=sid,
                    file=file,
                    start_line=sym.start_line,
                    end_line=sym.end_line,
                    header=header,
                    code=code,
                    content_hash=_sha(code),
                    kind=sym.kind,
                )
            )

    if small or not symbols:
        # File-level chunk for tiny symbols / empty
        if small:
            start = min(s.start_line for s in small)
            end = max(s.end_line for s in small)
            code = "".join(lines[start - 1 : end])
        else:
            # whole file truncated
            code = source_text[:8000]
            start, end = 1, min(len(lines), max(1, len(lines)))
        header = build_header(file, None, import_names)
        chunks.append(
            ChunkDraft(
                id=file_chunk_id(file, 0),
                symbol_id=None,
                file=file,
                start_line=start,
                end_line=end,
                header=header,
                code=code,
                content_hash=_sha(code),
                kind="file",
            )
        )

    return chunks


_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def split_identifier(name: str) -> str:
    """cancelOrderHandler → cancel order handler; get_user_id → get user id."""
    # snake_case
    parts = name.split("_")
    out: list[str] = []
    for p in parts:
        # camelCase / PascalCase
        pieces = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+", p)
        if pieces:
            out.extend(x.lower() for x in pieces)
        elif p:
            out.append(p.lower())
    return " ".join(out)


def collect_identifiers(
    symbol_name: str | None,
    qualified_name: str | None,
    file: str,
    code: str,
) -> str:
    tokens: list[str] = []
    if symbol_name:
        tokens.append(symbol_name)
        tokens.append(split_identifier(symbol_name))
    if qualified_name:
        tokens.append(qualified_name)
        for part in qualified_name.replace("::", ".").split("."):
            tokens.append(part)
            tokens.append(split_identifier(part))
    for seg in file.replace("\\", "/").split("/"):
        stem = seg.rsplit(".", 1)[0]
        tokens.append(stem)
        tokens.append(split_identifier(stem))
    for m in _IDENT_RE.findall(code):
        if len(m) >= 2:
            tokens.append(m)
            split = split_identifier(m)
            if split != m.lower():
                tokens.append(split)
    # dedupe preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for t in tokens:
        if t and t not in seen:
            seen.add(t)
            ordered.append(t)
    return " ".join(ordered)
