"""M3: TypeScript fixture symbols match expected.json."""

from __future__ import annotations

import json
from pathlib import Path

from prd2pr.config import LimitsConfig
from prd2pr.indexing.extractor import extract_file
from prd2pr.indexing.parser import parse_file


def _index_fixture(root: Path) -> list[dict]:
    symbols: list[dict] = []
    for path in sorted(root.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        if "node_modules" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        source = path.read_bytes()
        parsed = parse_file(source, "typescript")
        ext = extract_file(rel, parsed, LimitsConfig())
        symbols.extend(ext.symbols)
    return symbols


def test_ts_symbols_match_expected(ts_fixture: Path) -> None:
    expected = json.loads((ts_fixture / "expected.json").read_text())
    symbols = _index_fixture(ts_fixture)

    for exp in expected["symbols"]:
        matches = [
            s
            for s in symbols
            if s["file"] == exp["file"]
            and (
                (
                    "qualified_name" in exp
                    and s["qualified_name"] == exp["qualified_name"]
                )
                or (
                    "name_contains" in exp
                    and exp["name_contains"] in (s["name"] + s["qualified_name"])
                )
            )
            and s["kind"] == exp["kind"]
        ]
        assert matches, f"missing symbol {exp}; have {[s['qualified_name'] for s in symbols if s['file']==exp['file']]}"


def test_syntax_error_file_still_parses(ts_fixture: Path) -> None:
    path = ts_fixture / "src" / "broken.ts"
    parsed = parse_file(path.read_bytes(), "typescript")
    ext = extract_file("src/broken.ts", parsed, LimitsConfig())
    assert ext.parse_errors >= 1
