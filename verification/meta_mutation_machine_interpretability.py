#!/usr/bin/env python3
"""Attack the machine-interpretability join checker in temporary copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_machine_interpretability.py"


def clone_minimal(dst: Path) -> None:
    shutil.copytree(ROOT / "verification", dst / "verification")
    shutil.copytree(ROOT / "formal", dst / "formal")
    shutil.copytree(ROOT / "src", dst / "src")
    shutil.copytree(ROOT / "docs", dst / "docs")
    shutil.copytree(ROOT / "evals", dst / "evals")


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


def mutate_remove_binding(root: Path) -> None:
    path = root / "verification" / "bindings.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    target = "C-MATH-001"
    doc["bindings"] = [row for row in doc["bindings"] if row.get("claim_id") != target]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_formal_module_drift(root: Path) -> None:
    path = root / "verification" / "formal_inventory.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    row = next(item for item in doc["formal_claims"] if item.get("semantic_claim_id") == "C-MATH-001")
    row["module"] = "formal/Basilisk/Contract.lean"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_closed_frontier_schedule(root: Path) -> None:
    path = root / "verification" / "scope_registry.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["frontier_scope"].append(
        {"id": "CF-008", "layer": "core", "schedule": "active", "reason": "mutation"}
    )
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("semantic claim loses all exact bindings", mutate_remove_binding),
    ("Lean formal module drifts from provenance module", mutate_formal_module_drift),
    ("closed frontier item regains active scheduling", mutate_closed_frontier_schedule),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-machine-interpretability-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"MACHINE INTERPRETABILITY META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("MACHINE INTERPRETABILITY META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "MACHINE INTERPRETABILITY META-MUTATION CHECK: PASS — "
        f"{len(CASES)} registry corruptions detected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
