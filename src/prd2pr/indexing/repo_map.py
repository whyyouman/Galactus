"""Step 6: PageRank over graph → .prd2pr/repo_map.md."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx

from prd2pr.storage.pg_store import PgStore


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _pagerank(
    g: nx.DiGraph, alpha: float = 0.85, max_iter: int = 100, tol: float = 1.0e-6
) -> dict[str, float]:
    """Power-iteration PageRank without requiring scipy."""
    nodes = list(g.nodes())
    n = len(nodes)
    if n == 0:
        return {}
    rank = {node: 1.0 / n for node in nodes}
    for _ in range(max_iter):
        new_rank = {node: (1.0 - alpha) / n for node in nodes}
        for u in nodes:
            outs = list(g.successors(u))
            if not outs:
                share = alpha * rank[u] / n
                for v in nodes:
                    new_rank[v] += share
            else:
                share = alpha * rank[u] / len(outs)
                for v in outs:
                    new_rank[v] += share
        err = sum(abs(new_rank[node] - rank[node]) for node in nodes)
        rank = new_rank
        if err < tol:
            break
    return rank


def build_repo_map(
    store: PgStore,
    repo_id: int,
    repo_root: Path,
    token_budget: int = 4000,
) -> Path:
    symbols = store.list_symbols(repo_id)
    edges = store.list_edges(repo_id)
    files = store.list_files(repo_id)

    g: nx.DiGraph = nx.DiGraph()
    for s in symbols:
        g.add_node(s["id"])
    for e in edges:
        if e.get("resolved") and e["type"] in ("calls", "imports", "extends", "defines"):
            g.add_edge(e["src"], e["dst"])

    ranks: dict[str, float] = {}
    if g.number_of_nodes() > 0:
        try:
            ranks = _pagerank(g, alpha=0.85)
        except Exception:  # noqa: BLE001
            ranks = {n: 0.0 for n in g.nodes}

    store.update_symbol_ranks(repo_id, ranks)

    # Folder tree
    paths = sorted(f.path for f in files)
    lines: list[str] = ["# Repo map", "", "## Tree", ""]
    for p in paths:
        depth = p.count("/")
        name = p.split("/")[-1]
        lines.append("  " * depth + f"- {name}")

    lines.extend(["", "## Top symbols", ""])

    # Per-file top symbols by rank
    by_file: dict[str, list[dict[str, Any]]] = {}
    for s in symbols:
        s = {**s, "rank": ranks.get(s["id"], s.get("rank") or 0)}
        by_file.setdefault(s["file"], []).append(s)

    out_path = repo_root / ".prd2pr" / "repo_map.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    body_lines = list(lines)
    for fpath in sorted(by_file.keys()):
        syms = sorted(by_file[fpath], key=lambda x: -float(x.get("rank") or 0))
        block = [f"### {fpath}", ""]
        for s in syms[:8]:
            sig = (s.get("signature") or s["qualified_name"]).replace("\n", " ")
            block.append(f"- `{s['qualified_name']}` — {sig[:120]}")
        block.append("")
        candidate = "\n".join(body_lines + block)
        if _approx_tokens(candidate) > token_budget:
            break
        body_lines.extend(block)

    text = "\n".join(body_lines) + "\n"
    # Hard trim if still over
    while _approx_tokens(text) > token_budget and "\n" in text:
        text = text.rsplit("\n", 2)[0] + "\n"

    out_path.write_text(text, encoding="utf-8")
    return out_path
