#!/usr/bin/env python3
"""Check the finite privacy / minimum-sufficient-disclosure witness surface."""

from __future__ import annotations

from pathlib import Path

from registry_io import strict_load_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "verification" / "privacy_witnesses.json"


def accountability_view(w: dict[str, object]) -> tuple[bool, bool, bool, bool]:
    return (
        bool(w["external_event_observable"]),
        bool(w["authority_trace_observable"]),
        bool(w["provenance_observable"]),
        bool(w["compliance_witness_observable"]),
    )


def sufficient(w: dict[str, object]) -> bool:
    return all(accountability_view(w))


def main() -> int:
    doc = strict_load_json(SPEC)
    errors: list[str] = []
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        errors.append("privacy registry must be a schema_version 1 object")
        witnesses = []
    else:
        witnesses = doc.get("witnesses", [])
        if not isinstance(witnesses, list):
            errors.append("witnesses must be a list")
            witnesses = []

    seen: set[str] = set()
    required_bool = (
        "external_event_observable",
        "authority_trace_observable",
        "provenance_observable",
        "compliance_witness_observable",
        "private_interior_exposed",
        "expected_sufficient_for_accountability",
    )
    for witness in witnesses:
        if not isinstance(witness, dict):
            errors.append("every witness must be an object")
            continue
        wid = witness.get("id")
        if not isinstance(wid, str) or not wid:
            errors.append("witness id must be a nonempty string")
            continue
        if wid in seen:
            errors.append(f"duplicate witness id: {wid}")
        seen.add(wid)
        for key in required_bool:
            if type(witness.get(key)) is not bool:
                errors.append(f"{wid}: {key} must be Boolean")
        expected = witness.get("expected_sufficient_for_accountability")
        if type(expected) is bool and sufficient(witness) != expected:
            errors.append(
                f"{wid}: accountability sufficiency expected {expected}, got {sufficient(witness)}"
            )

    by_id = {
        w["id"]: w
        for w in witnesses
        if isinstance(w, dict) and isinstance(w.get("id"), str)
    }
    selective = by_id.get("PRIV-01")
    total = by_id.get("PRIV-02")
    if selective is None or total is None:
        errors.append("PRIV-01 and PRIV-02 are required controls")
    else:
        if accountability_view(selective) != accountability_view(total):
            errors.append("selective and total disclosure must have identical accountability views")
        if selective.get("private_interior_exposed") is not False:
            errors.append("PRIV-01 must preserve private interior")
        if total.get("private_interior_exposed") is not True:
            errors.append("PRIV-02 must expose private interior")
        if not sufficient(selective) or not sufficient(total):
            errors.append("both controls must be sufficient under the declared finite rule")

    relation = doc.get("expected_relation") if isinstance(doc, dict) else None
    if not isinstance(relation, dict):
        errors.append("expected_relation must be an object")
    else:
        if relation.get("same_accountability_view") is not True:
            errors.append("expected relation must require same accountability view")
        if relation.get("different_private_exposure") is not True:
            errors.append("expected relation must require different private exposure")
        if relation.get("principle") != "minimum sufficient disclosure":
            errors.append("expected relation must name minimum sufficient disclosure")

    if errors:
        print("PRIVACY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "PRIVACY CHECK: PASS — selective and total disclosure preserve the same "
        "finite accountability view while differing on private-interior exposure"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
