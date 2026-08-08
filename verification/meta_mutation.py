#!/usr/bin/env python3
"""Deliberately damage temporary copies and require verifier detection.

This is a mutation test of the interpretability machinery itself. The live
repository is never modified: each mutation is applied to an isolated temp copy.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "provenance": ROOT / "verification" / "check_provenance.py",
    "recursivity": ROOT / "verification" / "check_recursivity.py",
    "numeric": ROOT / "verification" / "check_numeric.py",
    "formal": ROOT / "verification" / "check_formal_closure.py",
}


def clone_minimal(dst: Path) -> None:
    for name in ("verification", "formal", "docs", "evals"):
        src = ROOT / name
        if src.exists():
            shutil.copytree(src, dst / name)


def run_check(name: str, temp_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["BASILISK_ROOT"] = str(temp_root)
    return subprocess.run(
        [sys.executable, str(CHECKS[name])],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def mutate_bad_receipt(root: Path) -> None:
    path = root / "verification" / "bindings.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["bindings"][0]["sha256"] = "0" * 64
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_cycle(root: Path) -> None:
    path = root / "verification" / "claims.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in doc["claims"]}
    by_id["C-MATH-001"]["depends_on"] = ["C-MATH-003"]
    by_id["C-MATH-003"]["depends_on"] = ["C-MATH-001"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_numeric_expected(root: Path) -> None:
    path = root / "verification" / "EXPECTED_NUMERIC.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["claims"]["C-MATH-001"]["observed_lipschitz_ratio"] = 999.0
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_inventory_entry(root: Path) -> None:
    path = root / "verification" / "formal_inventory.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["formal_claims"] = [
        e for e in doc["formal_claims"] if e["symbol"] != "lipschitz_alone_not_constitutional"
    ]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_remove_root_import(root: Path) -> None:
    path = root / "formal" / "Basilisk.lean"
    text = path.read_text(encoding="utf-8")
    text = text.replace("import Basilisk.ConstitutionalLipschitz\n", "")
    path.write_text(text, encoding="utf-8")


CASES = [
    ("bad provenance receipt", "provenance", mutate_bad_receipt),
    ("undeclared recursive justification", "recursivity", mutate_cycle),
    ("falsified numerical evidence", "numeric", mutate_numeric_expected),
    ("unregistered Lean theorem", "formal", mutate_remove_inventory_entry),
    ("unreachable Lean proof module", "formal", mutate_remove_root_import),
]


def main() -> int:
    failures: list[str] = []
    for label, checker, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-meta-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(checker, temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: verifier FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"META-MUTATION CHECK: PASS — {len(CASES)} deliberate corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
