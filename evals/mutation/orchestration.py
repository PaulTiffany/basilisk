#!/usr/bin/env python3
"""
Symbolic mutation orchestration skeleton for MAP-LB / Hypothesis Surface.
Dependency-free. Intended for human review before any integration.
Does not modify source protocol code. Does not expand permission.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

MUTANTS_DIR = Path(__file__).parent / "mutants"
SURVIVORS_LOG = Path(__file__).parent / "survivors.md"


def load_mutant(path: Path) -> Dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def assess_against_reference(mutated_intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder for call to the reference controller (map_lb.assess or equivalent).
    Replace with actual invocation of the dependency-free controller.
    Must return at least: gate decision, detected violations, residuals.
    """
    # TODO: integrate with src/map_lb once reviewed by human editor
    return {
        "gate": "UNKNOWN",
        "violations": [],
        "residuals": ["reference controller not yet wired"],
        "notes": "Human must replace this stub with the real assess call."
    }


def classify_outcome(mutant: Dict[str, Any], result: Dict[str, Any]) -> str:
    expected = mutant.get("expected_detection", "").lower()
    violations = [v.lower() for v in result.get("violations", [])]
    if any(tok in " ".join(violations) for tok in expected.split() if len(tok) > 3):
        return "KILLED"
    return "SURVIVED"


def main(mutant_paths: List[str] | None = None) -> None:
    paths = [Path(p) for p in mutant_paths] if mutant_paths else list(MUTANTS_DIR.glob("*.json"))
    survivors: List[str] = []

    for path in paths:
        mutant = load_mutant(path)
        result = assess_against_reference(mutant["mutated_intent"])
        status = classify_outcome(mutant, result)
        print(f"{mutant['mutant_id']}: {status}")
        if status == "SURVIVED":
            survivors.append(
                f"- {mutant['mutant_id']} ({mutant['operator']}): {mutant.get('residual', '')}"
            )

    if survivors:
        SURVIVORS_LOG.write_text(
            "# Survivors (undetected or misclassified mutants)\n\n"
            + "\n".join(survivors)
            + "\n\n<!-- Human review required. Do not auto-integrate. -->\n",
            encoding="utf-8",
        )
        print(f"Wrote {len(survivors)} survivors to {SURVIVORS_LOG}")
    else:
        print("No survivors recorded in this run.")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
