"""M5: import path resolution including aliases."""

from __future__ import annotations

from pathlib import Path

from prd2pr.indexing.graph import (
    GraphContext,
    load_tsconfig_paths,
    resolve_import_target,
)


def test_tsconfig_alias_and_relative(ts_fixture: Path) -> None:
    aliases = load_tsconfig_paths(ts_fixture)
    assert any(a[0].startswith("@/") for a in aliases)

    files = {
        p.relative_to(ts_fixture).as_posix()
        for p in ts_fixture.rglob("*.ts")
    }
    ctx = GraphContext(repo_root=ts_fixture, files=files, path_aliases=aliases)

    dst, ok = resolve_import_target("./order.model", "src/orders/order.repo.ts", "typescript", ctx)
    assert ok
    assert dst == "src/orders/order.model.ts"

    dst, ok = resolve_import_target("@/orders/order.service", "src/orders/handlers.ts", "typescript", ctx)
    assert ok
    assert dst == "src/orders/order.service.ts"

    dst, ok = resolve_import_target("express", "src/orders/orders.router.ts", "typescript", ctx)
    assert ok
    assert dst == "external:express"


def test_index_barrel_resolution(ts_fixture: Path) -> None:
    files = {
        p.relative_to(ts_fixture).as_posix()
        for p in ts_fixture.rglob("*.ts")
    }
    ctx = GraphContext(
        repo_root=ts_fixture,
        files=files,
        path_aliases=load_tsconfig_paths(ts_fixture),
    )
    dst, ok = resolve_import_target("./orders", "src/app.ts", "typescript", ctx)
    # ./orders → src/orders/index.ts
    assert ok
    assert dst == "src/orders/index.ts"
