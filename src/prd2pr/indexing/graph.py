"""Step 5c: resolve imports/calls → edges in PostgreSQL."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from prd2pr.indexing.languages.base import ExtractResult


@dataclass
class GraphContext:
    """Per-repo resolution context built once per index run."""

    repo_root: Path
    # path -> list of symbol dicts
    symbols_by_file: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    # qualified_name / name -> list of symbol ids
    symbols_by_name: dict[str, list[str]] = field(default_factory=dict)
    # file path set
    files: set[str] = field(default_factory=set)
    # tsconfig paths aliases: "@/*" -> "src/*"
    path_aliases: list[tuple[str, str]] = field(default_factory=list)


def load_tsconfig_paths(repo_root: Path) -> list[tuple[str, str]]:
    aliases: list[tuple[str, str]] = []
    for name in ("tsconfig.json", "tsconfig.app.json", "jsconfig.json"):
        path = repo_root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
            # Strip // comments roughly
            text = re.sub(r"//.*?$", "", text, flags=re.M)
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
            data = json.loads(text)
        except (OSError, json.JSONDecodeError):
            continue
        paths = (
            data.get("compilerOptions", {}).get("paths")
            or data.get("paths")
            or {}
        )
        for pattern, targets in paths.items():
            if not targets:
                continue
            aliases.append((pattern, targets[0]))
    return aliases


def build_context(
    repo_root: Path,
    symbols: list[dict[str, Any]],
    file_paths: list[str],
) -> GraphContext:
    ctx = GraphContext(repo_root=repo_root, files=set(file_paths))
    ctx.path_aliases = load_tsconfig_paths(repo_root)
    for s in symbols:
        ctx.symbols_by_file.setdefault(s["file"], []).append(s)
        ctx.symbols_by_name.setdefault(s["name"], []).append(s["id"])
        ctx.symbols_by_name.setdefault(s["qualified_name"], []).append(s["id"])
    return ctx


def _resolve_ts_path(module: str, from_file: str, ctx: GraphContext) -> str | None:
    """Resolve a relative / alias import to a repo-relative file path."""
    candidates: list[str] = []

    def add_with_ext(base: str) -> None:
        for ext in ("", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
            candidates.append(base + ext)
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            candidates.append(f"{base}/index{ext}")

    if module.startswith("."):
        from_dir = str(Path(from_file).parent).replace("\\", "/")
        if from_dir == ".":
            from_dir = ""
        joined = str(Path(from_dir) / module).replace("\\", "/")
        # normalize ..
        parts: list[str] = []
        for p in joined.split("/"):
            if p == "..":
                if parts:
                    parts.pop()
            elif p in ("", "."):
                continue
            else:
                parts.append(p)
        base = "/".join(parts)
        add_with_ext(base)
    else:
        # alias @/x → src/x
        resolved_alias = False
        for pattern, target in ctx.path_aliases:
            # pattern like "@/*" or "@app/*"
            if pattern.endswith("/*"):
                prefix = pattern[:-1]  # "@/"
                if module.startswith(prefix[:-1]) or module.startswith(prefix):
                    # "@foo" with "@/*" 
                    star = pattern[:-2]  # "@"
                    if module.startswith(star + "/"):
                        rest = module[len(star) + 1 :]
                        tgt_prefix = target[:-1] if target.endswith("*") else target
                        base = tgt_prefix + rest if target.endswith("*") else f"{target}/{rest}"
                        add_with_ext(base.lstrip("./"))
                        resolved_alias = True
                        break
            elif module == pattern.rstrip("*").rstrip("/"):
                add_with_ext(target.rstrip("*"))
                resolved_alias = True
                break
        if not resolved_alias:
            return None  # external package

    for c in candidates:
        c = c.lstrip("./")
        if c in ctx.files:
            return c
    return None


def _resolve_py_module(module: str, from_file: str, ctx: GraphContext) -> str | None:
    if module.startswith("."):
        dots = len(module) - len(module.lstrip("."))
        rest = module.lstrip(".")
        parts = list(Path(from_file).parts[:-1])
        for _ in range(dots - 1):
            if parts:
                parts.pop()
        if rest:
            parts.extend(rest.split("."))
        base = "/".join(parts)
    else:
        # absolute within repo: orders.service → orders/service.py
        base = module.replace(".", "/")

    for cand in (f"{base}.py", f"{base}/__init__.py"):
        if cand in ctx.files:
            return cand
    return None


def resolve_import_target(
    module: str, from_file: str, language: str, ctx: GraphContext
) -> tuple[str, bool]:
    """Return (dst_id, resolved)."""
    if language in ("typescript", "javascript"):
        path = _resolve_ts_path(module, from_file, ctx)
    else:
        path = _resolve_py_module(module, from_file, ctx)
    if path:
        return path, True
    # External
    pkg = module.lstrip(".").split("/")[0].split(".")[0]
    if not module.startswith("."):
        return f"external:{pkg}", True
    return module, False


def _lookup_local(
    name: str, file: str, ctx: GraphContext
) -> str | None:
    for s in ctx.symbols_by_file.get(file, []):
        if s["name"] == name or s["qualified_name"] == name:
            return s["id"]
        # Class.method match on method name only within class later
    return None


def _lookup_imported(
    name: str,
    file: str,
    raw: ExtractResult,
    language: str,
    ctx: GraphContext,
) -> str | None:
    for imp in raw.imports:
        if name in imp.names or name == imp.module.split("/")[-1].split(".")[0]:
            dst, ok = resolve_import_target(imp.module, file, language, ctx)
            if ok and not dst.startswith("external:"):
                # Prefer symbol with same name in target file
                hit = _lookup_local(name, dst, ctx)
                if hit:
                    return hit
                return dst
            if ok:
                return dst
    # Global name lookup
    ids = ctx.symbols_by_name.get(name)
    if ids:
        return ids[0]
    return None


def _constructor_param_types(file: str, class_name: str, source_hint: str | None) -> dict[str, str]:
    """Best-effort NestJS DI: constructor(private readonly x: FooService)."""
    mapping: dict[str, str] = {}
    if not source_hint:
        return mapping
    # Find constructor in class
    m = re.search(
        rf"class\s+{re.escape(class_name)}\b[\s\S]*?constructor\s*\(([\s\S]*?)\)",
        source_hint,
    )
    if not m:
        return mapping
    params = m.group(1)
    for part in params.split(","):
        part = part.strip()
        if not part:
            continue
        # private readonly orders: OrderService
        pm = re.search(r"(?:private|public|protected|readonly\s+)*\s*(\w+)\s*:\s*(\w+)", part)
        if pm:
            mapping[pm.group(1)] = pm.group(2)
    return mapping


def build_edges_for_file(
    file: str,
    language: str,
    raw: ExtractResult,
    ctx: GraphContext,
    source_text: str | None = None,
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []

    # defines: file → symbol
    for s in ctx.symbols_by_file.get(file, []):
        edges.append(
            {
                "src": file,
                "dst": s["id"],
                "type": "defines",
                "src_file": file,
                "resolved": True,
            }
        )

    # imports: file → file / external
    for imp in raw.imports:
        dst, ok = resolve_import_target(imp.module, file, language, ctx)
        edges.append(
            {
                "src": file,
                "dst": dst,
                "type": "imports",
                "src_file": file,
                "resolved": ok,
            }
        )

    # extends
    for ext in raw.extends:
        child_id = _lookup_local(ext.child, file, ctx) or f"{file}::{ext.child}"
        parent_id = _lookup_local(ext.parent, file, ctx)
        resolved = parent_id is not None
        if not parent_id:
            parent_id = _lookup_imported(ext.parent, file, raw, language, ctx)
            resolved = parent_id is not None and not str(parent_id).startswith("external:")
            if parent_id is None:
                parent_id = ext.parent
                resolved = False
        edges.append(
            {
                "src": child_id,
                "dst": parent_id,
                "type": "extends",
                "src_file": file,
                "resolved": resolved,
            }
        )

    # calls
    di_maps: dict[str, dict[str, str]] = {}
    for call in raw.calls:
        enclosing = call.enclosing_symbol
        src = None
        if enclosing:
            src = _lookup_local(enclosing.split(".")[-1], file, ctx)
            # Prefer qualified
            for s in ctx.symbols_by_file.get(file, []):
                if s["qualified_name"] == enclosing or s["name"] == enclosing:
                    src = s["id"]
                    break
        if not src:
            src = f"{file}::{enclosing}" if enclosing else file

        callee = call.callee
        dst: str | None = None
        resolved = False

        # this.x.bar() NestJS DI
        m = re.match(r"this\.(\w+)\.(\w+)$", callee)
        if m and enclosing:
            class_name = enclosing.split(".")[0]
            if class_name not in di_maps:
                di_maps[class_name] = _constructor_param_types(
                    file, class_name, source_text
                )
            type_name = di_maps[class_name].get(m.group(1))
            method = m.group(2)
            if type_name:
                # find Type.method
                for sid in ctx.symbols_by_name.get(f"{type_name}.{method}", []):
                    dst = sid
                    resolved = True
                    break
                if not dst:
                    for sid in ctx.symbols_by_name.get(method, []):
                        if type_name in sid:
                            dst = sid
                            resolved = True
                            break
                    if not dst:
                        dst = f"{type_name}.{method}"
                        resolved = False

        if dst is None:
            # Foo.bar or bar
            simple = callee.split(".")[-1]
            dst = _lookup_local(callee, file, ctx) or _lookup_local(simple, file, ctx)
            if dst:
                resolved = True
            else:
                dst = _lookup_imported(simple, file, raw, language, ctx)
                if dst:
                    # external:* counts as resolved
                    resolved = True
                else:
                    # Local/unknown receivers (res.json, console.log) → external
                    parts = callee.split(".")
                    if (
                        len(parts) >= 2
                        and parts[0] != "this"
                        and parts[0][:1].islower()
                    ):
                        dst = f"external:{parts[0]}"
                        resolved = True
                    else:
                        dst = callee
                        resolved = False

        edges.append(
            {
                "src": src,
                "dst": dst,
                "type": "calls",
                "src_file": file,
                "resolved": resolved,
            }
        )

    # handles_route: route symbol → handler (same symbol for Nest/FastAPI methods;
    # for express, try to link last callback identifier)
    for s in ctx.symbols_by_file.get(file, []):
        if s["kind"] != "route":
            continue
        # Self edge for decorated handler methods
        if "." in s["qualified_name"] and not s["name"].startswith(
            ("GET ", "POST ", "PUT ", "PATCH ", "DELETE ", "OPTIONS ", "HEAD ", "ALL ")
        ):
            edges.append(
                {
                    "src": s["id"],
                    "dst": s["id"],
                    "type": "handles_route",
                    "src_file": file,
                    "resolved": True,
                }
            )
            continue
        # Express-style: look for handler name in signature
        sig = s.get("signature") or ""
        handlers = re.findall(r"[,\(]\s*([A-Za-z_][A-Za-z0-9_]*)\s*[,)]", sig)
        # Also match trailing handler before )
        m = re.search(r"[,\s]([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*$", sig)
        if m:
            handlers.append(m.group(1))
        linked = False
        for h in handlers:
            if h.lower() in _ROUTE_METHODS_SET:
                continue
            hit = _lookup_local(h, file, ctx) or _lookup_imported(
                h, file, raw, language, ctx
            )
            if hit:
                edges.append(
                    {
                        "src": s["id"],
                        "dst": hit,
                        "type": "handles_route",
                        "src_file": file,
                        "resolved": True,
                    }
                )
                linked = True
                break
        if not linked:
            # Unresolved handler name kept as raw
            edges.append(
                {
                    "src": s["id"],
                    "dst": s["name"],
                    "type": "handles_route",
                    "src_file": file,
                    "resolved": False,
                }
            )

    # uses_config
    for ref in raw.config_refs:
        src = file
        if ref.enclosing_symbol:
            for s in ctx.symbols_by_file.get(file, []):
                if s["qualified_name"] == ref.enclosing_symbol or s["name"] == ref.enclosing_symbol:
                    src = s["id"]
                    break
        edges.append(
            {
                "src": src,
                "dst": f"config:{ref.key}",
                "type": "uses_config",
                "src_file": file,
                "resolved": True,
            }
        )

    # Deduplicate by (src, dst, type)
    uniq: dict[tuple[str, str, str], dict[str, Any]] = {}
    for e in edges:
        uniq[(e["src"], e["dst"], e["type"])] = e
    return list(uniq.values())


_ROUTE_METHODS_SET = {"get", "post", "put", "patch", "delete", "options", "head", "all"}
