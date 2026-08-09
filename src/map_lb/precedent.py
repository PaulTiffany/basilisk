from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class TrajectoryPrecedent:
    """A paired trajectory witness used to price entry into known bad basins.

    The precedent is not a natural-language rule. ``structural_signature`` is a
    set of typed trajectory features used for retrieval; the Lipschitz fields
    record the witnessed geometry; and ``hard_stop_features`` remain outside
    Bellman optimization.
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
    """Jaccard similarity over structural trajectory features.

    Retrieval is deliberately feature-based rather than keyword- or prose-based.
    """

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
    resource_costs: Mapping[str, float],
    shadow_prices: Mapping[str, float],
    observed_signature: Iterable[str],
    precedents: Iterable[TrajectoryPrecedent],
    min_similarity: float = 0.5,
) -> PrecedentPrice:
    """Price resources plus structurally retrieved precedent risk.

    ``shadow_prices`` implement the Bellman marginal value of scarce resources.
    Precedent surcharge is similarity times the witnessed Lipschitz excess times
    a declared damage weight. Hard-stop features are checked separately and are
    never traded away for reward.
    """

    if not 0.0 <= min_similarity <= 1.0:
        raise ValueError("min_similarity must be between 0 and 1")
    _non_negative_mapping("resource_costs", resource_costs)
    _non_negative_mapping("shadow_prices", shadow_prices)

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

        similarity = structural_similarity(signature, precedent.structural_signature)
        if similarity < min_similarity:
            continue
        surcharge = (
            similarity
            * precedent.excess_amplification
            * precedent.damage_weight
        )
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
    immediate_reward: float,
    continuation_value: float,
    discount: float,
    resource_costs: Mapping[str, float],
    shadow_prices: Mapping[str, float],
    observed_signature: Iterable[str],
    precedents: Iterable[TrajectoryPrecedent],
    min_similarity: float = 0.5,
) -> BellmanActionValue:
    """Return reward + discounted continuation minus constitutional prices.

    A hard stop yields ``value=None`` so callers cannot accidentally optimize
    through a constitutional halt by assigning it a sufficiently large reward.
    """

    if not 0.0 <= discount <= 1.0:
        raise ValueError("discount must be between 0 and 1")
    price = price_action(
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
