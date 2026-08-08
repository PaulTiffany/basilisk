#!/usr/bin/env python3
"""Check diagnostic observables on registered pairwise interaction seams."""

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

COVERAGE = ROOT / "verification" / "interaction_coverage.json"
DIAGNOSTICS = ROOT / "verification" / "interaction_diagnostics.json"


def standing_authority() -> StandingAuthority:
    return StandingAuthority(
        authority_id="interaction-diagnostics-standing",
        allowed_actions=("interaction",),
        max_scope=RiskLevel.CRITICAL,
        allow_external_write=True,
        allow_audience_change=True,
        allow_privacy_change=True,
        allow_authority_expansion=True,
    )


def state_for(defaults: dict, square: dict, corner: str) -> dict:
    if corner not in {"00", "10", "01", "11"}:
        raise ValueError(f"unknown corner {corner!r}")
    state = {**defaults, **square.get("base", {})}
    bits = (corner[0] == "1", corner[1] == "1")
    for factor, on in zip(square["factors"], bits, strict=True):
        state[factor["field"]] = factor["on"] if on else factor["off"]
    return state


def assess(label: str, state: dict):
    payload = {
        "action_id": label,
        "action_class": "interaction",
        "description": "Pairwise interaction diagnostic witness.",
        **{k: v for k, v in state.items() if k != "standing_authorized"},
        "tags": ["interaction-diagnostics"],
    }
    intent = ActionIntent.from_dict(payload)
    authority = standing_authority() if state["standing_authorized"] else None
    return assess_action(intent, authority)


def main() -> int:
    errors: list[str] = []
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    diagnostics = json.loads(DIAGNOSTICS.read_text(encoding="utf-8"))
    if diagnostics.get("schema_version") != 1:
        errors.append(f"unsupported diagnostic schema_version: {diagnostics.get('schema_version')!r}")

    defaults = coverage["defaults"]
    square_by_id = {square["id"]: square for square in coverage["squares"]}
    assertions = diagnostics.get("assertions", [])
    ids = [item.get("id") for item in assertions]
    if len(ids) != len(set(ids)):
        errors.append("duplicate interaction diagnostic assertion IDs")

    covered_squares: set[str] = set()
    for item in assertions:
        aid = item.get("id", "<missing>")
        square_id = item.get("square")
        square = square_by_id.get(square_id)
        if square is None:
            errors.append(f"{aid}: unknown interaction square {square_id}")
            continue
        covered_squares.add(square_id)
        try:
            state = state_for(defaults, square, item.get("corner"))
        except (TypeError, ValueError) as exc:
            errors.append(f"{aid}: malformed corner: {exc}")
            continue
        result = assess(aid, state)
        reasons = set(result.reasons)

        for reason in item.get("reason_contains", []):
            if reason not in reasons:
                errors.append(f"{aid}: missing diagnostic reason {reason!r}")
        for reason in item.get("reason_excludes", []):
            if reason in reasons:
                errors.append(f"{aid}: forbidden diagnostic reason present {reason!r}")
        if "authority_basis" in item and result.authority_basis != item["authority_basis"]:
            errors.append(
                f"{aid}: authority_basis expected {item['authority_basis']!r}, got {result.authority_basis!r}"
            )
        if "report_required" in item and result.report_required is not item["report_required"]:
            errors.append(
                f"{aid}: report_required expected {item['report_required']!r}, got {result.report_required!r}"
            )
        if "risk_score" in item and result.risk_score != item["risk_score"]:
            errors.append(f"{aid}: risk_score expected {item['risk_score']}, got {result.risk_score}")

    required_diagnostic_squares = {
        "IX01-audience-privacy",
        "IX02-external-standing",
        "IX03-authority-fresh",
        "IX05-hard-boundary-fresh",
        "IX08-critical-uncertainty-fresh",
        "IX09-rollback-inspectability",
        "IX10-destructive-external-standing",
    }
    missing = required_diagnostic_squares - covered_squares
    if missing:
        errors.append(f"diagnostic interaction surface missing squares: {sorted(missing)}")

    if errors:
        print("INTERACTION DIAGNOSTIC CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "INTERACTION DIAGNOSTIC CHECK: PASS — "
        f"{len(assertions)} diagnostic assertions across {len(covered_squares)} interaction squares"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
