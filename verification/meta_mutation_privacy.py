#!/usr/bin/env python3
"""Mutation pressure for minimum-sufficient-disclosure privacy witnesses."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "verification" / "privacy_witnesses.json"
CHECKER = ROOT / "verification" / "check_privacy.py"
REGISTRY_IO = ROOT / "verification" / "registry_io.py"


def run_mutant(doc: dict) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        verification = root / "verification"
        verification.mkdir()
        (verification / "privacy_witnesses.json").write_text(
            json.dumps(doc, indent=2) + "\n", encoding="utf-8"
        )
        (verification / "check_privacy.py").write_text(
            CHECKER.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (verification / "registry_io.py").write_text(
            REGISTRY_IO.read_text(encoding="utf-8"), encoding="utf-8"
        )
        result = subprocess.run(
            ["python3", str(verification / "check_privacy.py")],
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
    next(w for w in m1["witnesses"] if w["id"] == "PRIV-01")["private_interior_exposed"] = True
    mutants.append(("erase selective privacy preservation", m1))

    m2 = json.loads(json.dumps(original))
    next(w for w in m2["witnesses"] if w["id"] == "PRIV-01")["provenance_observable"] = False
    mutants.append(("remove required selective accountability evidence", m2))

    m3 = json.loads(json.dumps(original))
    next(w for w in m3["witnesses"] if w["id"] == "PRIV-02")["private_interior_exposed"] = False
    mutants.append(("collapse total exposure into selective disclosure", m3))

    survivors = [name for name, mutant in mutants if not run_mutant(mutant)]
    if survivors:
        print("PRIVACY META-MUTATION: FAIL")
        for name in survivors:
            print(f"- survivor: {name}")
        return 1
    print(f"PRIVACY META-MUTATION: PASS — killed {len(mutants)} mutants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
