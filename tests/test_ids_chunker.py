"""Unit: identifier splitting, ID generation, chunk splitting."""

from __future__ import annotations

from prd2pr.config import LimitsConfig
from prd2pr.indexing.chunker import (
    chunk_symbols,
    collect_identifiers,
    split_identifier,
)
from prd2pr.indexing.ids import chunk_id, file_chunk_id, symbol_id
from prd2pr.indexing.languages.base import RawSymbol


def test_split_identifier() -> None:
    assert split_identifier("cancelOrderHandler") == "cancel order handler"
    assert split_identifier("get_user_id") == "get user id"
    assert split_identifier("HTTPResponse") == "http response"


def test_stable_ids() -> None:
    assert symbol_id("a.ts", "Foo.bar") == "a.ts::Foo.bar"
    assert symbol_id("a.ts", "Foo.bar", 12) == "a.ts::Foo.bar@12"
    assert chunk_id("a.ts::Foo", 0) == "a.ts::Foo#0"
    assert file_chunk_id("a.ts") == "a.ts::__file__#0"


def test_collect_identifiers_includes_split_and_path() -> None:
    ids = collect_identifiers(
        "cancelOrder",
        "OrderService.cancelOrder",
        "src/orders/order.service.ts",
        "function cancelOrder() { return 1 }",
    )
    assert "cancelOrder" in ids
    assert "cancel order" in ids
    assert "order" in ids or "orders" in ids


def test_small_symbols_merge_to_file_chunk() -> None:
    syms = [
        RawSymbol(
            name="a",
            qualified_name="a",
            kind="function",
            start_line=1,
            end_line=2,
            start_byte=0,
            end_byte=10,
            signature="function a()",
        )
    ]
    source = "function a() {\n  return 1;\n}\n"
    chunks = chunk_symbols("f.ts", source, syms, [], LimitsConfig(min_chunk_lines=4))
    assert any("__file__" in c.id for c in chunks)


def test_large_symbol_splits() -> None:
    body_lines = ["  x = 1;"] * 200
    code = "function big() {\n" + "\n".join(body_lines) + "\n}\n"
    syms = [
        RawSymbol(
            name="big",
            qualified_name="big",
            kind="function",
            start_line=1,
            end_line=202,
            start_byte=0,
            end_byte=len(code),
            signature="function big()",
        )
    ]
    chunks = chunk_symbols(
        "f.ts", code, syms, [], LimitsConfig(min_chunk_lines=4, max_chunk_lines=50)
    )
    parts = [c for c in chunks if c.symbol_id and c.symbol_id.endswith("big")]
    assert len(parts) > 1
