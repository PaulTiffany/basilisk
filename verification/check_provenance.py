#!/usr/bin/env python3
"""Validate the machine-readable claim/provenance spine.

Claims remain centralized; exact source bindings may be sharded across
verification/bindings*.json. Shards are merged deterministically by filename,
while claim IDs and exact fragment receipts remain globally checked.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
CLAIMS_PATH = ROOT / "verification" / "claims.json"
BINDINGS_GLOB = "bindings*.json"

ALLOWED_STATUSES = {
    "definition",
    "standard_theorem",
    "lean_theorem",
    "target_theorem",
    "engineering_mechanism",
    "engineering_hypothesis",
    "constitutional_rule",
    "counterexample",
}

MECHANICAL_WITNESS_KINDS = {"lean", "python", "mechanism", "numpy"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(fragment: str) -> str:
    return hashlib.sha256(fragment.encode("utf-8")).hexdigest()


def load_bindings(errors: list[str]) -> tuple[list[dict], list[str]]:
    paths = sorted((ROOT / "verification").glob(BINDINGS_GLOB))
    if not paths:
        errors.append("no provenance binding shards found")
        return [], []
    bindings: list[dict] = []
    names: list[str] = []
    for path in paths:
        names.append(path.name)
        try:
            doc = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: malformed JSON: {exc}")
            continue
        if doc.get("schema_version") != 1:
            errors.append(f"{path.name}: unsupported schema_version {doc.get('schema_version')!r}")
        bindings.extend(doc.get("bindings", []))
    return bindings, names


def main() -> int:
    claims_doc = load_json(CLAIMS_PATH)
    errors: list[str] = []
    bindings, shard_names = load_bindings(errors)
    claims = claims_doc.get("claims", [])

    ids = [c.get("id") for c in claims]
    if len(ids) != len(set(ids)):
        errors.append("duplicate claim IDs")

    claim_by_id = {c["id"]: c for c in claims if "id" in c}
    for claim in claims:
        cid = claim.get("id", "<missing>")
        status = claim.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{cid}: invalid status {status!r}")
        for dep in claim.get("depends_on", []):
            if dep not in claim_by_id:
                errors.append(f"{cid}: unknown dependency {dep}")
        if not claim.get("statement"):
            errors.append(f"{cid}: empty canonical statement")

    bindings_by_claim: dict[str, list[dict]] = defaultdict(list)
    seen_receipts: set[tuple[str, str, str, str]] = set()
    for binding in bindings:
        cid = binding.get("claim_id")
        if cid not in claim_by_id:
            errors.append(f"binding references unknown claim {cid}")
            continue
        receipt_key = (
            str(cid), str(binding.get("kind")), str(binding.get("path")), str(binding.get("sha256"))
        )
        if receipt_key in seen_receipts:
            errors.append(f"duplicate provenance receipt across shards for {cid}: {binding.get('path')}")
        seen_receipts.add(receipt_key)
        bindings_by_claim[cid].append(binding)

        rel = binding.get("path")
        if not rel:
            errors.append(f"{cid}: binding missing path")
            continue
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"{cid}: bound artifact does not exist: {rel}")
            continue

        fragment = binding.get("fragment", "")
        expected = binding.get("sha256", "")
        if not fragment:
            errors.append(f"{cid}: empty provenance fragment in {rel}")
            continue
        actual = digest(fragment)
        if actual != expected:
            errors.append(
                f"{cid}: receipt mismatch for declared fragment in {rel}: "
                f"expected {expected}, computed {actual}"
            )
        text = path.read_text(encoding="utf-8")
        if fragment not in text:
            errors.append(f"{cid}: provenance fragment no longer occurs in {rel}")

    for cid, claim in claim_by_id.items():
        declared = set(claim.get("witnesses", []))
        bound_kinds = {b.get("kind") for b in bindings_by_claim.get(cid, [])}

        if claim["status"] == "lean_theorem" and "lean" not in bound_kinds:
            errors.append(f"{cid}: lean_theorem lacks exact Lean binding")
        if claim["status"] == "target_theorem" and "lean" in bound_kinds:
            errors.append(f"{cid}: target_theorem must not masquerade as Lean-proved")

        missing_declared = {
            w for w in declared
            if w in MECHANICAL_WITNESS_KINDS
            and w not in bound_kinds
            and not (w == "numpy" and (ROOT / "verification" / "numeric_witness.py").is_file())
        }
        if missing_declared:
            errors.append(
                f"{cid}: declared witnesses without corresponding artifact: {sorted(missing_declared)}"
            )

    if errors:
        print("PROVENANCE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"PROVENANCE CHECK: PASS — {len(claims)} claims, {len(bindings)} exact bindings, "
        f"{len(shard_names)} binding shard(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
