"""M4: Python fixture symbols match expected.json."""

from __future__ import annotations

import json
from pathlib import Path

from prd2pr.config import LimitsConfig
from prd2pr.indexing.extractor import extract_file
from prd2pr.indexing.parser import parse_file


def _index_fixture(root: Path) -> list[dict]:
    symbols: list[dict] = []
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        source = path.read_bytes()
        parsed = parse_file(source, "python")
        ext = extract_file(rel, parsed, LimitsConfig())
        symbols.extend(ext.symbols)
    return symbols


def test_py_symbols_match_expected(py_fixture: Path) -> None:
    expected = json.loads((py_fixture / "expected.json").read_text())
    symbols = _index_fixture(py_fixture)
    for exp in expected["symbols"]:
        matches = [
            s
            for s in symbols
            if s["file"] == exp["file"]
            and s["qualified_name"] == exp["qualified_name"]
            and s["kind"] == exp["kind"]
        ]
        assert matches, (
            f"missing {exp}; have "
            f"{[(s['qualified_name'], s['kind']) for s in symbols if s['file']==exp['file']]}"
        )
