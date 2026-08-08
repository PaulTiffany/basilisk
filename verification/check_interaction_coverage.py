#!/usr/bin/env python3
"""Check pairwise interaction seams on the declared controller exterior.

Each seam is a complete 2x2 square over two factors. The checker verifies that:
- the square is well-formed and varies exactly the declared factors;
- all four corners are distinct in the intended coordinates;
- the live Python controller returns the registered gate at every corner;
- every required seam class remains represented.

This is pairwise exterior coverage, not exhaustive combinatorial coverage.
"""

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

SPEC = ROOT / "verification" / "interaction_coverage.json"


def standing_authority() -> StandingAuthority:
    return StandingAuthority(
        authority_id="interaction-standing",
        allowed_actions=("interaction",),
        max_scope=RiskLevel.CRITICAL,
        allow_external_write=True,
        allow_audience_change=True,
        allow_privacy_change=True,
        allow_authority_expansion=True,
    )


def intent_from_state(label: str, state: dict) -> ActionIntent:
    payload = {
        "action_id": label,
        "action_class": "interaction",
        "description": "Pairwise exterior interaction witness.",
        **{k: v for k, v in state.items() if k != "standing_authorized"},
        "tags": ["interaction-coverage"],
    }
    return ActionIntent.from_dict(payload)


def gate_for(label: str, state: dict) -> str:
    authority = standing_authority() if state["standing_authorized"] else None
    return assess_action(intent_from_state(label, state), authority).gate.label()


def corner(defaults: dict, square: dict, a_on: bool, b_on: bool) -> dict:
    factors = square["factors"]
    state = {**defaults, **square.get("base", {})}
    for factor, on in zip(factors, (a_on, b_on), strict=True):
        state[factor["field"]] = factor["on"] if on else factor["off"]
    return state


def main() -> int:
    errors: list[str] = []
    doc = json.loads(SPEC.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        errors.append(f"unsupported interaction schema_version: {doc.get('schema_version')!r}")

    defaults = doc.get("defaults", {})
    required_classes = set(doc.get("required_seam_classes", []))
    squares = doc.get("squares", [])
    ids = [square.get("id") for square in squares]
    if len(ids) != len(set(ids)):
        errors.append("duplicate interaction square IDs")

    observed_classes: set[str] = set()
    expected_corner_keys = {"00", "10", "01", "11"}

    for square in squares:
        sid = square.get("id", "<missing>")
        seam_class = square.get("class")
        if seam_class not in required_classes:
            errors.append(f"{sid}: undeclared seam class {seam_class!r}")
        else:
            observed_classes.add(seam_class)

        factors = square.get("factors", [])
        if not isinstance(factors, list) or len(factors) != 2:
            errors.append(f"{sid}: each interaction square must declare exactly two factors")
            continue
        fields = [factor.get("field") for factor in factors]
        if len(set(fields)) != 2 or any(not field for field in fields):
            errors.append(f"{sid}: interaction factors must name two distinct fields")
        for factor in factors:
            if factor.get("off") == factor.get("on"):
                errors.append(f"{sid}: factor {factor.get('field')} has identical off/on values")

        expected = square.get("expected", {})
        if set(expected) != expected_corner_keys:
            errors.append(f"{sid}: expected must define exactly corners {sorted(expected_corner_keys)}")
            continue
        if not str(square.get("interpretation", "")).strip():
            errors.append(f"{sid}: missing interaction interpretation")

        states = {
            "00": corner(defaults, square, False, False),
            "10": corner(defaults, square, True, False),
            "01": corner(defaults, square, False, True),
            "11": corner(defaults, square, True, True),
        }

        # Project the four states onto only the declared factor coordinates. They
        # must realize all four combinations exactly once.
        projected = {
            key: tuple(state[field] for field in fields)
            for key, state in states.items()
        }
        if len(set(projected.values())) != 4:
            errors.append(f"{sid}: interaction square does not realize four distinct factor corners")

        # Base/context must be invariant away from the two factor fields.
        nonfactor_keys = set(defaults) - set(fields)
        baseline = states["00"]
        for key, state in states.items():
            changed_elsewhere = {
                field for field in nonfactor_keys if state[field] != baseline[field]
            }
            if changed_elsewhere:
                errors.append(
                    f"{sid}:{key}: square changes non-factor coordinates {sorted(changed_elsewhere)}"
                )

        for key, state in states.items():
            actual = gate_for(f"{sid}:{key}", state)
            if actual != expected[key]:
                errors.append(f"{sid}:{key}: expected {expected[key]}, got {actual}")

    missing_classes = required_classes - observed_classes
    if missing_classes:
        errors.append(f"interaction exterior missing seam classes: {sorted(missing_classes)}")

    if errors:
        print("INTERACTION COVERAGE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "INTERACTION COVERAGE CHECK: PASS — "
        f"{len(squares)} complete 2x2 seams across {len(required_classes)} seam classes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
