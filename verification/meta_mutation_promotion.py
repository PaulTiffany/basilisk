#!/usr/bin/env python3
"""Attack imaginal-to-operational promotion boundaries in temporary copies."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_promotion_vectors.py"


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


def mutate_recurrence_becomes_verification(root: Path) -> None:
    path = root / "src" / "map_lb" / "promotion.py"
    text = path.read_text(encoding="utf-8")
    old = "if not intent.externally_verified:\n            reasons = [\"shared-world assertion requires external verification\"]"
    new = "if not intent.externally_verified and intent.recurrence_count < 49:\n            reasons = [\"shared-world assertion requires external verification\"]"
    if old not in text:
        raise RuntimeError("promotion verification boundary not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_ideal_becomes_authority(root: Path) -> None:
    path = root / "src" / "map_lb" / "promotion.py"
    text = path.read_text(encoding="utf-8")
    old = "if not intent.human_authorized:\n            reasons = [\"operative authorization requires a human decision owner\"]"
    new = "if not (intent.human_authorized or intent.coordination_ideal_salient):\n            reasons = [\"operative authorization requires a human decision owner\"]"
    if old not in text:
        raise RuntimeError("promotion authority boundary not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_allow_silent_multistage_jump(root: Path) -> None:
    path = root / "src" / "map_lb" / "promotion.py"
    text = path.read_text(encoding="utf-8")
    old = "if int(intent.target) != int(intent.source) + 1:\n        return PromotionAssessment("
    new = "if False and int(intent.target) != int(intent.source) + 1:\n        return PromotionAssessment("
    if old not in text:
        raise RuntimeError("multi-stage promotion stop not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


CASES = [
    ("recurrence becomes verification at 49 loops", mutate_recurrence_becomes_verification),
    ("coordination ideal self-authorizes", mutate_ideal_becomes_authority),
    ("silent multi-stage promotion allowed", mutate_allow_silent_multistage_jump),
]


def main() -> int:
    failures: list[str] = []
    for label, mutator in CASES:
        with tempfile.TemporaryDirectory(prefix="basilisk-promotion-mutation-") as tmp:
            temp_root = Path(tmp)
            clone_minimal(temp_root)
            mutator(temp_root)
            result = run_check(temp_root)
            if result.returncode == 0:
                failures.append(f"{label}: promotion checker FAILED TO DETECT mutation")
            else:
                first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
                print(f"PROMOTION META-MUTATION DETECTED: {label} -> {first}")

    if failures:
        print("PROMOTION META-MUTATION CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PROMOTION META-MUTATION CHECK: PASS — {len(CASES)} promotion corruptions detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
