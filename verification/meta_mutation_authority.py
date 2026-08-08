#!/usr/bin/env python3
"""Attack structured-authority JSON↔Lean transcription in temporary copies."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_authority_transcription.py"


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


def mutate_lean_gate(root: Path) -> None:
    path = root / "formal" / "Basilisk" / "AuthorityVectors.lean"
    text = path.read_text(encoding="utf-8")
    old = 'expectedGate := .proceedAndReport }'
    new = 'expectedGate := .checkpoint }'
    if old not in text:
        raise RuntimeError("authority Lean expected gate not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_pinned_time(root: Path) -> None:
    path = root / "verification" / "authority_vectors.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["evaluation_time"] = "1990-01-01T00:00:00Z"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def mutate_action_permission(root: Path) -> None:
    path = root / "verification" / "authority_vectors.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["cases"][0]["authority"]["allowed_actions"] = ["other"]
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


CASES = [
    ("Lean expected gate drift", mutate_lean_gate),
    ("pinned expiry instant drift", mutate_pinned_time),
    ("standing action permission drift", mutate_action_permission),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-authority-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: authority transcription checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"AUTHORITY META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("AUTHORITY META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"AUTHORITY META-MUTATION CHECK: PASS — {len(CASES)} authority corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
