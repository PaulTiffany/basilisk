#!/usr/bin/env python3
"""Mutation pressure for the exhaustive gate interaction-order spectrum."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "verification" / "interaction_order.json"
CHECKER = ROOT / "verification" / "check_interaction_order.py"
REGISTRY_IO = ROOT / "verification" / "registry_io.py"


def run_mutant(doc: dict) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        verification = root / "verification"
        verification.mkdir()
        shutil.copytree(ROOT / "src", root / "src")
        (verification / "interaction_order.json").write_text(
            json.dumps(doc, indent=2) + "\n", encoding="utf-8"
        )
        (verification / "check_interaction_order.py").write_text(
            CHECKER.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (verification / "registry_io.py").write_text(
            REGISTRY_IO.read_text(encoding="utf-8"), encoding="utf-8"
        )
        result = subprocess.run(
            ["python3", str(verification / "check_interaction_order.py")],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode != 0


def main() -> int:
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    mutants: list[tuple[str, dict]] = []

    m1 = json.loads(json.dumps(original))
    m1["expected"]["proceed"]["max_order"] = 3
    mutants.append(("pretend proceed is third-order", m1))

    m2 = json.loads(json.dumps(original))
    m2["expected"]["checkpoint"]["nonzero_coefficients_by_order"]["9"] = 0
    mutants.append(("erase ninth-order checkpoint coefficient", m2))

    m3 = json.loads(json.dumps(original))
    support = m3["expected"]["proceed_and_report"]["max_order_supports"][0]
    support.remove("critical_uncertainty")
    mutants.append(("corrupt maximum-order support", m3))

    survivors = [name for name, mutant in mutants if not run_mutant(mutant)]
    if survivors:
        print("INTERACTION ORDER META-MUTATION: FAIL")
        for name in survivors:
            print(f"- survivor: {name}")
        return 1
    print(f"INTERACTION ORDER META-MUTATION: PASS — killed {len(mutants)} mutants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
