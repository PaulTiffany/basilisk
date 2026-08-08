#!/usr/bin/env python3
"""Mutation pressure for the finite nominal-choice / evitability distinction."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "verification" / "evitability_witnesses.json"
CHECKER = ROOT / "verification" / "check_evitability.py"


def run_mutant(doc: dict) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "verification").mkdir()
        (root / "verification" / "evitability_witnesses.json").write_text(
            json.dumps(doc, indent=2) + "\n", encoding="utf-8"
        )
        (root / "verification" / "check_evitability.py").write_text(
            CHECKER.read_text(encoding="utf-8"), encoding="utf-8"
        )
        env = dict(os.environ)
        # The checker derives ROOT from its own copied path.
        result = subprocess.run(
            ["python3", str(root / "verification" / "check_evitability.py")],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode != 0


def main() -> int:
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    mutants: list[tuple[str, dict]] = []

    m1 = json.loads(json.dumps(original))
    ev1 = next(c for c in m1["cases"] if c["id"] == "EV-001")
    ev1["after"]["viable"]["alternative"] = True
    mutants.append(("erase viability-loss witness", m1))

    m2 = json.loads(json.dumps(original))
    ev1 = next(c for c in m2["cases"] if c["id"] == "EV-001")
    ev1["after"]["available"]["alternative"] = False
    mutants.append(("confound nominal deletion with viability loss", m2))

    m3 = json.loads(json.dumps(original))
    ev2 = next(c for c in m3["cases"] if c["id"] == "EV-002")
    ev2["after"]["viable"]["alternative"] = False
    mutants.append(("break positive plural control", m3))

    survivors = [name for name, mutant in mutants if not run_mutant(mutant)]
    if survivors:
        print("EVITABILITY META-MUTATION: FAIL")
        for name in survivors:
            print(f"- survivor: {name}")
        return 1
    print(f"EVITABILITY META-MUTATION: PASS — killed {len(mutants)} mutants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
