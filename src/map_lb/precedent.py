from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping


class ExecutionPhase(str, Enum):
    INITIALIZING = "initializing"
    TRANSIENT = "transient"
    STEADY = "steady"
    TERMINAL = "terminal"
    FAULT = "fault"


def _coerce_phase(value: ExecutionPhase | str) -> ExecutionPhase:
    if isinstance(value, ExecutionPhase):
        return value
    try:
        return ExecutionPhase(value)
    except ValueError as exc:
        raise ValueError(f"unknown execution phase: {value!r}") from exc


@dataclass(frozen=True)
class TrajectoryPrecedent:
    """A paired trajectory witness used to price entry into known bad basins.

    The precedent is not a natural-language rule. ``structural_signature`` is a
    set of typed trajectory features used for retrieval; ``applicable_phases``
    prevents state-only matching from collapsing initialization, steady-state,
    and fault behavior; and ``hard_stop_features`` remain outside Bellman
    optimization.
    """

    precedent_id: str
    contract: str
    structural_signature: frozenset[str]
    divergence_point: str
    negative_trace: tuple[str, ...]
    positive_trace: tuple[str, ...]
    consequence_coordinates: tuple[str, ...]
    input_distance: float
    consequence_distance: float
    lipschitz_constant: float
    applicable_phases: frozenset[ExecutionPhase] = frozenset(ExecutionPhase)
    slack: float = 0.0
    damage_weight: float = 1.0
    hard_stop_features: frozenset[str] = frozenset()
    bounded_alternative: str = ""
    provenance: str = ""

    def __post_init__(self) -> None:
        if not self.precedent_id:
            raise ValueError("precedent_id must be non-empty")
        if not self.contract:
            raise ValueError("contract must be non-empty")
        if not self.applicable_phases:
            raise ValueError("applicable_phases must be non-empty")
        for name, value in (
            ("input_distance", self.input_distance),
            ("consequence_distance", self.consequence_distance),
            ("lipschitz_constant", self.lipschitz_constant),
            ("slack", self.slack),
            ("damage_weight", self.damage_weight),
        ):
            if value < 0:
                raise ValueError(f"{name} must be non-negative")

    @property
    def lipschitz_bound(self) -> float:
        return self.lipschitz_constant * self.input_distance + self.slack

    @property
    def excess_amplification(self) -> float:
        """Witnessed output motion beyond the admitted Lipschitz bound."""

        return max(0.0, self.consequence_distance - self.lipschitz_bound)

    def applies_in(self, phase: ExecutionPhase | str) -> bool:
        return _coerce_phase(phase) in self.applicable_phases

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "TrajectoryPrecedent":
        required = {
            "precedent_id",
            "contract",
            "structural_signature",
            "divergence_point",
            "negative_trace",
            "positive_trace",
            "consequence_coordinates",
            "input_distance",
            "consequence_distance",
            "lipschitz_constant",
            "applicable_phases",
        }
        missing = required - set(data)
        if missing:
            raise ValueError(f"precedent missing fields: {sorted(missing)}")

        def strings(name: str) -> tuple[str, ...]:
            value = data[name]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise TypeError(f"precedent field {name!r} must be a list of strings")
            return tuple(value)

        def number(name: str, default: float | None = None) -> float:
            value = data.get(name, default)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"precedent field {name!r} must be numeric")
            return float(value)

        precedent_id = data["precedent_id"]
        contract = data["contract"]
        divergence_point = data["divergence_point"]
        bounded_alternative = data.get("bounded_alternative", "")
        provenance = data.get("provenance", "")
        for name, value in (
            ("precedent_id", precedent_id),
            ("contract", contract),
            ("divergence_point", divergence_point),
            ("bounded_alternative", bounded_alternative),
            ("provenance", provenance),
        ):
            if not isinstance(value, str):
                raise TypeError(f"precedent field {name!r} must be a string")

        hard_stop_raw = data.get("hard_stop_features", [])
        if not isinstance(hard_stop_raw, list) or not all(
            isinstance(item, str) for item in hard_stop_raw
        ):
            raise TypeError("precedent field 'hard_stop_features' must be a list of strings")

        phase_values = strings("applicable_phases")
        phases = frozenset(_coerce_phase(value) for value in phase_values)

        return cls(
            precedent_id=precedent_id,
            contract=contract,
            structural_signature=frozenset(strings("structural_signature")),
            divergence_point=divergence_point,
            negative_trace=strings("negative_trace"),
            positive_trace=strings("positive_trace"),
            consequence_coordinates=strings("consequence_coordinates"),
            input_distance=number("input_distance"),
            consequence_distance=number("consequence_distance"),
            lipschitz_constant=number("lipschitz_constant"),
            applicable_phases=phases,
            slack=number("slack", 0.0),
            damage_weight=number("damage_weight", 1.0),
            hard_stop_features=frozenset(hard_stop_raw),
            bounded_alternative=bounded_alternative,
            provenance=provenance,
        )


@dataclass(frozen=True)
class PrecedentMatch:
    precedent_id: str
    similarity: float
    excess_amplification: float
    surcharge: float


@dataclass(frozen=True)
class PrecedentPrice:
    resource_shadow_cost: float
    trajectory_surcharge: float
    total_penalty: float
    hard_stop: bool
    matches: tuple[PrecedentMatch, ...]


@dataclass(frozen=True)
class BellmanActionValue:
    admissible: bool
    value: float | None
    price: PrecedentPrice


def structural_similarity(
    observed_signature: Iterable[str],
    precedent_signature: Iterable[str],
) -> float:
    """Jaccard similarity over structural trajectory features."""

    observed = frozenset(observed_signature)
    precedent = frozenset(precedent_signature)
    if not observed and not precedent:
        return 1.0
    union = observed | precedent
    if not union:
        return 0.0
    return len(observed & precedent) / len(union)


def _non_negative_mapping(name: str, values: Mapping[str, float]) -> None:
    for key, value in values.items():
        if value < 0:
            raise ValueError(f"{name}[{key!r}] must be non-negative")


def price_action(
    *,
    phase: ExecutionPhase | str,
    resource_costs: Mapping[str, float],
    shadow_prices: Mapping[str, float],
    observed_signature: Iterable[str],
    precedents: Iterable[TrajectoryPrecedent],
    min_similarity: float = 0.5,
) -> PrecedentPrice:
    """Price resources plus phase-correct structurally retrieved precedent risk.

    Hard-stop features are checked before precedent phase filtering because a
    constitutional halt such as practical loss of interruptibility is not made
    negotiable by classifying the process as initialization.
    """

    if not 0.0 <= min_similarity <= 1.0:
        raise ValueError("min_similarity must be between 0 and 1")
    _non_negative_mapping("resource_costs", resource_costs)
    _non_negative_mapping("shadow_prices", shadow_prices)

    phase_value = _coerce_phase(phase)
    signature = frozenset(observed_signature)
    resource_shadow_cost = sum(
        cost * shadow_prices.get(resource, 0.0)
        for resource, cost in resource_costs.items()
    )

    matches: list[PrecedentMatch] = []
    trajectory_surcharge = 0.0
    hard_stop = False

    for precedent in precedents:
        if precedent.hard_stop_features and precedent.hard_stop_features <= signature:
            hard_stop = True
        if phase_value not in precedent.applicable_phases:
            continue

        similarity = structural_similarity(signature, precedent.structural_signature)
        if similarity < min_similarity:
            continue
        surcharge = similarity * precedent.excess_amplification * precedent.damage_weight
        trajectory_surcharge += surcharge
        matches.append(
            PrecedentMatch(
                precedent_id=precedent.precedent_id,
                similarity=similarity,
                excess_amplification=precedent.excess_amplification,
                surcharge=surcharge,
            )
        )

    matches.sort(key=lambda match: (-match.surcharge, -match.similarity, match.precedent_id))
    total_penalty = resource_shadow_cost + trajectory_surcharge
    return PrecedentPrice(
        resource_shadow_cost=resource_shadow_cost,
        trajectory_surcharge=trajectory_surcharge,
        total_penalty=total_penalty,
        hard_stop=hard_stop,
        matches=tuple(matches),
    )


def bellman_action_value(
    *,
    phase: ExecutionPhase | str,
    immediate_reward: float,
    continuation_value: float,
    discount: float,
    resource_costs: Mapping[str, float],
    shadow_prices: Mapping[str, float],
    observed_signature: Iterable[str],
    precedents: Iterable[TrajectoryPrecedent],
    min_similarity: float = 0.5,
) -> BellmanActionValue:
    """Return reward + discounted continuation minus constitutional prices."""

    if not 0.0 <= discount <= 1.0:
        raise ValueError("discount must be between 0 and 1")
    price = price_action(
        phase=phase,
        resource_costs=resource_costs,
        shadow_prices=shadow_prices,
        observed_signature=observed_signature,
        precedents=precedents,
        min_similarity=min_similarity,
    )
    if price.hard_stop:
        return BellmanActionValue(admissible=False, value=None, price=price)
    value = immediate_reward + discount * continuation_value - price.total_penalty
    return BellmanActionValue(admissible=True, value=value, price=price)
