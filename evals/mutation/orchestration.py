#!/usr/bin/env python3
"""
Operational symbolic mutation orchestration for MAP-LB / Hypothesis Surface.

Mutation is treated as a *witnessed transformation*:
  source, changed dimensions, preserved dimensions, residual,
  loss class, and detection outcome are all inspectable.

- Deterministic mutant generation from structured base cases
- Differential assessment (original vs mutant)
- Exact classification with detector IDs and gate sets
- JSONL run ledger; survivors.md rendered from the ledger
- Never enacts authority or external effects
"""

from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .adapter import assess

ROOT = Path(__file__).resolve().parent
BASE_CASES_DIR = ROOT / "base_cases"
LEDGER_PATH = ROOT / "runs.jsonl"
SURVIVORS_PATH = ROOT / "survivors.md"

# Dimensions that are identity/book-keeping only and never counted as
# semantic change for loss-class purposes.
_IDENTITY_KEYS = {"action_id"}


def load_operators() -> List[Dict[str, Any]]:
    json_path = ROOT / "operators.json"
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return data["operators"]
    raise FileNotFoundError("evals/mutation/operators.json is required")


def load_base_cases() -> List[Dict[str, Any]]:
    cases = []
    for path in sorted(BASE_CASES_DIR.glob("*.json")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def content_fingerprint(data: Dict[str, Any]) -> str:
    """Stable short hash of a canonical serialisation (source identity)."""
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def apply_transform(
    base: Dict[str, Any], transform: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[str], List[str], str]:
    """Deterministically apply a field-level transform.

    Returns:
        mutant,
        changed_dimensions,
        preserved_dimensions,
        loss_class
    """
    mutant = deepcopy(base)
    set_map = transform.get("set", {})
    changed: List[str] = []
    for key, value in set_map.items():
        old = base.get(key)
        if old != value:
            changed.append(key)
        mutant[key] = value

    # action_id is always rewritten for ledger clarity; treat as identity, not semantic change.
    mutant["action_id"] = f"{base.get('action_id', 'base')}-mut"

    all_keys = set(base.keys()) | set(mutant.keys())
    preserved = sorted(
        k for k in all_keys
        if k not in changed and k not in _IDENTITY_KEYS and base.get(k) == mutant.get(k)
    )
    changed = sorted(changed)

    # Loss class: what distinctions the transform itself discards or quotients.
    loss_class = _infer_loss_class(changed, set_map, base)

    return mutant, changed, preserved, loss_class


def _infer_loss_class(
    changed: List[str], set_map: Dict[str, Any], base: Dict[str, Any]
) -> str:
    """Classify what the transformation itself quotients or discards."""
    if not changed:
        return "none"
    if "tags" in changed and set_map.get("tags") == []:
        return "residual-elision"
    if "within_contract" in changed and set_map.get("within_contract") is False:
        return "contract-boundary-collapse"
    if "hard_boundary_violation" in changed and set_map.get("hard_boundary_violation") is True:
        return "boundary-injection"
    if any(k in changed for k in ("judgment_mode", "judgment_requested", "uncertainty")):
        return "judgment-strength-inflation"
    if any(k in changed for k in ("authority_expansion", "audience_change", "privacy_change")):
        return "authority-surface-expansion"
    return "field-overwrite"


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
    """Generate mutant as a witnessed transformation, assess both sides, classify."""
    record: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator_id": operator["id"],
        "base_action_id": base.get("action_id"),
        "source_fingerprint": content_fingerprint(base),
        "status": None,
        "base_gate": None,
        "mutant_gate": None,
        "changed_dimensions": [],
        "preserved_dimensions": [],
        "loss_class": None,
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
        mutant, changed, preserved, loss_class = apply_transform(
            base, operator.get("transform", {})
        )
        record["changed_dimensions"] = changed
        record["preserved_dimensions"] = preserved
        record["loss_class"] = loss_class

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
        "Rendered from `runs.jsonl`. Each entry is a witnessed transformation.",
        "Paul holds practical erasure, revision, reversion, and persistence authority.",
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
                    f"(mutant_gate={rec.get('mutant_gate')}, "
                    f"loss_class={rec.get('loss_class')}, "
                    f"changed={rec.get('changed_dimensions')}): "
                    f"{rec.get('residual')}"
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
            print(
                f"{rec['operator_id']} × {rec['base_action_id']}: {rec['status']} "
                f"[loss={rec.get('loss_class')}, changed={rec.get('changed_dimensions')}]"
            )

    append_ledger(records)
    render_survivors()
    print(f"Ledger updated: {LEDGER_PATH}")
    print(f"Survivors rendered: {SURVIVORS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
