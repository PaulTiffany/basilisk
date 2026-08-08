#!/usr/bin/env python3
"""Check the finite observability/accountability witness surface."""

from __future__ import annotations

from pathlib import Path

from registry_io import strict_load_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "verification" / "observability_witnesses.json"


def explanatory_accountability_needed(frame: dict[str, object]) -> bool:
    return bool(frame["external_observable"]) and not bool(frame["relevant_interior_observable"])


def main() -> int:
    doc = strict_load_json(SPEC)
    errors: list[str] = []
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        errors.append("observability registry must be a schema_version 1 object")
        witnesses = []
    else:
        witnesses = doc.get("witnesses", [])
        if not isinstance(witnesses, list):
            errors.append("witnesses must be a list")
            witnesses = []

    seen: set[str] = set()
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
        frame = witness.get("frame")
        if not isinstance(frame, dict):
            errors.append(f"{wid}: frame must be an object")
            continue
        for key in (
            "external_observable",
            "relevant_interior_observable",
            "authority_trace_observable",
            "provenance_observable",
        ):
            if type(frame.get(key)) is not bool:
                errors.append(f"{wid}: frame.{key} must be Boolean")
        if type(witness.get("authorized")) is not bool:
            errors.append(f"{wid}: authorized must be Boolean")
        expected = witness.get("expected_explanatory_accountability_needed")
        if type(expected) is not bool:
            errors.append(f"{wid}: expected accountability value must be Boolean")
            continue
        actual = explanatory_accountability_needed(frame)
        if actual != expected:
            errors.append(f"{wid}: accountability expected {expected}, got {actual}")

    by_id = {w["id"]: w for w in witnesses if isinstance(w, dict) and isinstance(w.get("id"), str)}
    if "OBS-01" in by_id:
        f = by_id["OBS-01"]["frame"]
        if not (f["external_observable"] and not f["relevant_interior_observable"]):
            errors.append("OBS-01 must witness visible output with opaque relevant interior")
    if "OBS-03" in by_id:
        w = by_id["OBS-03"]
        f = w["frame"]
        if not (f["relevant_interior_observable"] and not w["authorized"]):
            errors.append("OBS-03 must witness interpretability without authorization")

    if errors:
        print("OBSERVABILITY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "OBSERVABILITY CHECK: PASS — "
        f"{len(witnesses)} finite witnesses preserve external/internal observability and authority distinctions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
