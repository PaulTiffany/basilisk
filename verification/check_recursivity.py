#!/usr/bin/env python3
"""Detect recursive justification in the claim graph.

Strongly connected components are computed mechanically. Cycles are rejected
unless the exact component is declared in recursion_policy.allowed_components.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS_PATH = ROOT / "verification" / "claims.json"


def strongly_connected_components(graph: dict[str, list[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(v: str) -> None:
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, []):
            if w not in indices:
                visit(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.append(w)
                if w == v:
                    break
            components.append(sorted(component))

    for vertex in sorted(graph):
        if vertex not in indices:
            visit(vertex)
    return components


def main() -> int:
    doc = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    claims = doc.get("claims", [])
    graph = {c["id"]: list(c.get("depends_on", [])) for c in claims}

    allowed_entries = doc.get("recursion_policy", {}).get("allowed_components", [])
    allowed: set[tuple[str, ...]] = set()
    malformed: list[str] = []
    for entry in allowed_entries:
        if not isinstance(entry, dict) or not entry.get("claims") or not entry.get("external_witness"):
            malformed.append(repr(entry))
            continue
        allowed.add(tuple(sorted(entry["claims"])))

    recursive: list[list[str]] = []
    for component in strongly_connected_components(graph):
        if len(component) > 1:
            recursive.append(component)
        elif component and component[0] in graph.get(component[0], []):
            recursive.append(component)

    errors: list[str] = []
    if malformed:
        errors.extend(f"malformed allowed recursion entry: {x}" for x in malformed)
    for component in recursive:
        key = tuple(component)
        if key not in allowed:
            errors.append(f"undeclared recursive justification: {component}")

    declared_but_absent = sorted(allowed - {tuple(c) for c in recursive})
    for component in declared_but_absent:
        errors.append(f"declared recursive component is not currently recursive: {list(component)}")

    if errors:
        print("RECURSIVITY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"RECURSIVITY CHECK: PASS — {len(graph)} claims, "
        f"{len(recursive)} declared recursive components"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
