#!/usr/bin/env python3
"""Check the real Python controller against shared cross-witness vectors."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.controller import assess_action  # noqa: E402
from map_lb.types import ActionIntent, RiskLevel, StandingAuthority  # noqa: E402

VECTORS = ROOT / "verification" / "controller_vectors.json"


def standing_authority() -> StandingAuthority:
    return StandingAuthority(
        authority_id="cross-witness-standing",
        allowed_actions=("vector",),
        max_scope=RiskLevel.CRITICAL,
        allow_external_write=True,
        allow_audience_change=True,
        allow_privacy_change=True,
        allow_authority_expansion=True,
    )


def intent_from_case(case: dict) -> ActionIntent:
    payload = {
        "action_id": case["id"],
        "action_class": "vector",
        "description": "Shared Python/Lean controller cross-witness vector.",
        "within_contract": case["within_contract"],
        "hard_boundary_violation": case["hard_boundary_violation"],
        "current_turn_explicit_authorization": case["current_turn_explicit_authorization"],
        "reversible": case["reversible"],
        "rollback_available": case["rollback_available"],
        "inspectable": case["inspectable"],
        "material_change": case["material_change"],
        "affects_external_system": case["affects_external_system"],
        "audience_change": case["audience_change"],
        "privacy_change": case["privacy_change"],
        "authority_expansion": case["authority_expansion"],
        "scope": case["scope"],
        "uncertainty": case["uncertainty"],
        "judgment_mode": case["judgment_mode"],
        "judgment_requested": case["judgment_requested"],
        "concrete_immediate_safety_risk": case["concrete_immediate_safety_risk"],
        "destructive": case["destructive"],
        "tags": ["cross-witness"],
    }
    return ActionIntent.from_dict(payload)


def main() -> int:
    doc = json.loads(VECTORS.read_text(encoding="utf-8"))
    failures: list[str] = []
    standing = standing_authority()

    for case in doc.get("cases", []):
        intent = intent_from_case(case)
        authority = standing if case["standing_authorized"] else None
        actual = assess_action(intent, authority).gate.label()
        expected = case["expected_gate"]
        if actual != expected:
            failures.append(f"{case['id']}: expected {expected}, got {actual}")

    if failures:
        print("CONTROLLER VECTOR CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"CONTROLLER VECTOR CHECK: PASS — {len(doc.get('cases', []))} shared vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
