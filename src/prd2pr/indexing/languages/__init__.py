"""Language adapters (tree-sitter query plugins)."""

from __future__ import annotations

from prd2pr.indexing.languages.base import LanguageAdapter
from prd2pr.indexing.languages.python import PythonAdapter
from prd2pr.indexing.languages.typescript import TypeScriptAdapter


def get_adapter(language: str) -> LanguageAdapter:
    if language in ("typescript", "javascript"):
        return TypeScriptAdapter()
    if language == "python":
        return PythonAdapter()
    raise ValueError(f"unsupported language: {language}")
