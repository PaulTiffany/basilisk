#!/usr/bin/env python3
"""Resolve Basilisk's canonical registries into deterministic machine-readable views."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from registry_io import load_registry_list, strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VERIFY = ROOT / "verification"


def load_all() -> dict[str, Any]:
    errors: list[str] = []
    claims_doc = strict_load_json(VERIFY / "claims.json")
    scope_doc = strict_load_json(VERIFY / "scope_registry.json")
    open_doc = strict_load_json(VERIFY / "completeness_frontier.json")
    closed_doc = strict_load_json(VERIFY / "frontier_closures.json")
    graph_doc = strict_load_json(VERIFY / "witness_graph.json")
    bindings, binding_shards = load_registry_list(
        VERIFY,
        base_name="bindings.json",
        shard_prefix="bindings_",
        payload_key="bindings",
        errors=errors,
    )
    formal, formal_shards = load_registry_list(
        VERIFY,
        base_name="formal_inventory.json",
        shard_prefix="formal_inventory_",
        payload_key="formal_claims",
        errors=errors,
    )
    assumptions_doc = strict_load_json(VERIFY / "theorem_assumptions.json")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "claims": claims_doc.get("claims", []),
        "scope": scope_doc,
        "open_frontier": open_doc.get("frontier", []),
        "closed_frontier": closed_doc.get("closures", []),
        "bindings": bindings,
        "binding_shards": binding_shards,
        "formal_inventory": formal,
        "formal_shards": formal_shards,
        "witness_graph": graph_doc,
        "assumptions": assumptions_doc.get("assumptions", []),
    }


def by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["id"]): row for row in rows if isinstance(row, dict) and "id" in row}


def claim_view(data: dict[str, Any], claim_id: str) -> dict[str, Any]:
    claims = by_id(data["claims"])
    if claim_id not in claims:
        raise KeyError(f"unknown claim: {claim_id}")
    claim = claims[claim_id]
    scope = by_id(data["scope"].get("claim_scope", [])).get(claim_id)
    bindings = sorted(
        [row for row in data["bindings"] if row.get("claim_id") == claim_id],
        key=lambda row: (str(row.get("kind")), str(row.get("path")), str(row.get("sha256"))),
    )
    formal = sorted(
        [row for row in data["formal_inventory"] if row.get("semantic_claim_id") == claim_id],
        key=lambda row: (str(row.get("module")), str(row.get("symbol"))),
    )
    graph = data["witness_graph"]
    edges = sorted(
        [row for row in graph.get("edges", []) if row.get("claim_id") == claim_id],
        key=lambda row: str(row.get("id")),
    )
    agreements = sorted(
        [row for row in graph.get("agreements", []) if row.get("claim_id") == claim_id],
        key=lambda row: str(row.get("id")),
    )
    return {
        "id": claim_id,
        "title": claim.get("title"),
        "status": claim.get("status"),
        "statement": claim.get("statement"),
        "interpretation": claim.get("interpretation"),
        "depends_on": list(claim.get("depends_on", [])),
        "declared_witness_kinds": list(claim.get("witnesses", [])),
        "scope": scope,
        "bindings": bindings,
        "formal_symbols": formal,
        "witness_transports": edges,
        "witness_agreements": agreements,
    }


def frontier_view(data: dict[str, Any], frontier_id: str) -> dict[str, Any]:
    open_rows = by_id(data["open_frontier"])
    closed_rows = by_id(data["closed_frontier"])
    scope_rows = by_id(data["scope"].get("frontier_scope", []))
    if frontier_id in open_rows:
        row = open_rows[frontier_id]
        return {
            "id": frontier_id,
            "state": "open",
            "surface": row.get("surface"),
            "gap": row.get("gap"),
            "closure_condition": row.get("closure_condition"),
            "scope": scope_rows.get(frontier_id),
        }
    if frontier_id in closed_rows:
        row = closed_rows[frontier_id]
        return {
            "id": frontier_id,
            "state": "closed",
            "surface": row.get("surface"),
            "closed_by_claims": list(row.get("closed_by_claims", [])),
            "evidence": list(row.get("evidence", [])),
            "closure": row.get("closure"),
        }
    raise KeyError(f"unknown frontier item: {frontier_id}")


def summary_view(data: dict[str, Any]) -> dict[str, Any]:
    claim_scope = data["scope"].get("claim_scope", [])
    frontier_scope = data["scope"].get("frontier_scope", [])
    layer_counts = {layer: 0 for layer in ("core", "theory", "bridge")}
    for row in claim_scope:
        layer = row.get("layer")
        if layer in layer_counts:
            layer_counts[layer] += 1
    schedule_counts = {schedule: 0 for schedule in ("active", "deferred", "parked")}
    for row in frontier_scope:
        schedule = row.get("schedule")
        if schedule in schedule_counts:
            schedule_counts[schedule] += 1
    return {
        "schema_version": 1,
        "claim_count": len(data["claims"]),
        "claim_layers": layer_counts,
        "open_frontier_count": len(data["open_frontier"]),
        "closed_frontier_count": len(data["closed_frontier"]),
        "open_schedules": schedule_counts,
        "binding_count": len(data["bindings"]),
        "formal_symbol_count": len(data["formal_inventory"]),
        "assumption_entry_count": len(data["assumptions"]),
        "witness_graph": {
            "nodes": len(data["witness_graph"].get("nodes", [])),
            "edges": len(data["witness_graph"].get("edges", [])),
            "agreements": len(data["witness_graph"].get("agreements", [])),
        },
    }


def all_view(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "summary": summary_view(data),
        "claims": [claim_view(data, cid) for cid in sorted(by_id(data["claims"]))],
        "frontier": [
            frontier_view(data, fid)
            for fid in sorted(set(by_id(data["open_frontier"])) | set(by_id(data["closed_frontier"])))
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("summary")
    p_claim = sub.add_parser("claim")
    p_claim.add_argument("id")
    p_frontier = sub.add_parser("frontier")
    p_frontier.add_argument("id")
    sub.add_parser("all")
    args = parser.parse_args()

    try:
        data = load_all()
        if args.mode == "summary":
            result = summary_view(data)
        elif args.mode == "claim":
            result = claim_view(data, args.id)
        elif args.mode == "frontier":
            result = frontier_view(data, args.id)
        else:
            result = all_view(data)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True))
        return 1

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
