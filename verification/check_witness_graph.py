#!/usr/bin/env python3
"""Validate the cross-representation witness graph.

The graph is deliberately stricter than a diagram: transports must connect
existing nodes, cite existing semantic claims, declare an allowed loss class,
name a checker artifact, and disclose a residual whenever the transport is not
exact. Agreement claims must provide at least two valid source-to-observable
paths, and every path must actually compose.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
GRAPH = ROOT / "verification" / "witness_graph.json"
CLAIMS = ROOT / "verification" / "claims.json"

LOSS_CLASSES = {"exact", "quotient", "projective", "interpretive"}


def artifact_exists(value: str) -> bool:
    if value == "ActionGate":
        return True
    return (ROOT / value).exists()


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
    claim_ids = {c["id"] for c in claims.get("claims", [])}
    errors: list[str] = []

    nodes = graph.get("nodes", [])
    node_ids = [n.get("id") for n in nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("duplicate witness node IDs")
    node_by_id = {n["id"]: n for n in nodes if n.get("id")}
    for node in nodes:
        artifact = node.get("artifact", "")
        if not artifact_exists(artifact):
            errors.append(f"{node.get('id')}: missing node artifact {artifact}")

    edges = graph.get("edges", [])
    edge_ids = [e.get("id") for e in edges]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("duplicate witness edge IDs")
    edge_by_id = {e["id"]: e for e in edges if e.get("id")}

    for edge in edges:
        eid = edge.get("id", "<missing>")
        if edge.get("source") not in node_by_id:
            errors.append(f"{eid}: unknown source {edge.get('source')}")
        if edge.get("target") not in node_by_id:
            errors.append(f"{eid}: unknown target {edge.get('target')}")
        if edge.get("claim_id") not in claim_ids:
            errors.append(f"{eid}: unknown claim {edge.get('claim_id')}")
        loss = edge.get("loss_class")
        if loss not in LOSS_CLASSES:
            errors.append(f"{eid}: invalid loss class {loss!r}")
        residual = edge.get("residual", "").strip()
        if loss != "exact" and not residual:
            errors.append(f"{eid}: non-exact transport lacks explicit residual")
        if loss == "exact" and residual:
            errors.append(f"{eid}: exact transport must not declare a residual")
        checker = edge.get("checker", "")
        if not checker or not artifact_exists(checker):
            errors.append(f"{eid}: checker artifact missing: {checker}")

    used_nodes: set[str] = set()
    for agreement in graph.get("agreements", []):
        aid = agreement.get("id", "<missing>")
        source = agreement.get("source")
        observable = agreement.get("observable")
        claim_id = agreement.get("claim_id")
        paths = agreement.get("paths", [])
        if claim_id not in claim_ids:
            errors.append(f"{aid}: unknown agreement claim {claim_id}")
        if source not in node_by_id or observable not in node_by_id:
            errors.append(f"{aid}: unknown source/observable")
            continue
        if len(paths) < 2:
            errors.append(f"{aid}: agreement requires at least two independent paths")
        if not agreement.get("scope", "").strip():
            errors.append(f"{aid}: agreement lacks explicit scope/non-claim")

        for path in paths:
            current = source
            used_nodes.add(current)
            if not path:
                errors.append(f"{aid}: empty agreement path")
                continue
            for eid in path:
                edge = edge_by_id.get(eid)
                if edge is None:
                    errors.append(f"{aid}: unknown edge {eid}")
                    break
                if edge.get("claim_id") != claim_id:
                    errors.append(f"{aid}: edge {eid} is bound to a different claim")
                if edge.get("source") != current:
                    errors.append(
                        f"{aid}: path discontinuity at {eid}: expected source {current}, "
                        f"found {edge.get('source')}"
                    )
                current = edge.get("target")
                used_nodes.add(current)
            if current != observable:
                errors.append(f"{aid}: path terminates at {current}, not {observable}")

    # Nodes may exist for future work only if explicitly marked optional.
    for nid, node in node_by_id.items():
        if nid not in used_nodes and not node.get("optional", False):
            errors.append(f"orphan witness node not used by an agreement: {nid}")

    if errors:
        print("WITNESS GRAPH CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"WITNESS GRAPH CHECK: PASS — {len(nodes)} nodes, {len(edges)} transports, "
        f"{len(graph.get('agreements', []))} agreement(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
