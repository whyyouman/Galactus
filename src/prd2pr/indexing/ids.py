"""Stable ID helpers shared across PostgreSQL, Qdrant and the graph."""

from __future__ import annotations


def symbol_id(file: str, qualified_name: str, start_line: int | None = None) -> str:
    """Stable symbol id; append @start_line on overload/duplicate."""
    base = f"{file}::{qualified_name}"
    if start_line is not None:
        return f"{base}@{start_line}"
    return base


def chunk_id(sym_id: str, part: int = 0) -> str:
    return f"{sym_id}#{part}"


def file_chunk_id(file: str, part: int = 0) -> str:
    return f"{file}::__file__#{part}"
