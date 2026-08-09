#!/usr/bin/env python3
"""Verify the stored exhaustive gate table is exact canonical output of the live law."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
VERIFICATION = ROOT / "verification"
if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))

from generate_gate_projection_exhaustive import canonical_document  # noqa: E402
from registry_io import strict_load_json  # noqa: E402

ARTIFACT = VERIFICATION / "gate_projection_exhaustive.json"


def main() -> int:
    errors: list[str] = []
    try:
        observed = strict_load_json(ARTIFACT)
    except Exception as exc:
        print("GATE PROJECTION EXHAUSTIVE CHECK: FAIL")
        print(f"- malformed strict JSON: {exc}")
        return 1

    expected = canonical_document()
    if not isinstance(observed, dict):
        errors.append("artifact root must be an object")
    else:
        if set(observed) != set(expected):
            missing = sorted(set(expected) - set(observed))
            extra = sorted(set(observed) - set(expected))
            if missing:
                errors.append(f"missing canonical fields: {missing}")
            if extra:
                errors.append(f"unexpected fields: {extra}")
        for field in ("schema_version", "bit_order_lsb_first", "gate_code", "state_count", "expected_counts"):
            if observed.get(field) != expected[field]:
                errors.append(f"{field} differs from live-law regeneration")

        codes = observed.get("gate_codes")
        expected_codes = expected["gate_codes"]
        if not isinstance(codes, list):
            errors.append("gate_codes must be a list")
        elif len(codes) != len(expected_codes):
            errors.append(f"gate_codes length expected {len(expected_codes)}, got {len(codes)}")
        else:
            mismatches = [i for i, (actual, wanted) in enumerate(zip(codes, expected_codes)) if actual != wanted]
            if mismatches:
                preview = mismatches[:8]
                errors.append(f"gate_codes differ from live law at state indices {preview}" + (" ..." if len(mismatches) > len(preview) else ""))

    if errors:
        print("GATE PROJECTION EXHAUSTIVE CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("GATE PROJECTION EXHAUSTIVE CHECK: PASS — stored 2^11 table exactly matches live gate law")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
