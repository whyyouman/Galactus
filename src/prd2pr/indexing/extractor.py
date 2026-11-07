"""Step 4: AST → symbols + chunks + raw imports/calls → records ready for PostgreSQL."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from prd2pr.config import LimitsConfig
from prd2pr.indexing.chunker import ChunkDraft, chunk_symbols, collect_identifiers
from prd2pr.indexing.ids import symbol_id
from prd2pr.indexing.languages import get_adapter
from prd2pr.indexing.languages.base import ExtractResult, RawSymbol
from prd2pr.indexing.parser import ParseResult


@dataclass
class FileExtraction:
    symbols: list[dict[str, Any]] = field(default_factory=list)
    chunks: list[dict[str, Any]] = field(default_factory=list)
    raw: ExtractResult = field(default_factory=ExtractResult)
    parse_errors: int = 0


def _dedupe_symbol_ids(symbols: list[RawSymbol], file: str) -> list[tuple[str, RawSymbol]]:
    """Assign stable IDs; append @start_line on duplicate qualified names."""
    seen: dict[str, int] = {}
    out: list[tuple[str, RawSymbol]] = []
    for sym in symbols:
        base = f"{file}::{sym.qualified_name}"
        if base in seen:
            sid = symbol_id(file, sym.qualified_name, sym.start_line)
        else:
            sid = base
            seen[base] = sym.start_line
        # Check collision of sid itself
        if any(existing == sid for existing, _ in out):
            sid = symbol_id(file, sym.qualified_name, sym.start_line)
        out.append((sid, sym))
    return out


def extract_file(
    file_path: str,
    parse: ParseResult,
    limits: LimitsConfig,
) -> FileExtraction:
    adapter = get_adapter(parse.language)
    raw = adapter.extract(parse.tree, parse.source, file_path)
    source_text = parse.source.decode("utf-8", errors="replace")

    # Prefer NestJS/FastAPI method routes over synthetic express route symbols
    # when both exist; keep all for graph.
    id_syms = _dedupe_symbol_ids(raw.symbols, file_path)
    symbols: list[dict[str, Any]] = []
    for sid, sym in id_syms:
        parent_id = None
        if sym.parent_name:
            parent_id = f"{file_path}::{sym.parent_name}"
        symbols.append(
            {
                "id": sid,
                "file": file_path,
                "name": sym.name,
                "qualified_name": sym.qualified_name,
                "kind": sym.kind,
                "start_line": sym.start_line,
                "end_line": sym.end_line,
                "signature": sym.signature,
                "docstring": sym.docstring,
                "parent_id": parent_id,
            }
        )

    drafts: list[ChunkDraft] = chunk_symbols(
        file_path, source_text, raw.symbols, raw.imports, limits
    )
    chunks: list[dict[str, Any]] = []
    for d in drafts:
        name = None
        qn = None
        if d.symbol_id and "::" in d.symbol_id:
            qn = d.symbol_id.split("::", 1)[1]
            name = qn.split(".")[-1]
        identifiers = collect_identifiers(name, qn, file_path, d.code)
        chunks.append(
            {
                "id": d.id,
                "symbol_id": d.symbol_id,
                "file": d.file,
                "start_line": d.start_line,
                "end_line": d.end_line,
                "header": d.header,
                "code": d.code,
                "content_hash": d.content_hash,
                "summary": None,
                "summary_hash": None,
                "embedded_hash": None,
                "identifiers": identifiers,
                "kind": d.kind,
            }
        )

    return FileExtraction(
        symbols=symbols,
        chunks=chunks,
        raw=raw,
        parse_errors=raw.parse_errors,
    )
