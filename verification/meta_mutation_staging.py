#!/usr/bin/env python3
"""Require staging-geometry checks to detect frame and activation corruption."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_staging_geometry.py"


def clone_minimal(dst: Path) -> None:
    shutil.copytree(ROOT / "verification", dst / "verification")


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


def mutate_nonprefix(root: Path) -> None:
    path = root / "verification" / "staging_geometry.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["stages"][1]["active_components"] = [0, 2]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_zero_scale(root: Path) -> None:
    path = root / "verification" / "staging_geometry.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["stages"][1]["frame_scale"] = 0.0
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("non-prefix constraint activation", mutate_nonprefix),
    ("zero frame scale collapses kernel", mutate_zero_scale),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-staging-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: staging checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"STAGING META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("STAGING META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"STAGING META-MUTATION CHECK: PASS — {len(CASES)} staging corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
