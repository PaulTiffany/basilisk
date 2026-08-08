#!/usr/bin/env python3
"""Check finite shared-obstruction and recursive materialization witnesses."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.materiality import (  # noqa: E402
    MaterialEncounter,
    WorldTransition,
    assess_recursive_materialization,
    assess_shared_obstruction,
)

SPEC = ROOT / "verification" / "materiality_witnesses.json"


def encounter(data: dict) -> MaterialEncounter:
    return MaterialEncounter(**data)


def transition(data: dict) -> WorldTransition:
    return WorldTransition(**data)


def main() -> int:
    errors: list[str] = []
    doc = json.loads(SPEC.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        errors.append(f"unsupported materiality schema_version: {doc.get('schema_version')!r}")

    cases = doc.get("cases", [])
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("duplicate materiality witness IDs")

    seen_kinds: set[str] = set()
    for case in cases:
        cid = case.get("id", "<missing>")
        kind = case.get("kind")
        seen_kinds.add(kind)
        expected = case.get("expected")
        if not isinstance(expected, bool):
            errors.append(f"{cid}: expected must be Boolean")
            continue

        if kind == "shared_obstruction":
            result = assess_shared_obstruction(tuple(encounter(x) for x in case.get("encounters", [])))
            actual = result.shared_obstruction
        elif kind == "recursive_materialization":
            result = assess_recursive_materialization(
                transition(case["transition"]),
                tuple(encounter(x) for x in case.get("later_encounters", [])),
            )
            actual = result.recursive_materialization
        else:
            errors.append(f"{cid}: unknown witness kind {kind!r}")
            continue

        if actual is not expected:
            errors.append(f"{cid}: expected {expected}, got {actual}")

    required = {"shared_obstruction", "recursive_materialization"}
    missing = required - seen_kinds
    if missing:
        errors.append(f"materiality witness corpus missing kinds: {sorted(missing)}")

    # Negative-control discipline: shared belief without obstruction must remain false.
    belief = next((case for case in cases if case.get("id") == "MW02-shared-belief-only"), None)
    if belief is None or belief.get("expected") is not False:
        errors.append("shared-belief negative control missing or no longer negative")

    if errors:
        print("MATERIALITY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "MATERIALITY CHECK: PASS — "
        f"{len(cases)} finite witnesses distinguish shared obstruction, belief-only agreement, and recursive materialization"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
