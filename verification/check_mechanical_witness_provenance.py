#!/usr/bin/env python3
"""Deterministic witness for provenance without identity or total judgment.

The witness attests only the declared transformation relation. It does not
decide semantic truth, normative correctness, actor identity, or closure.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

OPERATOR_ID = "collapse_ascii_whitespace_v1"
NON_CLAIMS = [
    "semantic_truth",
    "normative_correctness",
    "actor_identity",
    "closure",
]


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def apply_operator(operator_id: str, source: str) -> str:
    if operator_id != OPERATOR_ID:
        raise ValueError(f"unknown operator: {operator_id}")
    # The fixture is intentionally ASCII so this operator is stable across
    # Python/Unicode database versions.
    return " ".join(source.split())


def build_receipt(source: str) -> dict[str, Any]:
    output = apply_operator(OPERATOR_ID, source)
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "kind": "basilisk_mechanical_witness_provenance",
        "operator_id": OPERATOR_ID,
        "scope": "transition_only",
        "input": source,
        "input_sha256": digest_text(source),
        "output": output,
        "output_sha256": digest_text(output),
        "non_claims": NON_CLAIMS,
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical_bytes(receipt)).hexdigest()
    return receipt


def verify_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if receipt.get("kind") != "basilisk_mechanical_witness_provenance":
        errors.append("unexpected receipt kind")
    if receipt.get("scope") != "transition_only":
        errors.append("mechanical witness scope must remain transition_only")
    if receipt.get("non_claims") != NON_CLAIMS:
        errors.append("non-claim boundary drifted")

    source = receipt.get("input")
    output = receipt.get("output")
    operator_id = receipt.get("operator_id")
    if not isinstance(source, str) or not isinstance(output, str) or not isinstance(operator_id, str):
        errors.append("input, output, and operator_id must be strings")
        return errors

    if receipt.get("input_sha256") != digest_text(source):
        errors.append("input digest mismatch")
    if receipt.get("output_sha256") != digest_text(output):
        errors.append("output digest mismatch")

    try:
        expected_output = apply_operator(operator_id, source)
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if output != expected_output:
            errors.append("declared output is not the deterministic operator result")

    declared_receipt = receipt.get("receipt_sha256")
    if not isinstance(declared_receipt, str) or len(declared_receipt) != 64:
        errors.append("receipt_sha256 must be a lowercase SHA-256 digest")
    else:
        unsigned = dict(receipt)
        unsigned.pop("receipt_sha256", None)
        actual_receipt = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
        if actual_receipt != declared_receipt:
            errors.append("receipt digest mismatch")
    return errors


def main() -> int:
    source = "  provenance   records what happened; identity is a separate question  "
    receipt = build_receipt(source)

    errors = verify_receipt(receipt)
    if errors:
        print("MECHANICAL WITNESS PROVENANCE: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    if "actor_identity" in receipt:
        print("MECHANICAL WITNESS PROVENANCE: FAIL")
        print("- actor identity became required provenance")
        return 1

    tampered = dict(receipt)
    tampered["output"] = tampered["output"] + " altered"
    if not verify_receipt(tampered):
        print("MECHANICAL WITNESS PROVENANCE: FAIL")
        print("- tampered output was not detected")
        return 1

    overclaim = dict(receipt)
    overclaim["scope"] = "global_judgment"
    unsigned = dict(overclaim)
    unsigned.pop("receipt_sha256", None)
    overclaim["receipt_sha256"] = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    if not verify_receipt(overclaim):
        print("MECHANICAL WITNESS PROVENANCE: FAIL")
        print("- total-judgment scope was accepted")
        return 1

    print(
        "MECHANICAL WITNESS PROVENANCE: PASS — "
        "transition witnessed without identity or total-judgment claim"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
