#!/usr/bin/env python3
"""Render/check the exhaustive 11-bit GateProjection table deterministically."""

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
from registry_io import strict_load_json  # noqa: E402

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
    errors: list[str] = []
    try:
        observed = strict_load_json(TARGET)
    except Exception as exc:
        print("GATE PROJECTION EXHAUSTIVE CHECK: FAIL")
        print(f"- stored artifact is not strict JSON: {exc}")
        return 1

    if observed != expected:
        errors.append("stored exhaustive table disagrees with the live 11-bit gate law")
    raw = TARGET.read_text(encoding="utf-8")
    if raw != canonical_text(expected):
        errors.append("stored exhaustive table is not in deterministic canonical serialization")

    if errors:
        print("GATE PROJECTION EXHAUSTIVE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    counts = expected["expected_counts"]
    print(
        "GATE PROJECTION EXHAUSTIVE CHECK: PASS — "
        f"{expected['state_count']} states; "
        f"proceed={counts['proceed']}, "
        f"proceed_and_report={counts['proceed_and_report']}, "
        f"checkpoint={counts['checkpoint']}, stop={counts['stop']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    TARGET.write_text(canonical_text(build_doc()), encoding="utf-8")
    print(f"rendered {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
