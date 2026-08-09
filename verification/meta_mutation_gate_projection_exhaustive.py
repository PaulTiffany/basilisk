#!/usr/bin/env python3
"""Attack exhaustive gate-table assurance in temporary repository copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_gate_projection_exhaustive.py"


def clone_minimal(dst: Path) -> None:
    shutil.copytree(ROOT / "verification", dst / "verification")
    shutil.copytree(ROOT / "src", dst / "src")


def run_check(temp_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BASILISK_ROOT"] = str(temp_root)
    return subprocess.run(
        [sys.executable, str(CHECKER)],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def corrupt_one_state(root: Path) -> None:
    path = root / "verification" / "gate_projection_exhaustive.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["gate_codes"][2] = 3 if doc["gate_codes"][2] != 3 else 0
    path.write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")


def truncate_table(root: Path) -> None:
    path = root / "verification" / "gate_projection_exhaustive.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["gate_codes"] = doc["gate_codes"][:-1]
    path.write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")


CASES = [
    ("single gate-code corruption", corrupt_one_state),
    ("truncated gate-code table", truncate_table),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-gate-table-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: exhaustive gate checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"GATE TABLE META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("GATE TABLE META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"GATE TABLE META-MUTATION CHECK: PASS — {len(CASES)} corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
