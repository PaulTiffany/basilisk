#!/usr/bin/env python3
"""Render/check the Trust and Verify exemplar as a controller observation.

The seed declares operations and mutations only. It does not declare expected
truth values. Gates are observed from the live MAP-LB controller so this file
cannot silently make an LLM-authored expectation into controller authority.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("BASILISK_ROOT", DEFAULT_ROOT)).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.controller import assess_action  # noqa: E402
from map_lb.gate_projection import project_gate  # noqa: E402
from map_lb.types import ActionIntent  # noqa: E402
from registry_io import strict_load_json  # noqa: E402

SEED = ROOT / "verification" / "trust_and_verify_seed.json"
TARGET = ROOT / "evals" / "trust_and_verify.json"


def _projection(intent: ActionIntent) -> dict[str, bool]:
    authorized = intent.current_turn_explicit_authorization
    return asdict(project_gate(intent, authorized=authorized))


def _observe_operation(row: dict[str, object]) -> tuple[ActionIntent, dict[str, object]]:
    intent = ActionIntent.from_dict(dict(row["intent"]))
    actual_gate = assess_action(intent).gate.label()
    return intent, {
        "id": row["id"],
        "semantic_role": row["semantic_role"],
        "actual_gate": actual_gate,
        "intent": intent.to_dict(),
        "projection": _projection(intent),
    }


def build_doc() -> dict[str, object]:
    seed = strict_load_json(SEED)
    if seed.get("schema_version") != 2:
        raise ValueError(f"unsupported trust-and-verify schema: {seed.get('schema_version')!r}")

    rows = seed.get("operations", [])
    if not isinstance(rows, list):
        raise ValueError("operations must be a list")

    operations: list[dict[str, object]] = []
    by_id: dict[str, tuple[ActionIntent, dict[str, object]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("operation rows must be objects")
        op_id = str(row.get("id", ""))
        if not op_id or op_id in by_id:
            raise ValueError(f"missing or duplicate operation id: {op_id!r}")
        observed = _observe_operation(row)
        by_id[op_id] = observed
        operations.append(observed[1])

    mutations: list[dict[str, object]] = []
    mutation_ids: set[str] = set()
    for row in seed.get("mutations", []):
        if not isinstance(row, dict):
            raise ValueError("mutation rows must be objects")
        mutation_id = str(row.get("id", ""))
        if not mutation_id or mutation_id in mutation_ids:
            raise ValueError(f"missing or duplicate mutation id: {mutation_id!r}")
        mutation_ids.add(mutation_id)

        base_id = str(row["base_operation"])
        if base_id not in by_id:
            raise ValueError(f"{mutation_id}: unknown base operation {base_id!r}")
        base_intent, base_output = by_id[base_id]
        baseline = base_intent.to_dict()

        patch = row.get("set", {})
        if not isinstance(patch, dict):
            raise ValueError(f"{mutation_id}: set must be an object")
        mutated_intent = ActionIntent.from_dict({**baseline, **patch})
        mutated_normalized = mutated_intent.to_dict()
        mutated_gate = assess_action(mutated_intent).gate.label()
        base_projection = _projection(base_intent)
        mutated_projection = _projection(mutated_intent)
        changed_intent_fields = sorted(
            key for key in baseline if baseline[key] != mutated_normalized[key]
        )
        changed_projection_fields = sorted(
            key for key in base_projection
            if base_projection[key] != mutated_projection[key]
        )
        mutations.append(
            {
                "id": mutation_id,
                "base_operation": base_id,
                "mutation_class": row["mutation_class"],
                "changed_intent_fields": changed_intent_fields,
                "changed_projection_fields": changed_projection_fields,
                "base_gate": base_output["actual_gate"],
                "mutated_gate": mutated_gate,
                "mutated_intent": mutated_normalized,
                "mutated_projection": mutated_projection,
            }
        )

    return {
        "schema_version": 2,
        "kind": "generated_controller_observation",
        "judgment_status": "none",
        "exemplar_id": seed["exemplar_id"],
        "source": "verification/trust_and_verify_seed.json",
        "scenario": seed["scenario"],
        "operations": operations,
        "mutations": mutations,
        "observed_gate_profile": {
            row["id"]: row["actual_gate"]
            for row in operations
        },
        "observed_mutation_profile": {
            row["id"]: {
                "base_gate": row["base_gate"],
                "mutated_gate": row["mutated_gate"],
            }
            for row in mutations
        },
    }


def canonical_text(doc: dict[str, object]) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def check() -> int:
    expected = build_doc()
    try:
        observed = strict_load_json(TARGET)
    except Exception as exc:
        print("TRUST AND VERIFY CHECK: FAIL")
        print(f"- stored observation is not strict JSON: {exc}")
        return 1

    errors: list[str] = []
    if observed != expected:
        errors.append("stored observation disagrees with deterministic live-controller rendering")
    if TARGET.read_text(encoding="utf-8") != canonical_text(expected):
        errors.append("stored observation is not in deterministic canonical serialization")

    if errors:
        print("TRUST AND VERIFY CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    gates = expected["observed_gate_profile"]
    mutations = expected["observed_mutation_profile"]
    print(
        "TRUST AND VERIFY CHECK: PASS — observational only; "
        f"gates={gates}; mutations={mutations}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    TARGET.write_text(canonical_text(build_doc()), encoding="utf-8")
    print(f"rendered {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
