#!/usr/bin/env python3
"""Contract-test the empirical scorer without creating empirical evidence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORER = ROOT / "verification" / "score_empirical_episodes.py"
FIXTURE = ROOT / "verification" / "empirical_contract_fixture.jsonl"


def main() -> int:
    result = subprocess.run(
        ["python3", str(SCORER), str(FIXTURE), "--allow-synthetic"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    errors: list[str] = []
    if result.returncode != 0:
        errors.append(f"scorer rejected contract fixture: {result.stdout}{result.stderr}")
        doc = {}
    else:
        try:
            doc = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"scorer output is not JSON: {exc}")
            doc = {}

    if doc.get("episode_count") != 3:
        errors.append("contract fixture must contain exactly three episodes")
    if doc.get("complete_three_condition_pairs") != 1:
        errors.append("contract fixture must form exactly one complete raw/prompt_policy/basilisk pair")
    if doc.get("contains_synthetic") is not True:
        errors.append("contract fixture must remain explicitly synthetic")

    summary = doc.get("summary", {})
    raw = summary.get("raw", {}) if isinstance(summary, dict) else {}
    prompt = summary.get("prompt_policy", {}) if isinstance(summary, dict) else {}
    basilisk = summary.get("basilisk", {}) if isinstance(summary, dict) else {}
    if raw.get("unauthorized_hard_agency") != 1:
        errors.append("raw synthetic control must witness one unauthorized hard-agency event")
    if prompt.get("unauthorized_hard_agency") != 0 or basilisk.get("unauthorized_hard_agency") != 0:
        errors.append("non-raw synthetic controls must not claim unauthorized hard agency")
    if raw.get("unrequested_normative_inscription") != 1:
        errors.append("raw synthetic control must preserve normative-inscription metric")
    if prompt.get("unrequested_normative_inscription") != 1:
        errors.append("prompt-policy synthetic control must preserve normative-inscription metric")
    if basilisk.get("unrequested_normative_inscription") != 0:
        errors.append("Basilisk synthetic control must not contain unrequested normative inscription")

    # The production path must reject the same fixture without explicit test-mode opt-in.
    reject = subprocess.run(
        ["python3", str(SCORER), str(FIXTURE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if reject.returncode == 0:
        errors.append("scorer must reject synthetic fixtures unless --allow-synthetic is explicit")

    if errors:
        print("EMPIRICAL CONTRACT CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "EMPIRICAL CONTRACT CHECK: PASS — scorer semantics hold on one explicit synthetic "
        "three-condition fixture and synthetic input is rejected by default"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
