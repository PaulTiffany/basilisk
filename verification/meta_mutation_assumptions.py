#!/usr/bin/env python3
"""Attack theorem-assumption coverage in temporary repository copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_theorem_assumptions.py"


def clone_minimal(dst: Path) -> None:
    shutil.copytree(ROOT / "verification", dst / "verification")
    shutil.copytree(ROOT / "formal", dst / "formal")


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


def load_registry(root: Path) -> tuple[Path, dict]:
    path = root / "verification" / "theorem_assumptions.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def write_registry(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def delete_classification(root: Path) -> None:
    path, doc = load_registry(root)
    doc["assumptions"] = doc["assumptions"][1:]
    write_registry(path, doc)


def downgrade_substantive(root: Path) -> None:
    path, doc = load_registry(root)
    row = next(r for r in doc["assumptions"] if r["category"] == "substantive")
    row["category"] = "definitional"
    row["evidence_symbol"] = None
    write_registry(path, doc)


def point_outside_necessity_surface(root: Path) -> None:
    path, doc = load_registry(root)
    row = next(r for r in doc["assumptions"] if r["category"] == "substantive")
    row["evidence_symbol"] = "ActionGate.fromNat_toNat"
    write_registry(path, doc)


CASES = [
    ("missing premise classification", delete_classification),
    ("substantive premise downgraded", downgrade_substantive),
    ("substantive witness outside necessity surface", point_outside_necessity_surface),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-assumption-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: theorem-assumption checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"ASSUMPTION META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("ASSUMPTION META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"ASSUMPTION META-MUTATION CHECK: PASS — {len(CASES)} corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
