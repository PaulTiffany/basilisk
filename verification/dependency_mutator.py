#!/usr/bin/env python3
"""Executable dependency-topology witness for the family-closure layer."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
SPEC = ROOT / "verification" / "dependency_mutation.json"


def family_closure(vertices: list[str], edges: set[tuple[str, str]], x: str) -> set[str]:
    parents = {v for v in vertices if (v, x) in edges}
    children = {v for v in vertices if (x, v) in edges}
    coparents = {
        v
        for v in vertices
        if v != x
        and any((x, child) in edges and (v, child) in edges for child in vertices)
    }
    return parents | children | coparents


def apply_mutation(edges: set[tuple[str, str]], mutation: dict) -> set[tuple[str, str]]:
    out = set(edges)
    op = mutation.get("operator")
    edge = tuple(mutation.get("edge", []))
    if len(edge) != 2:
        raise ValueError("mutation edge must have exactly two vertices")
    if op == "add_edge":
        out.add((edge[0], edge[1]))
    elif op == "remove_edge":
        out.discard((edge[0], edge[1]))
    else:
        raise ValueError(f"unsupported dependency mutation operator: {op!r}")
    return out


def evaluate(spec: dict) -> dict:
    vertices = list(spec["vertices"])
    x = spec["distinguished"]
    target = spec["target_vertex"]
    before_edges = {tuple(edge) for edge in spec["before_edges"]}
    after_edges = apply_mutation(before_edges, spec["mutation"])
    before = family_closure(vertices, before_edges, x)
    after = family_closure(vertices, after_edges, x)
    return {
        "before_family_closure": sorted(before),
        "after_family_closure": sorted(after),
        "target_before": target in before,
        "target_after": target in after,
        "changed_dimensions": ["dependency_edges", "family_closure"],
        "preserved_dimensions": ["vertex_set", "distinguished_vertex"],
        "residual": sorted(after.symmetric_difference(before)),
        "loss_class": "none",
    }


def main() -> int:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    result = evaluate(spec)
    expected = spec["expected"]
    observed = {key: result[key] for key in expected}
    if observed != expected:
        print("DEPENDENCY MUTATION WITNESS: FAIL")
        print(json.dumps({"expected": expected, "observed": observed}, indent=2))
        return 1
    print("DEPENDENCY MUTATION WITNESS: PASS")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
