#!/usr/bin/env python3
"""Generate the canonical exhaustive GateProjection artifact from the live gate law."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.gate_projection import GateProjection, gate_from_projection  # noqa: E402

OUTPUT = ROOT / "verification" / "gate_projection_exhaustive.json"
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
GATE_CODE = {"proceed": 0, "proceed_and_report": 1, "checkpoint": 2, "stop": 3}


def projection(mask: int) -> GateProjection:
    values = {field: bool((mask >> index) & 1) for index, field in enumerate(FIELDS)}
    return GateProjection(**values)


def canonical_document() -> dict[str, object]:
    labels = [gate_from_projection(projection(mask)).label() for mask in range(1 << len(FIELDS))]
    counts = Counter(labels)
    return {
        "schema_version": 1,
        "bit_order_lsb_first": FIELDS,
        "gate_code": GATE_CODE,
        "state_count": 1 << len(FIELDS),
        "expected_counts": {label: counts[label] for label in GATE_CODE},
        "gate_codes": [GATE_CODE[label] for label in labels],
    }


def canonical_text() -> str:
    return json.dumps(canonical_document(), separators=(",", ":"), ensure_ascii=False) + "\n"


def main() -> int:
    OUTPUT.write_text(canonical_text(), encoding="utf-8")
    print(f"GATE PROJECTION GENERATOR: wrote {1 << len(FIELDS)} states to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
