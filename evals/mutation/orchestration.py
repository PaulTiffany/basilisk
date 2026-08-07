#!/usr/bin/env python3
"""
Operational symbolic mutation orchestration for MAP-LB / Hypothesis Surface.

- Deterministic mutant generation from structured base cases
- Differential assessment (original vs mutant)
- Exact classification with detector IDs and gate sets
- JSONL run ledger; survivors.md rendered from the ledger
- Never enacts authority or external effects
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .adapter import assess

ROOT = Path(__file__).resolve().parent
BASE_CASES_DIR = ROOT / "base_cases"
OPERATORS_PATH = ROOT / "operators.yaml"
LEDGER_PATH = ROOT / "runs.jsonl"
SURVIVORS_PATH = ROOT / "survivors.md"


def _load_yaml_operators(path: Path) -> List[Dict[str, Any]]:
    """Minimal YAML loader for the operators file (avoids external dependency)."""
    # The operators file is intentionally simple; we parse the list of operator dicts
    # via a very small subset parser sufficient for the controlled schema.
    # For robustness we also accept a JSON sibling if present.
    json_sibling = path.with_suffix(".json")
    if json_sibling.exists():
        return json.loads(json_sibling.read_text(encoding="utf-8"))["operators"]

    text = path.read_text(encoding="utf-8")
    # Fallback: require operators.json for fully deterministic environments.
    # The committed operators.yaml is the source of truth; a generated
    # operators.json may be produced by a human or CI step if needed.
    raise RuntimeError(
        "operators.yaml present but no operators.json sibling. "
        "Emit a JSON snapshot of the operator catalogue for the harness."
    )


def load_operators() -> List[Dict[str, Any]]:
    json_path = ROOT / "operators.json"
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return data["operators"]
    # Bootstrap: if only YAML exists, the test suite / human can materialise JSON.
    # For the operational layer we ship operators.json explicitly.
    raise FileNotFoundError("evals/mutation/operators.json is required")


def load_base_cases() -> List[Dict[str, Any]]:
    cases = []
    for path in sorted(BASE_CASES_DIR.glob("*.json")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def apply_transform(base: Dict[str, Any], transform: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically apply a field-level transform to a base intent."""
    mutant = deepcopy(base)
    for key, value in transform.get("set", {}).items():
        mutant[key] = value
    # Ensure action_id remains distinct for ledger clarity.
    mutant["action_id"] = f"{base.get('action_id', 'base')}-mut"
    return mutant


def classify(
    operator: Dict[str, Any],
    base_result: Dict[str, Any],
    mutant_result: Dict[str, Any],
) -> str:
    """Exact classification using detector substrings and gate sets."""
    allowed = set(operator.get("allowed_gates", []))
    forbidden = set(operator.get("forbidden_gates", []))
    required = operator.get("required_detectors", [])

    mutant_gate = mutant_result.get("gate")
    mutant_reasons = [r.lower() for r in mutant_result.get("reasons", [])]

    if forbidden and mutant_gate in forbidden:
        return "SURVIVED"

    if allowed and mutant_gate not in allowed:
        return "SURVIVED"

    for det in required:
        if not any(det.lower() in r for r in mutant_reasons):
            return "SURVIVED"

    # If base and mutant assessments are identical and no required detectors,
    # treat as potentially equivalent.
    if (
        not required
        and base_result.get("gate") == mutant_result.get("gate")
        and base_result.get("reasons") == mutant_result.get("reasons")
    ):
        return "EQUIVALENT"

    return "KILLED"


def run_pair(
    base: Dict[str, Any],
    operator: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate mutant, assess both sides, classify, return ledger record."""
    record: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator_id": operator["id"],
        "base_action_id": base.get("action_id"),
        "status": None,
        "base_gate": None,
        "mutant_gate": None,
        "residual": operator.get("residual"),
        "error": None,
    }

    try:
        base_result = assess(base)
        record["base_gate"] = base_result.get("gate")
    except Exception as exc:  # noqa: BLE001
        record["status"] = "INVALID_BASE"
        record["error"] = f"base assessment failed: {exc}"
        return record

    try:
        mutant = apply_transform(base, operator.get("transform", {}))
        mutant_result = assess(mutant)
        record["mutant_gate"] = mutant_result.get("gate")
        record["mutant_reasons"] = mutant_result.get("reasons")
    except Exception as exc:  # noqa: BLE001
        record["status"] = "ERROR"
        record["error"] = f"mutant assessment failed: {exc}"
        return record

    record["status"] = classify(operator, base_result, mutant_result)
    return record


def append_ledger(records: List[Dict[str, Any]]) -> None:
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, sort_keys=True) + "\n")


def render_survivors() -> None:
    if not LEDGER_PATH.exists():
        SURVIVORS_PATH.write_text(
            "# Survivors\n\n(no runs yet)\n",
            encoding="utf-8",
        )
        return

    lines = [
        "# Survivors (undetected or misclassified mutants)\n",
        "",
        "Rendered from `runs.jsonl`. Human review required for any protocol change.",
        "",
    ]
    found = False
    with LEDGER_PATH.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("status") == "SURVIVED":
                found = True
                lines.append(
                    f"- `{rec.get('operator_id')}` on `{rec.get('base_action_id')}` "
                    f"(mutant_gate={rec.get('mutant_gate')}): {rec.get('residual')}"
                )
    if not found:
        lines.append("(none in current ledger)")
    lines.append("")
    SURVIVORS_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    operators = load_operators()
    bases = load_base_cases()
    if not bases:
        print("No base cases found.", file=sys.stderr)
        return 1

    records: List[Dict[str, Any]] = []
    for op in operators:
        for base in bases:
            rec = run_pair(base, op)
            records.append(rec)
            print(f"{rec['operator_id']} × {rec['base_action_id']}: {rec['status']}")

    append_ledger(records)
    render_survivors()
    print(f"Ledger updated: {LEDGER_PATH}")
    print(f"Survivors rendered: {SURVIVORS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
