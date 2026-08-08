#!/usr/bin/env python3
"""Check the finite distinction between nominal availability and viable refusal."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "verification" / "evitability_witnesses.json"


def nominally_preserves(before: dict, after: dict, embodiments: list[str]) -> bool:
    return all(not before["available"][e] or after["available"][e] for e in embodiments)


def preserves_evitability(before: dict, after: dict, embodiments: list[str]) -> bool:
    return all(not before["viable"][e] or after["viable"][e] for e in embodiments)


def main() -> int:
    doc = json.loads(PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    if doc.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    embodiments = doc.get("embodiments", [])
    if not isinstance(embodiments, list) or not embodiments:
        errors.append("embodiments must be a nonempty list")
        embodiments = []

    seen: set[str] = set()
    for case in doc.get("cases", []):
        cid = case.get("id", "<missing>")
        if cid in seen:
            errors.append(f"duplicate case id {cid}")
        seen.add(cid)
        before = case.get("before", {})
        after = case.get("after", {})
        for phase_name, phase in (("before", before), ("after", after)):
            for field in ("available", "viable"):
                mapping = phase.get(field, {})
                if set(mapping) != set(embodiments):
                    errors.append(f"{cid}: {phase_name}.{field} does not cover exact embodiment set")
                if any(not isinstance(v, bool) for v in mapping.values()):
                    errors.append(f"{cid}: {phase_name}.{field} values must be booleans")

        nominal = nominally_preserves(before, after, embodiments)
        viable = preserves_evitability(before, after, embodiments)
        if nominal != case.get("expect_nominal_preservation"):
            errors.append(f"{cid}: nominal preservation expectation mismatch")
        if viable != case.get("expect_evitability_preservation"):
            errors.append(f"{cid}: evitability preservation expectation mismatch")

    by_id = {case.get("id"): case for case in doc.get("cases", [])}
    witness = by_id.get("EV-001")
    control = by_id.get("EV-002")
    if witness is None or control is None:
        errors.append("required EV-001 witness and EV-002 control must both be present")
    else:
        if not nominally_preserves(witness["before"], witness["after"], embodiments):
            errors.append("EV-001 must preserve nominal availability")
        if preserves_evitability(witness["before"], witness["after"], embodiments):
            errors.append("EV-001 must lose viability for at least one previously viable embodiment")
        if not preserves_evitability(control["before"], control["after"], embodiments):
            errors.append("EV-002 identity control must preserve viability")

    if errors:
        print("EVITABILITY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"EVITABILITY CHECK: PASS — {len(seen)} finite cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
