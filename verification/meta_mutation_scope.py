#!/usr/bin/env python3
"""Attack consolidation scope policy in temporary copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_scope_registry.py"


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


def activate_bridge(root: Path) -> None:
    path = root / "verification" / "scope_registry.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    row = next(row for row in doc["frontier_scope"] if row["id"] == "CF-012")
    row["schedule"] = "active"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def drop_claim_placement(root: Path) -> None:
    path = root / "verification" / "scope_registry.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["claim_scope"] = [
        row for row in doc["claim_scope"] if row["id"] != "C-MATH-001"
    ]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def invent_closed_frontier_as_open_scope(root: Path) -> None:
    path = root / "verification" / "scope_registry.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["frontier_scope"].append(
        {
            "id": "CF-010",
            "layer": "core",
            "schedule": "active",
            "reason": "mutation fixture",
        }
    )
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("parked Bridge promoted to active", activate_bridge),
    ("canonical claim loses scope placement", drop_claim_placement),
    ("closed debt reintroduced into open scheduling", invent_closed_frontier_as_open_scope),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-scope-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: scope checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"SCOPE META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("SCOPE META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"SCOPE META-MUTATION CHECK: PASS — {len(CASES)} scope corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
