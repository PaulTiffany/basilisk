#!/usr/bin/env python3
"""Enforce finite Core/Theory/Bridge scope during consolidation."""

from __future__ import annotations

import os
from pathlib import Path

from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
CLAIMS = ROOT / "verification" / "claims.json"
FRONTIER = ROOT / "verification" / "completeness_frontier.json"
SCOPE = ROOT / "verification" / "scope_registry.json"

ALLOWED_LAYERS = {"core", "theory", "bridge"}
ALLOWED_SCHEDULES = {"active", "deferred", "parked"}


def unique_ids(rows: list[dict], label: str, errors: list[str]) -> list[str]:
    ids: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            errors.append(f"{label}[{index}] missing nonempty string id")
            continue
        ids.append(rid)
    if len(ids) != len(set(ids)):
        errors.append(f"{label} contains duplicate IDs")
    return ids


def main() -> int:
    errors: list[str] = []
    try:
        claims_doc = strict_load_json(CLAIMS)
        frontier_doc = strict_load_json(FRONTIER)
        scope_doc = strict_load_json(SCOPE)
    except Exception as exc:
        print("SCOPE REGISTRY CHECK: FAIL")
        print(f"- malformed strict JSON: {exc}")
        return 1

    claims = claims_doc.get("claims", []) if isinstance(claims_doc, dict) else []
    frontier = frontier_doc.get("frontier", []) if isinstance(frontier_doc, dict) else []
    claim_scope = scope_doc.get("claim_scope", []) if isinstance(scope_doc, dict) else []
    frontier_scope = scope_doc.get("frontier_scope", []) if isinstance(scope_doc, dict) else []

    if not all(isinstance(x, list) for x in (claims, frontier, claim_scope, frontier_scope)):
        print("SCOPE REGISTRY CHECK: FAIL")
        print("- claims/frontier/scope payloads must be lists")
        return 1

    claim_ids = set(unique_ids(claims, "claims", errors))
    open_ids = set(unique_ids(frontier, "frontier", errors))
    scoped_claim_ids = set(unique_ids(claim_scope, "claim_scope", errors))
    scoped_frontier_ids = set(unique_ids(frontier_scope, "frontier_scope", errors))

    missing_claims = claim_ids - scoped_claim_ids
    extra_claims = scoped_claim_ids - claim_ids
    if missing_claims:
        errors.append(f"claims missing scope placement: {sorted(missing_claims)}")
    if extra_claims:
        errors.append(f"scope registry references unknown claims: {sorted(extra_claims)}")

    missing_frontier = open_ids - scoped_frontier_ids
    extra_frontier = scoped_frontier_ids - open_ids
    if missing_frontier:
        errors.append(f"open frontier items missing scope placement: {sorted(missing_frontier)}")
    if extra_frontier:
        errors.append(f"scope registry references non-open frontier items: {sorted(extra_frontier)}")

    for row in claim_scope:
        if not isinstance(row, dict):
            continue
        layer = row.get("layer")
        if layer not in ALLOWED_LAYERS:
            errors.append(f"{row.get('id')}: invalid claim layer {layer!r}")

    for row in frontier_scope:
        if not isinstance(row, dict):
            continue
        fid = row.get("id")
        layer = row.get("layer")
        schedule = row.get("schedule")
        reason = row.get("reason")
        if layer not in ALLOWED_LAYERS:
            errors.append(f"{fid}: invalid frontier layer {layer!r}")
        if schedule not in ALLOWED_SCHEDULES:
            errors.append(f"{fid}: invalid frontier schedule {schedule!r}")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{fid}: frontier scheduling requires a nonempty reason")
        if schedule == "active" and layer != "core":
            errors.append(f"{fid}: only Core debt may be active during consolidation")
        if layer == "bridge" and schedule != "parked":
            errors.append(f"{fid}: Bridge debt must remain parked during consolidation")

    if errors:
        print("SCOPE REGISTRY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    active = sorted(
        row["id"] for row in frontier_scope
        if isinstance(row, dict) and row.get("schedule") == "active"
    )
    deferred = sorted(
        row["id"] for row in frontier_scope
        if isinstance(row, dict) and row.get("schedule") == "deferred"
    )
    parked = sorted(
        row["id"] for row in frontier_scope
        if isinstance(row, dict) and row.get("schedule") == "parked"
    )
    print(
        "SCOPE REGISTRY CHECK: PASS — "
        f"{len(claim_ids)} claims placed, {len(open_ids)} open debts placed; "
        f"active={active}, deferred={deferred}, parked={parked}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
