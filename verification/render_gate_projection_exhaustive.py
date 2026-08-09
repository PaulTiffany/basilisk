#!/usr/bin/env python3
"""Render/check the exhaustive 11-bit GateProjection table deterministically.

The exhaustive table is a derived artifact, not repository source state. CI
recomputes and checks the full 2,048-state law; an operator may still render the
JSON on demand for inspection without requiring the generated blob to be
committed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.gate_projection import GateProjection, gate_from_projection  # noqa: E402

TARGET = ROOT / "verification" / "gate_projection_exhaustive.json"
FIELDS = [
    "hard_boundary_violation",
    "within_contract",
    "unrequested_model_judgment",
    "critical_destructive",
    "current_turn_explicit_authorization",
    "boundary_crossing",
    "authorized",
    "high_scope",
    "critical_uncertainty",
    "material_change",
    "risk_score_at_least_report",
]
GATE_CODE = {
    "proceed": 0,
    "proceed_and_report": 1,
    "checkpoint": 2,
    "stop": 3,
}


def projection(mask: int) -> GateProjection:
    return GateProjection(
        **{field: bool((mask >> index) & 1) for index, field in enumerate(FIELDS)}
    )


def build_doc() -> dict[str, object]:
    labels = [
        gate_from_projection(projection(mask)).label()
        for mask in range(1 << len(FIELDS))
    ]
    counts = Counter(labels)
    return {
        "schema_version": 1,
        "bit_order_lsb_first": FIELDS,
        "gate_code": GATE_CODE,
        "state_count": 1 << len(FIELDS),
        "expected_counts": {
            label: counts[label]
            for label in ("proceed", "proceed_and_report", "checkpoint", "stop")
        },
        "gate_codes": [GATE_CODE[label] for label in labels],
    }


def canonical_text(doc: dict[str, object]) -> str:
    return json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n"


def check() -> int:
    expected = build_doc()
    repeated = build_doc()
    raw = canonical_text(expected)
    round_trip = json.loads(raw)
    codes = expected["gate_codes"]
    counts = Counter(codes)
    encoded_counts = expected["expected_counts"]

    errors: list[str] = []
    if repeated != expected:
        errors.append("repeated exhaustive traversal is not deterministic")
    if round_trip != expected:
        errors.append("canonical serialization does not round-trip")
    if expected["state_count"] != 1 << len(FIELDS):
        errors.append("state_count disagrees with projection width")
    if len(codes) != expected["state_count"]:
        errors.append("gate code table length disagrees with state_count")
    for label, code in GATE_CODE.items():
        if counts[code] != encoded_counts[label]:
            errors.append(f"count mismatch for {label}")

    if errors:
        print("GATE PROJECTION EXHAUSTIVE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "GATE PROJECTION EXHAUSTIVE CHECK: PASS — "
        f"{expected['state_count']} states recomputed; "
        f"proceed={encoded_counts['proceed']}, "
        f"proceed_and_report={encoded_counts['proceed_and_report']}, "
        f"checkpoint={encoded_counts['checkpoint']}, stop={encoded_counts['stop']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    TARGET.write_text(canonical_text(build_doc()), encoding="utf-8")
    print(f"rendered derived artifact {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
