#!/usr/bin/env python3
"""Check selected 2x2x2 controller junctions and explicit stop conditions.

`trefoil_like` is an engineering interaction signature, not a knot invariant:
all three pairwise links must be present somewhere in the cube and the declared
third-order ActionGate ordinal finite difference must be nonzero.

Controls distinguish this from an unknot-like dominant strand and a detached
third strand. Stop/release edges are checked independently of the topology label.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("BASILISK_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from map_lb.controller import assess_action  # noqa: E402
from map_lb.types import ActionIntent, RiskLevel, StandingAuthority  # noqa: E402

SPEC = ROOT / "verification" / "trefoil_junctions.json"

CORNERS = ("000", "001", "010", "011", "100", "101", "110", "111")
PAIR_AXES = {
    "AB": (0, 1, 2),
    "BC": (1, 2, 0),
    "CA": (2, 0, 1),
}


def standing_authority() -> StandingAuthority:
    return StandingAuthority(
        authority_id="trefoil-standing",
        allowed_actions=("trefoil",),
        max_scope=RiskLevel.CRITICAL,
        allow_external_write=True,
        allow_audience_change=True,
        allow_privacy_change=True,
        allow_authority_expansion=True,
    )


def state_for(defaults: dict, junction: dict, key: str) -> dict:
    state = {**defaults, **junction.get("base", {})}
    for factor, bit in zip(junction["factors"], key, strict=True):
        state[factor["field"]] = factor["on"] if bit == "1" else factor["off"]
    return state


def assessment_for(label: str, state: dict):
    payload = {
        "action_id": label,
        "action_class": "trefoil",
        "description": "Three-way junction witness.",
        **{k: v for k, v in state.items() if k != "standing_authorized"},
        "tags": ["trefoil-junction"],
    }
    authority = standing_authority() if state["standing_authorized"] else None
    return assess_action(ActionIntent.from_dict(payload), authority)


def flip(key: str, axis: int, value: str) -> str:
    chars = list(key)
    chars[axis] = value
    return "".join(chars)


def pair_second_differences(ordinals: dict[str, int], a: int, b: int, fixed: int) -> list[int]:
    out: list[int] = []
    for fixed_value in ("0", "1"):
        base = ["0", "0", "0"]
        base[fixed] = fixed_value
        k00 = "".join(base)
        k10 = flip(k00, a, "1")
        k01 = flip(k00, b, "1")
        k11 = flip(k10, b, "1")
        out.append(ordinals[k11] - ordinals[k10] - ordinals[k01] + ordinals[k00])
    return out


def third_order_residual(ordinals: dict[str, int]) -> int:
    return (
        ordinals["111"]
        - ordinals["110"]
        - ordinals["101"]
        - ordinals["011"]
        + ordinals["100"]
        + ordinals["010"]
        + ordinals["001"]
        - ordinals["000"]
    )


def classify(linked_pairs: set[str], third: int) -> str:
    if linked_pairs == {"AB", "BC", "CA"} and third != 0:
        return "trefoil_like"
    if not linked_pairs and third == 0:
        return "unknot_control"
    if len(linked_pairs) == 1 and third == 0:
        return "detached_strand_control"
    return "other"


def main() -> int:
    errors: list[str] = []
    doc = json.loads(SPEC.read_text(encoding="utf-8"))
    if doc.get("schema_version") != 1:
        errors.append(f"unsupported trefoil schema_version: {doc.get('schema_version')!r}")

    defaults = doc.get("defaults", {})
    gate_ordinals = doc.get("gate_ordinals", {})
    halt_gates = set(doc.get("halt_gates", []))
    required_classes = set(doc.get("required_topology_classes", []))
    junctions = doc.get("junctions", [])
    ids = [j.get("id") for j in junctions]
    if len(ids) != len(set(ids)):
        errors.append("duplicate trefoil junction IDs")

    observed_classes: set[str] = set()

    for junction in junctions:
        jid = junction.get("id", "<missing>")
        factors = junction.get("factors", [])
        if len(factors) != 3:
            errors.append(f"{jid}: junction must declare exactly three factors")
            continue
        fields = [f.get("field") for f in factors]
        if len(set(fields)) != 3 or any(not f for f in fields):
            errors.append(f"{jid}: factors must name three distinct fields")
        for factor in factors:
            if factor.get("off") == factor.get("on"):
                errors.append(f"{jid}: factor {factor.get('field')} has identical off/on values")

        expected = junction.get("expected", {})
        if set(expected) != set(CORNERS):
            errors.append(f"{jid}: expected must define all eight cube corners")
            continue

        states = {key: state_for(defaults, junction, key) for key in CORNERS}
        projected = {
            key: tuple(states[key][field] for field in fields)
            for key in CORNERS
        }
        if len(set(projected.values())) != 8:
            errors.append(f"{jid}: cube does not realize eight distinct factor corners")

        nonfactor = set(defaults) - set(fields)
        baseline = states["000"]
        for key, state in states.items():
            changed_elsewhere = {f for f in nonfactor if state[f] != baseline[f]}
            if changed_elsewhere:
                errors.append(f"{jid}:{key}: changes non-factor coordinates {sorted(changed_elsewhere)}")

        assessments = {key: assessment_for(f"{jid}:{key}", state) for key, state in states.items()}
        gates = {key: assessments[key].gate.label() for key in CORNERS}
        for key in CORNERS:
            if gates[key] != expected[key]:
                errors.append(f"{jid}:{key}: expected {expected[key]}, got {gates[key]}")

        try:
            ordinals = {key: int(gate_ordinals[gates[key]]) for key in CORNERS}
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{jid}: invalid gate ordinal encoding: {exc}")
            continue

        pair_diffs = {
            pair: pair_second_differences(ordinals, *axes)
            for pair, axes in PAIR_AXES.items()
        }
        linked_pairs = {pair for pair, diffs in pair_diffs.items() if any(value != 0 for value in diffs)}
        third = third_order_residual(ordinals)
        actual_class = classify(linked_pairs, third)
        declared_class = junction.get("topology_class")
        observed_classes.add(declared_class)
        if actual_class != declared_class:
            errors.append(
                f"{jid}: topology class expected {declared_class}, computed {actual_class}; "
                f"linked_pairs={sorted(linked_pairs)}, third={third}"
            )

        signature = junction.get("interaction_signature", {})
        if set(signature.get("linked_pairs", [])) != linked_pairs:
            errors.append(
                f"{jid}: linked-pair signature mismatch: declared {sorted(signature.get('linked_pairs', []))}, "
                f"computed {sorted(linked_pairs)}"
            )
        if signature.get("third_order_residual") != third:
            errors.append(
                f"{jid}: third-order residual expected {signature.get('third_order_residual')}, got {third}"
            )

        stop = junction.get("stop_condition", {})
        if not str(stop.get("interpretation", "")).strip():
            errors.append(f"{jid}: stop condition lacks interpretation")
        actual_halts = {key for key, gate in gates.items() if gate in halt_gates}
        required_halts = set(stop.get("required_halt_corners", []))
        if actual_halts != required_halts:
            errors.append(
                f"{jid}: halt corners expected {sorted(required_halts)}, got {sorted(actual_halts)}"
            )

        for kind, should_release in (("release_edges", True), ("nonrelease_edges", False)):
            for edge in stop.get(kind, []):
                source = edge.get("from")
                target = edge.get("to")
                factor = edge.get("factor")
                if source not in CORNERS or target not in CORNERS:
                    errors.append(f"{jid}: malformed {kind} corner {source}->{target}")
                    continue
                differences = [i for i in range(3) if source[i] != target[i]]
                if len(differences) != 1:
                    errors.append(f"{jid}: {kind} edge {source}->{target} must change exactly one factor")
                    continue
                axis = differences[0]
                if factors[axis].get("label") != factor:
                    errors.append(
                        f"{jid}: {kind} edge {source}->{target} claims factor {factor!r}, "
                        f"actually changes {factors[axis].get('label')!r}"
                    )
                source_halt = gates[source] in halt_gates
                target_halt = gates[target] in halt_gates
                if not source_halt:
                    errors.append(f"{jid}: {kind} source {source} is not a halt corner")
                if should_release and target_halt:
                    errors.append(f"{jid}: release edge {source}->{target} does not leave halt surface")
                if not should_release and not target_halt:
                    errors.append(f"{jid}: nonrelease edge {source}->{target} unexpectedly leaves halt surface")

    missing_classes = required_classes - observed_classes
    if missing_classes:
        errors.append(f"trefoil surface missing topology classes: {sorted(missing_classes)}")

    if errors:
        print("TREFOIL JUNCTION CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "TREFOIL JUNCTION CHECK: PASS — "
        f"{len(junctions)} complete 2x2x2 junctions across {len(required_classes)} topology classes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
