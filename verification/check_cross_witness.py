#!/usr/bin/env python3
"""Check that every shared controller vector is transcribed into Lean.

This does not prove the Lean proposition; `lake build` does that. It verifies
that the JSON observable contract and the concrete Lean vector proposition are
mechanically aligned rather than merely maintained by prose convention.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
VECTORS = ROOT / "verification" / "controller_vectors.json"
LEAN = ROOT / "formal" / "Basilisk" / "ControllerVectors.lean"

BOOL_FIELDS = [
    "within_contract",
    "hard_boundary_violation",
    "current_turn_explicit_authorization",
    "reversible",
    "rollback_available",
    "inspectable",
    "material_change",
    "affects_external_system",
    "audience_change",
    "privacy_change",
    "authority_expansion",
]
TAIL_BOOL_FIELDS = [
    "judgment_requested",
    "concrete_immediate_safety_risk",
    "destructive",
]

RISK = {
    "low": ".low",
    "moderate": ".moderate",
    "high": ".high",
    "critical": ".critical",
}
JUDGMENT = {
    "none": ".none",
    "user_supplied": ".userSupplied",
    "sourced_external": ".sourcedExternal",
    "explicit_model_recommendation": ".explicitModelRecommendation",
    "narrow_safety": ".narrowSafety",
}
GATE = {
    "proceed": ".proceed",
    "proceed_and_report": ".proceedAndReport",
    "checkpoint": ".checkpoint",
    "stop": ".stop",
}


def b(value: bool) -> str:
    return "true" if value else "false"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def lean_expression(case: dict) -> str:
    fields = [b(case[name]) for name in BOOL_FIELDS]
    fields += [RISK[case["scope"]], RISK[case["uncertainty"]], JUDGMENT[case["judgment_mode"]]]
    fields += [b(case[name]) for name in TAIL_BOOL_FIELDS]
    authorized = case["current_turn_explicit_authorization"] or case["standing_authorized"]
    return (
        f"(vIntent {' '.join(fields)}).assess {b(authorized)} = "
        f"{GATE[case['expected_gate']]}"
    )


def main() -> int:
    doc = json.loads(VECTORS.read_text(encoding="utf-8"))
    lean = norm(LEAN.read_text(encoding="utf-8"))
    failures: list[str] = []

    cases = doc.get("cases", [])
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        failures.append("duplicate vector IDs")

    for case in cases:
        expected = norm(lean_expression(case))
        if expected not in lean:
            failures.append(
                f"{case['id']}: expected Lean transcription missing: {expected}"
            )

    declaration = "theorem controller_vectors_hold : controllerVectorsProp := by"
    if declaration not in lean:
        failures.append("aggregate Lean vector theorem declaration is missing or changed")

    if failures:
        print("CROSS-WITNESS TRANSCRIPTION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"CROSS-WITNESS TRANSCRIPTION CHECK: PASS — {len(cases)} JSON↔Lean vectors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
