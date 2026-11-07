"""LanguageAdapter interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from tree_sitter import Node, Tree


@dataclass
class RawSymbol:
    name: str
    qualified_name: str
    kind: str  # class|function|method|route|model
    start_line: int  # 1-based
    end_line: int
    start_byte: int
    end_byte: int
    signature: str
    docstring: str | None = None
    parent_name: str | None = None
    # For routes: HTTP method + path
    route_method: str | None = None
    route_path: str | None = None


@dataclass
class RawImport:
    module: str  # e.g. "./orders" or "express" or "os"
    names: list[str] = field(default_factory=list)  # imported bindings
    is_relative: bool = False
    start_line: int = 1


@dataclass
class RawCall:
    callee: str  # e.g. "bar", "Foo.bar", "this.x.bar"
    start_line: int
    enclosing_symbol: str | None = None


@dataclass
class RawConfigRef:
    key: str
    start_line: int
    enclosing_symbol: str | None = None


@dataclass
class RawExtends:
    child: str
    parent: str
    start_line: int


@dataclass
class ExtractResult:
    symbols: list[RawSymbol] = field(default_factory=list)
    imports: list[RawImport] = field(default_factory=list)
    calls: list[RawCall] = field(default_factory=list)
    config_refs: list[RawConfigRef] = field(default_factory=list)
    extends: list[RawExtends] = field(default_factory=list)
    parse_errors: int = 0


class LanguageAdapter(Protocol):
    language_name: str

    def extract(self, tree: Tree, source: bytes, file_path: str) -> ExtractResult: ...


def node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def line_of(node: Node) -> tuple[int, int]:
    """1-based start/end lines."""
    return node.start_point[0] + 1, node.end_point[0] + 1
