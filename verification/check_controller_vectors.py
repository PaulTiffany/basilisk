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

BOOL_FIELDS = {
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
    "judgment_requested",
    "concrete_immediate_safety_risk",
    "destructive",
    "standing_authorized",
}
RISK_VALUES = {"low", "moderate", "high", "critical"}
JUDGMENT_VALUES = {
    "none",
    "user_supplied",
    "sourced_external",
    "explicit_model_recommendation",
    "narrow_safety",
}
GATE_VALUES = {"proceed", "proceed_and_report", "checkpoint", "stop"}
REQUIRED_FIELDS = BOOL_FIELDS | {
    "id", "scope", "uncertainty", "judgment_mode", "expected_gate"
}


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


def validate_case(case: dict, index: int) -> list[str]:
    errors: list[str] = []
    cid = case.get("id", f"case[{index}]")
    missing = sorted(REQUIRED_FIELDS - set(case))
    extra = sorted(set(case) - REQUIRED_FIELDS)
    if missing:
        errors.append(f"{cid}: missing fields {missing}")
    if extra:
        errors.append(f"{cid}: unexpected fields {extra}")
    if not isinstance(case.get("id"), str) or not case.get("id", "").strip():
        errors.append(f"case[{index}]: id must be a non-empty string")
    for field in BOOL_FIELDS:
        if field in case and type(case[field]) is not bool:
            errors.append(f"{cid}: {field} must be Boolean")
    if case.get("scope") not in RISK_VALUES:
        errors.append(f"{cid}: invalid scope {case.get('scope')!r}")
    if case.get("uncertainty") not in RISK_VALUES:
        errors.append(f"{cid}: invalid uncertainty {case.get('uncertainty')!r}")
    if case.get("judgment_mode") not in JUDGMENT_VALUES:
        errors.append(f"{cid}: invalid judgment_mode {case.get('judgment_mode')!r}")
    if case.get("expected_gate") not in GATE_VALUES:
        errors.append(f"{cid}: invalid expected_gate {case.get('expected_gate')!r}")
    return errors


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
    if doc.get("schema_version") != 1:
        failures.append(f"unsupported schema_version: {doc.get('schema_version')!r}")
    cases = doc.get("cases")
    if not isinstance(cases, list) or not cases:
        failures.append("cases must be a non-empty list")
        cases = []

    ids: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            failures.append(f"case[{index}] must be an object")
            continue
        failures.extend(validate_case(case, index))
        if isinstance(case.get("id"), str):
            ids.append(case["id"])
    if len(ids) != len(set(ids)):
        failures.append("controller vector IDs must be unique")

    if failures:
        print("CONTROLLER VECTOR CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    standing = standing_authority()
    for case in cases:
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
