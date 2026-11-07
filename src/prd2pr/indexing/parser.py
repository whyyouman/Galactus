"""Step 3: tree-sitter setup per language."""

from __future__ import annotations

from dataclasses import dataclass

from tree_sitter import Language, Parser, Tree
from tree_sitter_language_pack import get_language


@dataclass
class ParseResult:
    tree: Tree
    source: bytes
    language: str


_PARSERS: dict[str, Parser] = {}


def _ts_lang_name(language: str) -> str:
    if language in ("typescript", "javascript"):
        # Prefer typescript grammar for both TS and JS/JSX/TSX
        return "typescript"
    if language == "python":
        return "python"
    raise ValueError(f"unsupported language: {language}")


def get_parser(language: str) -> Parser:
    key = _ts_lang_name(language)
    if key not in _PARSERS:
        lang: Language = get_language(key)  # type: ignore[assignment]
        parser = Parser(lang)
        _PARSERS[key] = parser
    return _PARSERS[key]


def parse_file(source: bytes, language: str) -> ParseResult:
    parser = get_parser(language)
    tree = parser.parse(source)
    return ParseResult(tree=tree, source=source, language=language)
