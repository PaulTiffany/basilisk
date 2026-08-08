#!/usr/bin/env python3
"""Validate that closed technical-debt frontier items carry inspectable evidence."""

from __future__ import annotations

import os
from pathlib import Path

from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VERIFY = ROOT / "verification"
FRONTIER = VERIFY / "completeness_frontier.json"
CLOSURES = VERIFY / "frontier_closures.json"
CLAIMS = VERIFY / "claims.json"


def main() -> int:
    errors: list[str] = []
    try:
        frontier_doc = strict_load_json(FRONTIER)
        closure_doc = strict_load_json(CLOSURES)
        claims_doc = strict_load_json(CLAIMS)
    except (ValueError, OSError) as exc:
        print("FRONTIER CLOSURE CHECK: FAIL")
        print(f"- {exc}")
        return 1

    if frontier_doc.get("schema_version") != 1:
        errors.append("unsupported completeness frontier schema_version")
    if closure_doc.get("schema_version") != 1:
        errors.append("unsupported frontier closure schema_version")
    if claims_doc.get("schema_version") != 1:
        errors.append("unsupported claim schema_version")

    open_items = frontier_doc.get("frontier", [])
    closures = closure_doc.get("closures", [])
    claims = claims_doc.get("claims", [])
    if not isinstance(open_items, list):
        errors.append("frontier must be a list")
        open_items = []
    if not isinstance(closures, list):
        errors.append("closures must be a list")
        closures = []

    open_ids = {item.get("id") for item in open_items if isinstance(item, dict)}
    claim_ids = {item.get("id") for item in claims if isinstance(item, dict)}
    closed_ids: set[str] = set()

    for index, item in enumerate(closures):
        if not isinstance(item, dict):
            errors.append(f"closures[{index}] must be an object")
            continue
        cid = item.get("id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"closures[{index}] lacks a valid id")
            continue
        if cid in closed_ids:
            errors.append(f"duplicate frontier closure id: {cid}")
        closed_ids.add(cid)
        if cid in open_ids:
            errors.append(f"{cid}: item cannot be both open and closed")
        if not str(item.get("surface", "")).strip():
            errors.append(f"{cid}: closure lacks surface")
        if not str(item.get("closure", "")).strip():
            errors.append(f"{cid}: closure lacks rationale")

        closed_by = item.get("closed_by_claims", [])
        if not isinstance(closed_by, list) or not closed_by:
            errors.append(f"{cid}: closure requires at least one claim witness")
        else:
            for claim_id in closed_by:
                if claim_id not in claim_ids:
                    errors.append(f"{cid}: unknown closure claim {claim_id!r}")

        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{cid}: closure requires evidence artifacts")
        else:
            for rel in evidence:
                if not isinstance(rel, str) or not rel:
                    errors.append(f"{cid}: malformed evidence path {rel!r}")
                    continue
                path = (ROOT / rel).resolve()
                try:
                    path.relative_to(ROOT)
                except ValueError:
                    errors.append(f"{cid}: evidence escapes repository root: {rel}")
                    continue
                if not path.is_file():
                    errors.append(f"{cid}: missing closure evidence: {rel}")

    if errors:
        print("FRONTIER CLOSURE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"FRONTIER CLOSURE CHECK: PASS — {len(closed_ids)} closed debt items, "
        f"{len(open_ids)} open frontier items"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
