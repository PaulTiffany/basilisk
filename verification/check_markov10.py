#!/usr/bin/env python3
"""Finite mechanistic witness for the Markov 10+ research bridge.

This does not implement Newton polyhedra or claim the algebraic bridge. It checks
three prior obligations on finite weighted transition systems:

1. horizon composition is mechanically visible in accumulated support;
2. normalized convex geometry can stabilize while individual horizon supports
   keep changing;
3. stable normalized geometry can still collapse protected semantic labels, so
   an independent faithfulness witness remains necessary.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
from typing import Iterable

Vector = tuple[int, int]
QVector = tuple[Fraction, Fraction]


@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    label: str
    delta: Vector


@dataclass(frozen=True)
class WeightedSystem:
    transitions: tuple[Transition, ...]

    def outgoing(self, state: str) -> tuple[Transition, ...]:
        return tuple(t for t in self.transitions if t.source == state)


def add(a: Vector, b: Vector) -> Vector:
    return (a[0] + b[0], a[1] + b[1])


def path_support(system: WeightedSystem, start: str, horizon: int) -> set[Vector]:
    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    frontier: set[tuple[str, Vector]] = {(start, (0, 0))}
    for _ in range(horizon):
        next_frontier: set[tuple[str, Vector]] = set()
        for state, total in frontier:
            for transition in system.outgoing(state):
                next_frontier.add((transition.target, add(total, transition.delta)))
        frontier = next_frontier
    return {total for _state, total in frontier}


def minkowski(left: Iterable[Vector], right: Iterable[Vector]) -> set[Vector]:
    return {add(a, b) for a in left for b in right}


def normalize(point: Vector, horizon: int) -> QVector:
    if horizon <= 0:
        raise ValueError("normalization requires a positive horizon")
    return (Fraction(point[0], horizon), Fraction(point[1], horizon))


def cross(o: QVector, a: QVector, b: QVector) -> Fraction:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points: Iterable[QVector]) -> tuple[QVector, ...]:
    pts = sorted(set(points))
    if len(pts) <= 1:
        return tuple(pts)
    lower: list[QVector] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[QVector] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return tuple(lower[:-1] + upper[:-1])


def normalized_hull(system: WeightedSystem, start: str, horizon: int) -> tuple[QVector, ...]:
    return convex_hull(normalize(p, horizon) for p in path_support(system, start, horizon))


def encoding_is_injective_on_labels(system: WeightedSystem) -> bool:
    label_to_delta: dict[str, Vector] = {}
    for transition in system.transitions:
        previous = label_to_delta.get(transition.label)
        if previous is not None and previous != transition.delta:
            raise ValueError(f"label {transition.label!r} has inconsistent deltas")
        label_to_delta[transition.label] = transition.delta
    return len(set(label_to_delta.values())) == len(label_to_delta)


def qvector_json(points: tuple[QVector, ...]) -> list[list[str]]:
    return [[str(x), str(y)] for x, y in points]


LINEAR = WeightedSystem((Transition("s", "s", "advance", (1, 2)),))
BRANCHING = WeightedSystem(
    (
        Transition("s", "s", "left", (1, 0)),
        Transition("s", "s", "right", (0, 1)),
    )
)
COLLAPSED = WeightedSystem(
    (
        Transition("s", "s", "protected_0", (1, 0)),
        Transition("s", "s", "protected_1", (1, 0)),
    )
)


def build_witness() -> dict:
    p, q = 2, 3
    linear_p = path_support(LINEAR, "s", p)
    linear_q = path_support(LINEAR, "s", q)
    linear_pq = path_support(LINEAR, "s", p + q)
    linear_composes = minkowski(linear_p, linear_q) == linear_pq

    linear_hulls = [normalized_hull(LINEAR, "s", n) for n in range(1, 6)]
    linear_stable = all(h == linear_hulls[0] for h in linear_hulls[1:])

    branching_support_2 = path_support(BRANCHING, "s", 2)
    branching_support_3 = path_support(BRANCHING, "s", 3)
    branching_hulls = [normalized_hull(BRANCHING, "s", n) for n in range(1, 6)]
    branching_hull_stable = all(h == branching_hulls[0] for h in branching_hulls[1:])

    collapsed_faithful = encoding_is_injective_on_labels(COLLAPSED)

    return {
        "kind": "finite_markov10_bridge_witness",
        "claim_boundary": "finite transition/support geometry only; not a Newton-polyhedron or graded-ideal theorem",
        "linear": {
            "horizons": [p, q, p + q],
            "composition_support_equal": linear_composes,
            "normalized_hull_stable_1_to_5": linear_stable,
            "normalized_hull": qvector_json(linear_hulls[0]),
        },
        "branching": {
            "support_changes_between_2_and_3": branching_support_2 != branching_support_3,
            "support_size_h2": len(branching_support_2),
            "support_size_h3": len(branching_support_3),
            "normalized_hull_stable_1_to_5": branching_hull_stable,
            "normalized_hull": qvector_json(branching_hulls[0]),
        },
        "faithfulness_guard": {
            "distinct_protected_labels": 2,
            "distinct_encoded_vectors": len({t.delta for t in COLLAPSED.transitions}),
            "encoding_injective_on_labels": collapsed_faithful,
            "collapse_detected": not collapsed_faithful,
        },
    }


def main() -> int:
    witness = build_witness()
    print(json.dumps(witness, indent=2, sort_keys=True))
    ok = (
        witness["linear"]["composition_support_equal"]
        and witness["linear"]["normalized_hull_stable_1_to_5"]
        and witness["branching"]["support_changes_between_2_and_3"]
        and witness["branching"]["normalized_hull_stable_1_to_5"]
        and witness["faithfulness_guard"]["collapse_detected"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
