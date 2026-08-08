#!/usr/bin/env python3
"""Attack trefoil-like junction topology and stop/release semantics."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_trefoil_junctions.py"


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


def load(root: Path) -> tuple[Path, dict]:
    path = root / "verification" / "trefoil_junctions.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, doc: dict) -> None:
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_erase_trefoil_strand(root: Path) -> None:
    path, doc = load(root)
    junction = next(j for j in doc["junctions"] if j["id"] == "TJ01-destructive-external-missing-fresh")
    junction["interaction_signature"]["linked_pairs"] = ["AB", "BC"]
    save(path, doc)


def mutate_zero_third_order(root: Path) -> None:
    path, doc = load(root)
    junction = next(j for j in doc["junctions"] if j["id"] == "TJ03-privacy-audience-missing-standing")
    junction["interaction_signature"]["third_order_residual"] = 0
    save(path, doc)


def mutate_false_trefoil_label(root: Path) -> None:
    path, doc = load(root)
    junction = next(j for j in doc["junctions"] if j["id"] == "UC01-hard-boundary-authority-control")
    junction["topology_class"] = "trefoil_like"
    junction["interaction_signature"] = {
        "linked_pairs": ["AB", "BC", "CA"],
        "third_order_residual": 1,
    }
    save(path, doc)


def mutate_release_strand_identity(root: Path) -> None:
    path, doc = load(root)
    junction = next(j for j in doc["junctions"] if j["id"] == "TJ01-destructive-external-missing-fresh")
    junction["stop_condition"]["release_edges"][0]["factor"] = "external-effect"
    save(path, doc)


CASES = [
    ("erased trefoil pairwise strand", mutate_erase_trefoil_strand),
    ("zeroed trefoil third-order residual", mutate_zero_third_order),
    ("falsely labeled unknot as trefoil", mutate_false_trefoil_label),
    ("corrupted stop-release strand identity", mutate_release_strand_identity),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-trefoil-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: trefoil checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"TREFOIL META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("TREFOIL META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"TREFOIL META-MUTATION CHECK: PASS — {len(CASES)} junction corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
