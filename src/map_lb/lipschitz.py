from __future__ import annotations

from dataclasses import dataclass

from .types import ActionGate, ActionIntent


@dataclass(frozen=True)
class PairCheck:
    context_distance: float
    gate_distance: float
    bound: float
    passed: bool
    changed_features: tuple[str, ...]


_FEATURE_WEIGHTS: dict[str, float] = {
    "within_contract": 3.0,
    "hard_boundary_violation": 3.0,
    "current_turn_explicit_authorization": 2.0,
    "reversible": 2.0,
    "rollback_available": 1.0,
    "inspectable": 1.0,
    "material_change": 0.5,
    "affects_external_system": 2.0,
    "audience_change": 2.0,
    "privacy_change": 2.0,
    "authority_expansion": 2.5,
    "scope": 1.0,
    "uncertainty": 0.75,
    "judgment_mode": 2.0,
    "judgment_requested": 1.5,
    "concrete_immediate_safety_risk": 2.0,
    "destructive": 2.0,
}


def intent_distance(left: ActionIntent, right: ActionIntent) -> tuple[float, tuple[str, ...]]:
    changed: list[str] = []
    distance = 0.0
    for feature, weight in _FEATURE_WEIGHTS.items():
        lv = getattr(left, feature)
        rv = getattr(right, feature)
        if lv == rv:
            continue
        changed.append(feature)
        if feature in {"scope", "uncertainty"}:
            distance += weight * abs(int(lv) - int(rv))
        else:
            distance += weight
    return distance, tuple(changed)


def check_pair(
    left: ActionIntent,
    left_gate: ActionGate,
    right: ActionIntent,
    right_gate: ActionGate,
    *,
    lipschitz_constant: float = 1.0,
    slack: float = 0.0,
) -> PairCheck:
    context_distance, changed = intent_distance(left, right)
    gate_distance = float(abs(int(left_gate) - int(right_gate)))
    bound = lipschitz_constant * context_distance + slack
    return PairCheck(
        context_distance=context_distance,
        gate_distance=gate_distance,
        bound=bound,
        passed=gate_distance <= bound,
        changed_features=changed,
    )
