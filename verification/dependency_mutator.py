#!/usr/bin/env python3
"""Executable dependency-topology witness for the family-closure layer."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
SPEC = ROOT / "verification" / "dependency_mutation.json"


def validate_spec(spec: dict) -> None:
    if spec.get("schema_version") != 1:
        raise ValueError(f"unsupported schema_version: {spec.get('schema_version')!r}")
    vertices = spec.get("vertices")
    if not isinstance(vertices, list) or len(vertices) < 2:
        raise ValueError("vertices must be a list with at least two entries")
    if any(not isinstance(v, str) or not v for v in vertices):
        raise ValueError("every vertex must be a non-empty string")
    if len(vertices) != len(set(vertices)):
        raise ValueError("vertices must be unique")
    vertex_set = set(vertices)
    if spec.get("distinguished") not in vertex_set:
        raise ValueError("distinguished vertex must occur in vertices")
    if spec.get("target_vertex") not in vertex_set:
        raise ValueError("target_vertex must occur in vertices")

    raw_edges = spec.get("before_edges")
    if not isinstance(raw_edges, list):
        raise ValueError("before_edges must be a list")
    edges: list[tuple[str, str]] = []
    for index, raw in enumerate(raw_edges):
        if not isinstance(raw, list) or len(raw) != 2:
            raise ValueError(f"before_edges[{index}] must contain exactly two vertices")
        edge = (raw[0], raw[1])
        if edge[0] not in vertex_set or edge[1] not in vertex_set:
            raise ValueError(f"before_edges[{index}] references an unknown vertex")
        edges.append(edge)
    if len(edges) != len(set(edges)):
        raise ValueError("before_edges must not contain duplicates")

    mutation = spec.get("mutation")
    if not isinstance(mutation, dict):
        raise ValueError("mutation must be an object")
    op = mutation.get("operator")
    if op not in {"add_edge", "remove_edge"}:
        raise ValueError(f"unsupported dependency mutation operator: {op!r}")
    raw_edge = mutation.get("edge")
    if not isinstance(raw_edge, list) or len(raw_edge) != 2:
        raise ValueError("mutation edge must have exactly two vertices")
    edge = (raw_edge[0], raw_edge[1])
    if edge[0] not in vertex_set or edge[1] not in vertex_set:
        raise ValueError("mutation edge references an unknown vertex")
    before = set(edges)
    if op == "add_edge" and edge in before:
        raise ValueError("add_edge mutation is a no-op because the edge already exists")
    if op == "remove_edge" and edge not in before:
        raise ValueError("remove_edge mutation is a no-op because the edge is absent")


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
    op = mutation["operator"]
    edge = tuple(mutation["edge"])
    if op == "add_edge":
        out.add((edge[0], edge[1]))
    else:
        out.remove((edge[0], edge[1]))
    return out


def evaluate(spec: dict) -> dict:
    validate_spec(spec)
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
    try:
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        result = evaluate(spec)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        print("DEPENDENCY MUTATION WITNESS: FAIL")
        print(f"- malformed witness specification: {exc}")
        return 1
    expected = spec.get("expected")
    if not isinstance(expected, dict):
        print("DEPENDENCY MUTATION WITNESS: FAIL")
        print("- expected must be an object")
        return 1
    observed = {key: result.get(key) for key in expected}
    if observed != expected:
        print("DEPENDENCY MUTATION WITNESS: FAIL")
        print(json.dumps({"expected": expected, "observed": observed}, indent=2))
        return 1
    print("DEPENDENCY MUTATION WITNESS: PASS")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
