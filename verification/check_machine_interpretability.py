#!/usr/bin/env python3
"""Validate total joins across Basilisk's machine-readable interpretability spine."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

from query_project import load_all, summary_view
from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VERIFY = ROOT / "verification"
INDEX = VERIFY / "interpretability_index.json"

ALLOWED_WITNESS_KINDS = {"lean", "python", "mechanism", "numpy", "prose"}


def main() -> int:
    errors: list[str] = []
    try:
        index = strict_load_json(INDEX)
        data = load_all()
    except Exception as exc:
        print("MACHINE INTERPRETABILITY CHECK: FAIL")
        print(f"- {exc}")
        return 1

    if index.get("schema_version") != 1:
        errors.append("unsupported interpretability_index schema_version")

    # Canonical source paths declared in the machine index must exist.
    for name, spec in index.get("canonical_sources", {}).items():
        if not isinstance(spec, dict):
            errors.append(f"canonical source {name}: specification must be an object")
            continue
        rel = spec.get("path")
        if rel is not None:
            if not isinstance(rel, str) or not (ROOT / rel).is_file():
                errors.append(f"canonical source {name}: missing path {rel!r}")
        directory = spec.get("directory")
        if directory is not None:
            if not isinstance(directory, str) or not (ROOT / directory).is_dir():
                errors.append(f"canonical source {name}: missing directory {directory!r}")

    claims = {row["id"]: row for row in data["claims"]}
    claim_scope = {row["id"]: row for row in data["scope"].get("claim_scope", [])}
    frontier_scope = {row["id"]: row for row in data["scope"].get("frontier_scope", [])}
    open_frontier = {row["id"]: row for row in data["open_frontier"]}
    closed_frontier = {row["id"]: row for row in data["closed_frontier"]}

    bindings_by_claim: dict[str, list[dict]] = defaultdict(list)
    for row in data["bindings"]:
        bindings_by_claim[str(row.get("claim_id"))].append(row)

    formal_by_claim: dict[str, list[dict]] = defaultdict(list)
    for row in data["formal_inventory"]:
        cid = row.get("semantic_claim_id")
        if cid:
            formal_by_claim[str(cid)].append(row)

    graph_edges_by_claim: dict[str, list[dict]] = defaultdict(list)
    graph_agreements_by_claim: dict[str, list[dict]] = defaultdict(list)
    for row in data["witness_graph"].get("edges", []):
        graph_edges_by_claim[str(row.get("claim_id"))].append(row)
    for row in data["witness_graph"].get("agreements", []):
        graph_agreements_by_claim[str(row.get("claim_id"))].append(row)

    # Every semantic claim must be self-describing enough to resolve without prose inference.
    for cid, claim in claims.items():
        if cid not in claim_scope:
            errors.append(f"{cid}: missing scope placement")
        if not bindings_by_claim.get(cid):
            errors.append(f"{cid}: no exact provenance binding")

        declared = claim.get("witnesses", [])
        if not isinstance(declared, list):
            errors.append(f"{cid}: witnesses must be a list")
            declared = []
        unknown = sorted(set(declared) - ALLOWED_WITNESS_KINDS)
        if unknown:
            errors.append(f"{cid}: unknown declared witness kind(s) {unknown}")

        bound_kinds = {str(row.get("kind")) for row in bindings_by_claim.get(cid, [])}
        for witness in declared:
            if witness in {"lean", "python", "mechanism", "prose"} and witness not in bound_kinds:
                errors.append(f"{cid}: declared {witness} witness has no exact binding")

        if claim.get("status") == "lean_theorem":
            formal_rows = formal_by_claim.get(cid, [])
            if not formal_rows:
                errors.append(f"{cid}: Lean theorem has no formal-inventory symbol")
            bound_lean_paths = {
                str(row.get("path")) for row in bindings_by_claim.get(cid, []) if row.get("kind") == "lean"
            }
            formal_modules = {str(row.get("module")) for row in formal_rows}
            if bound_lean_paths.isdisjoint(formal_modules):
                errors.append(
                    f"{cid}: Lean provenance paths and formal-inventory modules do not intersect: "
                    f"bindings={sorted(bound_lean_paths)}, formal={sorted(formal_modules)}"
                )

        # Witness graph is optional per claim, but if present its substrate must be declared.
        if graph_edges_by_claim.get(cid) or graph_agreements_by_claim.get(cid):
            graph_substrates: set[str] = set()
            node_by_id = {n.get("id"): n for n in data["witness_graph"].get("nodes", [])}
            for edge in graph_edges_by_claim.get(cid, []):
                for endpoint in (edge.get("source"), edge.get("target")):
                    substrate = node_by_id.get(endpoint, {}).get("substrate")
                    if substrate in {"lean", "python", "numpy"}:
                        graph_substrates.add(substrate)
            missing = sorted(graph_substrates - set(declared))
            if missing:
                errors.append(f"{cid}: witness graph uses undeclared executable/formal substrate(s) {missing}")

    # Frontier must partition open and closed state, with scheduling only on open items.
    overlap = sorted(set(open_frontier) & set(closed_frontier))
    if overlap:
        errors.append(f"frontier IDs both open and closed: {overlap}")
    for fid in open_frontier:
        if fid not in frontier_scope:
            errors.append(f"{fid}: open frontier item lacks scope/schedule")
    for fid, closure in closed_frontier.items():
        if fid in frontier_scope:
            errors.append(f"{fid}: closed frontier item still has active scope/schedule")
        for cid in closure.get("closed_by_claims", []):
            if cid not in claims:
                errors.append(f"{fid}: closure references unknown claim {cid}")
        for rel in closure.get("evidence", []):
            if not isinstance(rel, str) or not (ROOT / rel).is_file():
                errors.append(f"{fid}: closure evidence cannot be resolved: {rel!r}")

    # Claim dependency graph is explicitly resolvable.
    for cid, claim in claims.items():
        for dep in claim.get("depends_on", []):
            if dep not in claims:
                errors.append(f"{cid}: unresolved dependency {dep}")

    # The public summary is computed from the same joined state.
    summary = summary_view(data)
    if summary["claim_count"] != len(claims):
        errors.append("summary claim_count disagrees with canonical claim registry")
    if summary["open_frontier_count"] != len(open_frontier):
        errors.append("summary open_frontier_count disagrees with canonical frontier")
    if summary["closed_frontier_count"] != len(closed_frontier):
        errors.append("summary closed_frontier_count disagrees with canonical closures")

    if errors:
        print("MACHINE INTERPRETABILITY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "MACHINE INTERPRETABILITY CHECK: PASS — "
        f"{len(claims)} claims, {len(data['bindings'])} bindings, "
        f"{len(data['formal_inventory'])} formal symbols, "
        f"{len(open_frontier)} open + {len(closed_frontier)} closed frontier items"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
