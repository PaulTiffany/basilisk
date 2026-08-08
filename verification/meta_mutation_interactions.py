#!/usr/bin/env python3
"""Attack pairwise seam completeness and diagnostics in isolated temp copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKERS = {
    "coverage": ROOT / "verification" / "check_interaction_coverage.py",
    "diagnostics": ROOT / "verification" / "check_interaction_diagnostics.py",
}


def clone_minimal(dst: Path) -> None:
    shutil.copytree(ROOT / "verification", dst / "verification")
    shutil.copytree(ROOT / "src", dst / "src")


def run_check(name: str, temp_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BASILISK_ROOT"] = str(temp_root)
    return subprocess.run(
        [sys.executable, str(CHECKERS[name])],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def mutate_remove_seam_class(root: Path) -> None:
    path = root / "verification" / "interaction_coverage.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["squares"] = [s for s in doc["squares"] if s["class"] != "risk_synergy"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_degenerate_square(root: Path) -> None:
    path = root / "verification" / "interaction_coverage.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    square = next(s for s in doc["squares"] if s["id"] == "IX09-rollback-inspectability")
    square["factors"][1]["on"] = square["factors"][1]["off"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_false_corner(root: Path) -> None:
    path = root / "verification" / "interaction_coverage.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    square = next(s for s in doc["squares"] if s["id"] == "IX05-hard-boundary-fresh")
    square["expected"]["11"] = "proceed_and_report"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_diagnostic_reason_only(root: Path) -> None:
    path = root / "verification" / "interaction_diagnostics.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assertion = next(a for a in doc["assertions"] if a["id"] == "ID03-audience-and-privacy")
    assertion["reason_contains"] = ["audience change"]
    assertion["reason_excludes"] = ["privacy boundary change"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("erased interaction seam class", "coverage", mutate_remove_seam_class),
    ("degenerated 2x2 interaction square", "coverage", mutate_degenerate_square),
    ("falsified interaction corner", "coverage", mutate_false_corner),
    ("diagnostic semantics corrupted while gate stays unchanged", "diagnostics", mutate_diagnostic_reason_only),
]


def main() -> int:
    failures: list[str] = []
    for label, checker, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-interaction-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(checker, temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: {checker} checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"INTERACTION META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("INTERACTION META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"INTERACTION META-MUTATION CHECK: PASS — {len(CASES)} seam corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
