#!/usr/bin/env python3
"""Require the exterior checker to detect erasure of the open completeness frontier."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "verification" / "check_exterior_coverage.py"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="basilisk-frontier-mutation-") as tmp:
        temp_root = Path(tmp)
        for name in ("verification", "formal", "src"):
            shutil.copytree(ROOT / name, temp_root / name)

        frontier = temp_root / "verification" / "completeness_frontier.json"
        doc = json.loads(frontier.read_text(encoding="utf-8"))
        doc["frontier"] = []
        frontier.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

        env = os.environ.copy()
        env["BASILISK_ROOT"] = str(temp_root)
        result = subprocess.run(
            [sys.executable, str(CHECKER)],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode == 0:
            print("FRONTIER META-MUTATION: FAIL — erased frontier was not detected")
            return 1
        first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "<no output>"
        print(f"FRONTIER META-MUTATION: PASS — erased frontier detected -> {first}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
