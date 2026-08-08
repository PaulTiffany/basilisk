#!/usr/bin/env python3
"""Exhaustively check multilinear interaction order on the 11-bit gate quotient."""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.gate_projection import GateProjection, gate_from_projection  # noqa: E402
from registry_io import strict_load_json  # noqa: E402

SPEC = ROOT / "verification" / "interaction_order.json"
FIELDS = [
    "hard_boundary_violation",
    "within_contract",
    "unrequested_model_judgment",
    "critical_destructive",
    "current_turn_explicit_authorization",
    "boundary_crossing",
    "authorized",
    "high_scope",
    "critical_uncertainty",
    "material_change",
    "risk_score_at_least_report",
]
LABELS = ["proceed", "proceed_and_report", "checkpoint", "stop"]


def projection(mask: int) -> GateProjection:
    values = {field: bool((mask >> index) & 1) for index, field in enumerate(FIELDS)}
    return GateProjection(**values)


def mobius(values: list[int]) -> list[int]:
    coeff = list(values)
    for bit in range(len(FIELDS)):
        for mask in range(1 << len(FIELDS)):
            if mask & (1 << bit):
                coeff[mask] -= coeff[mask ^ (1 << bit)]
    return coeff


def support(mask: int) -> list[str]:
    return [field for index, field in enumerate(FIELDS) if mask & (1 << index)]


def spectrum(coeff: list[int]) -> tuple[int, dict[str, int], list[list[str]]]:
    nonzero = [(mask, value) for mask, value in enumerate(coeff) if value != 0]
    maximum = max(mask.bit_count() for mask, _ in nonzero)
    counts = Counter(mask.bit_count() for mask, _ in nonzero)
    supports = [support(mask) for mask, _ in nonzero if mask.bit_count() == maximum]
    return maximum, {str(order): counts[order] for order in sorted(counts)}, supports


def main() -> int:
    doc = strict_load_json(SPEC)
    errors: list[str] = []
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        errors.append("interaction-order registry must be a schema_version 1 object")
    if doc.get("bit_order_lsb_first") != FIELDS:
        errors.append("registered bit order does not match live GateProjection coordinate order")
    if doc.get("state_count") != 1 << len(FIELDS):
        errors.append("registered state count must equal 2^11")

    gates = [gate_from_projection(projection(mask)).label() for mask in range(1 << len(FIELDS))]
    expected = doc.get("expected", {}) if isinstance(doc, dict) else {}
    if not isinstance(expected, dict) or set(expected) != set(LABELS):
        errors.append("expected must define exactly the four gate labels")
        expected = {}

    observed_max = 0
    for label in LABELS:
        values = [1 if gate == label else 0 for gate in gates]
        maximum, counts, supports = spectrum(mobius(values))
        observed_max = max(observed_max, maximum)
        registered = expected.get(label, {})
        if registered.get("max_order") != maximum:
            errors.append(
                f"{label}: max_order expected {registered.get('max_order')}, got {maximum}"
            )
        if registered.get("nonzero_coefficients_by_order") != counts:
            errors.append(f"{label}: coefficient spectrum drift: expected {registered.get('nonzero_coefficients_by_order')}, got {counts}")
        if registered.get("max_order_supports") != supports:
            errors.append(f"{label}: maximum-order supports drift: expected {registered.get('max_order_supports')}, got {supports}")

    if observed_max != 10:
        errors.append(f"complete one-hot interaction order expected 10, got {observed_max}")

    if errors:
        print("INTERACTION ORDER CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "INTERACTION ORDER CHECK: PASS — exhaustive 2^11 state / 2^11 subset Möbius analysis; "
        "one-hot gate orders proceed=10, proceed_and_report=10, checkpoint=9, stop=3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
