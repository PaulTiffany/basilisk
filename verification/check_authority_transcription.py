#!/usr/bin/env python3
"""Require exact JSON→Lean transcription of structured authority vectors."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from registry_io import strict_load_json

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
VECTORS = ROOT / "verification" / "authority_vectors.json"
LEAN = ROOT / "formal" / "Basilisk" / "AuthorityVectors.lean"
BEGIN = "-- BEGIN GENERATED AUTHORITY VECTORS"
END = "-- END GENERATED AUTHORITY VECTORS"

RISK = {
    "low": ".low",
    "moderate": ".moderate",
    "high": ".high",
    "critical": ".critical",
}
GATE = {
    "proceed": ".proceed",
    "proceed_and_report": ".proceedAndReport",
    "checkpoint": ".checkpoint",
    "stop": ".stop",
}


def _bool(value: bool) -> str:
    if type(value) is not bool:
        raise ValueError(f"expected bool, got {value!r}")
    return "true" if value else "false"


def _string(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"expected string, got {value!r}")
    return json.dumps(value, ensure_ascii=False)


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _expired(expires_at: object, evaluation_time: datetime) -> bool:
    if expires_at is None:
        return False
    if not isinstance(expires_at, str):
        raise ValueError(f"expires_at must be string or null, got {expires_at!r}")
    try:
        expires = _instant(expires_at)
    except ValueError:
        return True
    return evaluation_time >= expires


def _risk(value: object) -> str:
    if value not in RISK:
        raise ValueError(f"unknown risk value: {value!r}")
    return RISK[str(value)]


def _gate(value: object) -> str:
    if value not in GATE:
        raise ValueError(f"unknown gate value: {value!r}")
    return GATE[str(value)]


def render_generated_block(doc: dict) -> str:
    evaluation_time = _instant(doc["evaluation_time"])
    cases = doc["cases"]
    if not isinstance(cases, list):
        raise ValueError("cases must be a list")

    lines = [BEGIN, "def authorityVectors : List AuthorityVector := ["]
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"cases[{index}] must be an object")
        auth = case["authority"]
        if not isinstance(auth, dict):
            raise ValueError(f"{case.get('id', index)}: authority must be an object")
        allowed = auth["allowed_actions"]
        if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
            raise ValueError(f"{case.get('id', index)}: allowed_actions must be string list")
        allowed_lean = "[" + ", ".join(_string(x) for x in allowed) + "]"
        expired = _expired(auth["expires_at"], evaluation_time)

        line = (
            "  { id := " + _string(case["id"])
            + ", intent := { baseAuthorityIntent with currentTurnExplicitAuthorization := "
            + _bool(case["current_turn_explicit_authorization"])
            + ", affectsExternalSystem := " + _bool(case["affects_external_system"])
            + ", audienceChange := " + _bool(case["audience_change"])
            + ", privacyChange := " + _bool(case["privacy_change"])
            + ", authorityExpansion := " + _bool(case["authority_expansion"])
            + ", scope := " + _risk(case["scope"])
            + " }, actionClass := " + _string(case["action_class"])
            + ", authority := { allowedActions := " + allowed_lean
            + ", maxScope := " + _risk(auth["max_scope"])
            + ", allowExternalWrite := " + _bool(auth["allow_external_write"])
            + ", allowAudienceChange := " + _bool(auth["allow_audience_change"])
            + ", allowPrivacyChange := " + _bool(auth["allow_privacy_change"])
            + ", allowAuthorityExpansion := " + _bool(auth["allow_authority_expansion"])
            + ", active := " + _bool(auth["active"])
            + ", expired := " + _bool(expired)
            + " }, expectedCovers := " + _bool(case["expected_covers"])
            + ", expectedAuthorized := " + _bool(case["expected_authorized"])
            + ", expectedGate := " + _gate(case["expected_gate"])
            + " }"
        )
        if index != len(cases) - 1:
            line += ","
        lines.append(line)
    lines.extend(["]", END])
    return "\n".join(lines)


def extract_generated_block(text: str) -> str:
    start = text.find(BEGIN)
    end = text.find(END)
    if start < 0 or end < 0 or end < start:
        raise ValueError("AuthorityVectors.lean lacks unique generated markers")
    if text.find(BEGIN, start + len(BEGIN)) >= 0 or text.find(END, end + len(END)) >= 0:
        raise ValueError("AuthorityVectors.lean contains duplicate generated markers")
    return text[start : end + len(END)]


def main() -> int:
    errors: list[str] = []
    try:
        doc = strict_load_json(VECTORS)
        if not isinstance(doc, dict) or doc.get("schema_version") != 1:
            raise ValueError("authority vector registry must be schema_version 1 object")
        expected = render_generated_block(doc)
        actual = extract_generated_block(LEAN.read_text(encoding="utf-8"))
        if actual != expected:
            errors.append("generated authority Lean block drifted from authority_vectors.json")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))

    if errors:
        print("AUTHORITY TRANSCRIPTION CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    count = len(doc["cases"])
    print(f"AUTHORITY TRANSCRIPTION CHECK: PASS — {count} JSON↔Lean structured authority vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
