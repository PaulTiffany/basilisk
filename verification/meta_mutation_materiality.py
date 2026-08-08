#!/usr/bin/env python3
"""Attack the finite materiality boundary in isolated temporary copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_materiality.py"


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


def mutate_belief_into_material(root: Path) -> None:
    path = root / "verification" / "materiality_witnesses.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    case = next(c for c in doc["cases"] if c["id"] == "MW02-shared-belief-only")
    case["expected"] = True
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_fake_recursive_aftereffect(root: Path) -> None:
    path = root / "verification" / "materiality_witnesses.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    case = next(c for c in doc["cases"] if c["id"] == "MW05-recursion-without-shared-aftereffect")
    case["expected"] = True
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_observer_diversity(root: Path) -> None:
    path = root / "verification" / "materiality_witnesses.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    case = next(c for c in doc["cases"] if c["id"] == "MW01-shared-obstruction")
    case["encounters"][1]["observer_id"] = case["encounters"][0]["observer_id"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_break_authored_constraint(root: Path) -> None:
    path = root / "verification" / "materiality_witnesses.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    case = next(c for c in doc["cases"] if c["id"] == "MW04-recursive-materialization")
    case["later_encounters"][1]["constraint_signature"] = "different-constraint"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("promoted shared belief into materiality", mutate_belief_into_material),
    ("accepted recursion without shared aftereffect", mutate_fake_recursive_aftereffect),
    ("erased observer diversity", mutate_remove_observer_diversity),
    ("broke authored-constraint continuity", mutate_break_authored_constraint),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-materiality-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: materiality checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"MATERIALITY META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("MATERIALITY META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"MATERIALITY META-MUTATION CHECK: PASS — {len(CASES)} ontology-boundary corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
