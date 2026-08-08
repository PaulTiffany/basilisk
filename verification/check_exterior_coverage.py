#!/usr/bin/env python3
"""Check completeness by lining semantic exteriors rather than sampling interiors.

A controller surface is a minimal pair: two states differing in exactly one
registered coordinate. Dependency completeness requires add/remove witnesses for
parent, child, and co-parent roles. Transport completeness requires every declared
loss class. Theorem completeness requires countermodels for selected hypotheses.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
VERIFY = ROOT / "verification"
SRC = ROOT / "src"
for path in (SRC, VERIFY):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from map_lb.controller import assess_action  # noqa: E402
from map_lb.types import ActionIntent, RiskLevel, StandingAuthority  # noqa: E402
from dependency_mutator import evaluate as evaluate_dependency  # noqa: E402

SPEC = VERIFY / "exterior_coverage.json"
DEP = VERIFY / "dependency_exterior.json"
GRAPH = VERIFY / "witness_graph.json"
QUOTIENT = VERIFY / "gate_quotient.json"
INVENTORY = VERIFY / "formal_inventory.json"


def standing_authority() -> StandingAuthority:
    return StandingAuthority(
        authority_id="exterior-standing",
        allowed_actions=("exterior",),
        max_scope=RiskLevel.CRITICAL,
        allow_external_write=True,
        allow_audience_change=True,
        allow_privacy_change=True,
        allow_authority_expansion=True,
    )


def intent_from_state(label: str, state: dict) -> ActionIntent:
    payload = {
        "action_id": label,
        "action_class": "exterior",
        "description": "Exterior completeness witness.",
        **{k: v for k, v in state.items() if k != "standing_authorized"},
        "tags": ["exterior-coverage"],
    }
    return ActionIntent.from_dict(payload)


def gate_for(label: str, state: dict) -> str:
    authority = standing_authority() if state["standing_authorized"] else None
    return assess_action(intent_from_state(label, state), authority).gate.label()


def changed_coordinates(before: dict, after: dict) -> set[str]:
    return {key for key in before if before[key] != after[key]}


def main() -> int:
    errors: list[str] = []
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    controller = spec["controller"]
    defaults = controller["defaults"]
    required_fields = set(controller["required_surface_fields"])
    surfaces = controller["surfaces"]
    probes = controller["probes"]

    surface_ids = [surface["id"] for surface in surfaces]
    if len(surface_ids) != len(set(surface_ids)):
        errors.append("duplicate controller exterior surface IDs")

    covered_fields: set[str] = set()
    observed_values: dict[str, set] = {
        "scope": {defaults["scope"]},
        "uncertainty": {defaults["uncertainty"]},
        "judgment_mode": {defaults["judgment_mode"]},
        "gate": set(),
    }

    for surface in surfaces:
        before = {**defaults, **surface.get("before", {})}
        after = {**defaults, **surface.get("after", {})}
        declared = set(surface.get("changed_fields", []))
        actual_changed = changed_coordinates(before, after)
        if len(declared) != 1:
            errors.append(f"{surface['id']}: surface must declare exactly one changed field")
        if actual_changed != declared:
            errors.append(
                f"{surface['id']}: not a minimal pair; declared {sorted(declared)}, "
                f"actually changed {sorted(actual_changed)}"
            )
        covered_fields |= declared

        before_gate = gate_for(surface["id"] + ":before", before)
        after_gate = gate_for(surface["id"] + ":after", after)
        if before_gate != surface["expected_before"]:
            errors.append(
                f"{surface['id']}: before expected {surface['expected_before']}, got {before_gate}"
            )
        if after_gate != surface["expected_after"]:
            errors.append(
                f"{surface['id']}: after expected {surface['expected_after']}, got {after_gate}"
            )
        observed_values["gate"].update((before_gate, after_gate))
        for field in ("scope", "uncertainty", "judgment_mode"):
            observed_values[field].update((before[field], after[field]))

    missing_fields = required_fields - covered_fields
    extra_fields = covered_fields - required_fields
    if missing_fields:
        errors.append(f"controller exterior missing surface fields: {sorted(missing_fields)}")
    if extra_fields:
        errors.append(f"controller exterior has undeclared surface fields: {sorted(extra_fields)}")

    probe_ids = [probe["id"] for probe in probes]
    if len(probe_ids) != len(set(probe_ids)):
        errors.append("duplicate controller exterior probe IDs")
    for probe in probes:
        state = {**defaults, **probe.get("overrides", {})}
        actual = gate_for(probe["id"], state)
        if actual != probe["expected_gate"]:
            errors.append(f"{probe['id']}: expected {probe['expected_gate']}, got {actual}")
        observed_values["gate"].add(actual)
        for field in ("scope", "uncertainty", "judgment_mode"):
            observed_values[field].add(state[field])

    for field, required in controller["required_values"].items():
        missing = set(required) - observed_values[field]
        if missing:
            errors.append(f"controller exterior missing {field} values: {sorted(missing)}")

    dep_doc = json.loads(DEP.read_text(encoding="utf-8"))
    required_roles = set(spec["dependency"]["required_role_mutations"])
    dep_cases = dep_doc.get("cases", [])
    dep_ids = {case.get("id") for case in dep_cases}
    if dep_ids != required_roles:
        errors.append(
            f"dependency exterior role mismatch: expected {sorted(required_roles)}, got {sorted(dep_ids)}"
        )
    for case in dep_cases:
        executable_case = {"schema_version": dep_doc.get("schema_version"), **case}
        observed = evaluate_dependency(executable_case)
        for key, expected in case["expected"].items():
            if observed.get(key) != expected:
                errors.append(
                    f"dependency {case['id']}: {key} expected {expected!r}, got {observed.get(key)!r}"
                )

    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    observed_losses = {edge.get("loss_class") for edge in graph.get("edges", [])}
    required_losses = set(spec["loss_classes"]["required"])
    missing_losses = required_losses - observed_losses
    if missing_losses:
        errors.append(f"witness exterior missing loss classes: {sorted(missing_losses)}")

    quotient = json.loads(QUOTIENT.read_text(encoding="utf-8"))
    partition = quotient.get("partition", {})
    expected_gate_keys = {"proceed", "proceed_and_report", "checkpoint", "stop"}
    if set(partition) != expected_gate_keys:
        errors.append("gate quotient must partition all four ActionGate values exactly")
    if set(partition.values()) != {"continue", "interrupt"}:
        errors.append("gate quotient must expose exactly continue and interrupt classes")
    if partition.get("proceed") != partition.get("proceed_and_report"):
        errors.append("gate quotient no longer identifies the two continuation gates")
    if partition.get("checkpoint") != partition.get("stop"):
        errors.append("gate quotient no longer identifies the two interruption gates")
    if partition.get("proceed") == partition.get("checkpoint"):
        errors.append("gate quotient collapsed continuation and interruption into one class")
    if not str(quotient.get("residual", "")).strip():
        errors.append("gate quotient lacks an explicit residual")

    assumption_file = ROOT / spec["assumption_surfaces"]["artifact"]
    assumption_text = assumption_file.read_text(encoding="utf-8") if assumption_file.exists() else ""
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    symbols = {entry.get("symbol") for entry in inventory.get("formal_claims", [])}
    theorem_for = {
        "PreservesPredicate.comp:hT": "preserves_comp_needs_hT",
        "PreservesPredicate.comp:hS": "preserves_comp_needs_hS",
    }
    for assumption in spec["assumption_surfaces"]["required"]:
        symbol = theorem_for.get(assumption)
        if symbol is None:
            errors.append(f"unknown assumption surface declaration: {assumption}")
            continue
        if f"theorem {symbol}" not in assumption_text:
            errors.append(f"missing Lean assumption countermodel: {symbol}")
        if symbol not in symbols:
            errors.append(f"assumption countermodel not in formal inventory: {symbol}")

    if errors:
        print("EXTERIOR COMPLETENESS CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "EXTERIOR COMPLETENESS CHECK: PASS — "
        f"{len(surfaces)} minimal controller surfaces, {len(probes)} enum probes, "
        f"{len(dep_cases)} dependency role mutations, {len(required_losses)} loss classes, "
        f"{len(spec['assumption_surfaces']['required'])} theorem-assumption countermodels"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
