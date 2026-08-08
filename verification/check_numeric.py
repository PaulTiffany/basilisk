#!/usr/bin/env python3
"""Compare live NumPy witnesses against the committed expected evidence."""

from __future__ import annotations

import json
from pathlib import Path

from numeric_witness import main_data

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "verification" / "EXPECTED_NUMERIC.json"


def main() -> int:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    actual = main_data()
    if actual != expected:
        print("NUMERIC WITNESS CHECK: FAIL")
        print("EXPECTED:")
        print(json.dumps(expected, indent=2, sort_keys=True))
        print("ACTUAL:")
        print(json.dumps(actual, indent=2, sort_keys=True))
        return 1
    print("NUMERIC WITNESS CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
