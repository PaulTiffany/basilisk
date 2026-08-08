#!/usr/bin/env python3
"""Check the pre-collapse standing-authority projection against live Python."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from map_lb.controller import assess_action
from map_lb.types import ActionIntent, RiskLevel, StandingAuthority
from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VECTORS = ROOT / "verification" / "authority_vectors.json"


def _risk(value: str) -> RiskLevel:
    return RiskLevel[value.upper()]


def _parse_instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _intent(case: dict) -> ActionIntent:
    return ActionIntent(
        action_id=case["id"],
        action_class=case["action_class"],
        description=case["id"],
        current_turn_explicit_authorization=case["current_turn_explicit_authorization"],
        affects_external_system=case["affects_external_system"],
        audience_change=case["audience_change"],
        privacy_change=case["privacy_change"],
        authority_expansion=case["authority_expansion"],
        scope=_risk(case["scope"]),
    )


def _authority(raw: dict) -> StandingAuthority:
    return StandingAuthority(
        authority_id="authority-vector",
        allowed_actions=tuple(raw["allowed_actions"]),
        max_scope=_risk(raw["max_scope"]),
        allow_external_write=raw["allow_external_write"],
        allow_audience_change=raw["allow_audience_change"],
        allow_privacy_change=raw["allow_privacy_change"],
        allow_authority_expansion=raw["allow_authority_expansion"],
        active=raw["active"],
        expires_at=raw["expires_at"],
    )


def main() -> int:
    doc = strict_load_json(VECTORS)
    cases = doc.get("cases", [])
    errors: list[str] = []
    seen: set[str] = set()

    if doc.get("schema_version") != 1:
        errors.append(f"unsupported schema_version {doc.get('schema_version')!r}")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        cases = []

    try:
        evaluation_time = _parse_instant(doc["evaluation_time"])
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"invalid evaluation_time: {exc}")
        evaluation_time = datetime(1970, 1, 1, tzinfo=timezone.utc)

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{index}] must be an object")
            continue
        cid = case.get("id", "<missing>")
        if cid in seen:
            errors.append(f"duplicate case id: {cid}")
            continue
        seen.add(cid)
        try:
            intent = _intent(case)
            authority = _authority(case["authority"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{cid}: malformed vector: {exc}")
            continue

        covers = authority.covers(intent, now=evaluation_time)
        authorized = intent.current_turn_explicit_authorization or covers
        assessment = assess_action(intent, authority, now=evaluation_time)

        if covers != case.get("expected_covers"):
            errors.append(
                f"{cid}: covers expected {case.get('expected_covers')!r}, got {covers!r}"
            )
        if authorized != case.get("expected_authorized"):
            errors.append(
                f"{cid}: authorized expected {case.get('expected_authorized')!r}, got {authorized!r}"
            )
        if assessment.gate.label() != case.get("expected_gate"):
            errors.append(
                f"{cid}: gate expected {case.get('expected_gate')!r}, got {assessment.gate.label()!r}"
            )

    required_prefixes = {
        "A02-inactive",
        "A03-expired",
        "A04-wrong-action-class",
        "A05-over-scope",
        "A06-external-permission-missing",
        "A07-audience-permission-missing",
        "A08-privacy-permission-missing",
        "A09-expansion-permission-missing",
        "A11-current-turn-overrides-standing-miss",
        "A12-standing-not-fresh-high-scope",
    }
    missing = required_prefixes - seen
    if missing:
        errors.append(f"required authority surfaces missing: {sorted(missing)}")

    if errors:
        print("AUTHORITY VECTOR CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"AUTHORITY VECTOR CHECK: PASS — {len(cases)} structured authority vectors "
        f"at {evaluation_time.isoformat()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
