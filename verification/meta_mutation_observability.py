#!/usr/bin/env python3
"""Mutation pressure for frame-relative observability/accountability witnesses."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "verification" / "observability_witnesses.json"
CHECKER = ROOT / "verification" / "check_observability.py"
REGISTRY_IO = ROOT / "verification" / "registry_io.py"


def run_mutant(doc: dict) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        verification = root / "verification"
        verification.mkdir()
        (verification / "observability_witnesses.json").write_text(
            json.dumps(doc, indent=2) + "\n", encoding="utf-8"
        )
        (verification / "check_observability.py").write_text(
            CHECKER.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (verification / "registry_io.py").write_text(
            REGISTRY_IO.read_text(encoding="utf-8"), encoding="utf-8"
        )
        result = subprocess.run(
            ["python3", str(verification / "check_observability.py")],
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
    obs1 = next(w for w in m1["witnesses"] if w["id"] == "OBS-01")
    obs1["frame"]["relevant_interior_observable"] = True
    mutants.append(("erase opaque-interior witness", m1))

    m2 = json.loads(json.dumps(original))
    obs1 = next(w for w in m2["witnesses"] if w["id"] == "OBS-01")
    obs1["expected_explanatory_accountability_needed"] = False
    mutants.append(("deny accountability at opaque remainder", m2))

    m3 = json.loads(json.dumps(original))
    obs3 = next(w for w in m3["witnesses"] if w["id"] == "OBS-03")
    obs3["authorized"] = True
    mutants.append(("conflate interpretability with authorization", m3))

    survivors = [name for name, mutant in mutants if not run_mutant(mutant)]
    if survivors:
        print("OBSERVABILITY META-MUTATION: FAIL")
        for name in survivors:
            print(f"- survivor: {name}")
        return 1
    print(f"OBSERVABILITY META-MUTATION: PASS — killed {len(mutants)} mutants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
