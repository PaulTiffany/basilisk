"""Finite exemplar: capability can grow while observer reachability shrinks.

The model is intentionally neutral about the real-world source that inspired it.
It mechanically witnesses finite relations among capabilities, access
requirements, urban coordination structure, and a preserved ledger.

An optional mythic reading may map the three surfaces to Garden, fallen city,
and New Jerusalem / Garden-City. That reading is not part of the certificate.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Affordance:
    name: str
    route: str
    requirements: frozenset[str] = frozenset()

    @property
    def ledger_gated(self) -> bool:
        return any(requirement.startswith("ledger:") for requirement in self.requirements)


@dataclass(frozen=True)
class LedgerEntry:
    event_id: str
    event: str


@dataclass(frozen=True)
class Surface:
    name: str
    affordances: tuple[Affordance, ...]
    coordination_edges: tuple[tuple[str, str], ...] = ()
    ledger: tuple[LedgerEntry, ...] = ()

    @property
    def capability_count(self) -> int:
        return len(self.affordances)

    @property
    def urban(self) -> bool:
        return bool(self.coordination_edges) and all(
            affordance.route != "direct" for affordance in self.affordances
        )

    def reachable(self, held: frozenset[str]) -> tuple[str, ...]:
        return tuple(
            affordance.name
            for affordance in self.affordances
            if affordance.requirements <= held
        )

    def blocked_requirements(self, held: frozenset[str]) -> int:
        return sum(
            len(affordance.requirements - held)
            for affordance in self.affordances
        )

    def ledger_gated_affordances(self) -> tuple[str, ...]:
        return tuple(
            affordance.name for affordance in self.affordances if affordance.ledger_gated
        )

    def urban_signature(self) -> tuple[tuple[str, str], ...]:
        return tuple((affordance.name, affordance.route) for affordance in self.affordances)


def build_surfaces() -> tuple[Surface, Surface, Surface, frozenset[str]]:
    observer_resources = frozenset({"public_access"})

    direct = Surface(
        "direct",
        (
            Affordance("food", "direct"),
            Affordance("water", "direct"),
            Affordance("shelter", "direct"),
            Affordance("kinship", "direct"),
        ),
    )

    city_ledger = (
        LedgerEntry("e1", "arrival"),
        LedgerEntry("e2", "contract_entered"),
        LedgerEntry("e3", "payment_missed"),
    )
    city_edges = (
        ("food", "movement"),
        ("water", "shelter"),
        ("shelter", "movement"),
        ("communication", "movement"),
        ("public_space", "communication"),
    )

    mediated = Surface(
        "mediated_city",
        (
            Affordance("food", "market", frozenset({"money"})),
            Affordance("water", "utility", frozenset({"money"})),
            Affordance(
                "shelter",
                "registry",
                frozenset({"money", "contract", "ledger:clear_history"}),
            ),
            Affordance("movement", "transit", frozenset({"money"})),
            Affordance("communication", "network", frozenset({"money", "device"})),
            Affordance("public_space", "civic", frozenset({"public_access"})),
        ),
        coordination_edges=city_edges,
        ledger=city_ledger,
    )

    healed = Surface(
        "healed_city",
        (
            Affordance("food", "market", frozenset({"public_access"})),
            Affordance("water", "utility", frozenset({"public_access"})),
            Affordance("shelter", "registry", frozenset({"public_access"})),
            Affordance("movement", "transit", frozenset({"public_access"})),
            Affordance("communication", "network", frozenset({"public_access"})),
            Affordance("public_space", "civic", frozenset({"public_access"})),
        ),
        coordination_edges=city_edges,
        ledger=city_ledger,
    )

    return direct, mediated, healed, observer_resources


def witness() -> dict[str, object]:
    direct, mediated, healed, held = build_surfaces()

    direct_reachable = direct.reachable(held)
    mediated_reachable = mediated.reachable(held)
    healed_reachable = healed.reachable(held)

    return {
        "kind": "finite_affordance_surface_witness",
        "observer_resources": sorted(held),
        "surfaces": {
            direct.name: {
                "capabilities": direct.capability_count,
                "reachable": len(direct_reachable),
                "reachable_actions": list(direct_reachable),
                "blocked_requirement_count": direct.blocked_requirements(held),
                "urban": direct.urban,
                "urban_signature": list(direct.urban_signature()),
                "coordination_edges": list(direct.coordination_edges),
                "ledger": [entry.__dict__ for entry in direct.ledger],
                "ledger_gated_actions": list(direct.ledger_gated_affordances()),
            },
            mediated.name: {
                "capabilities": mediated.capability_count,
                "reachable": len(mediated_reachable),
                "reachable_actions": list(mediated_reachable),
                "blocked_requirement_count": mediated.blocked_requirements(held),
                "urban": mediated.urban,
                "urban_signature": list(mediated.urban_signature()),
                "coordination_edges": list(mediated.coordination_edges),
                "ledger": [entry.__dict__ for entry in mediated.ledger],
                "ledger_gated_actions": list(mediated.ledger_gated_affordances()),
            },
            healed.name: {
                "capabilities": healed.capability_count,
                "reachable": len(healed_reachable),
                "reachable_actions": list(healed_reachable),
                "blocked_requirement_count": healed.blocked_requirements(held),
                "urban": healed.urban,
                "urban_signature": list(healed.urban_signature()),
                "coordination_edges": list(healed.coordination_edges),
                "ledger": [entry.__dict__ for entry in healed.ledger],
                "ledger_gated_actions": list(healed.ledger_gated_affordances()),
            },
        },
        "mechanical_claims": {
            "capability_can_increase_while_reachability_decreases": (
                mediated.capability_count > direct.capability_count
                and len(mediated_reachable) < len(direct_reachable)
            ),
            "reachability_can_be_restored_without_capability_loss": (
                healed.capability_count == mediated.capability_count
                and len(healed_reachable) > len(mediated_reachable)
            ),
            "restoration_preserves_city_structure": (
                healed.urban
                and mediated.urban
                and healed.urban_signature() == mediated.urban_signature()
                and healed.coordination_edges == mediated.coordination_edges
            ),
            "ledger_history_is_preserved_without_remaining_an_access_gate": (
                healed.ledger == mediated.ledger
                and bool(mediated.ledger_gated_affordances())
                and not healed.ledger_gated_affordances()
            ),
            "restoration_is_not_a_return_to_the_direct_surface": (
                healed.urban
                and not direct.urban
                and healed.urban_signature() != direct.urban_signature()
            ),
        },
        "certificate_scope": {
            "certifies": [
                "the finite counts and set-membership relations encoded here",
                "a counterexample to the implication: more modeled capability => more modeled observer reachability",
                "that the modeled healed state preserves the modeled city's routes, coordination graph, and ledger",
                "that the preserved modeled ledger need not remain an access-control predicate",
                "that modeled restored reachability need not mean returning to the modeled direct surface",
            ],
            "does_not_certify": [
                "that any real jungle or city has these affordances",
                "that money, contracts, credentials, devices, or historical records are intrinsically harmful",
                "that real institutions should remove any particular eligibility or safety requirement",
                "that preserved provenance is itself true, complete, or morally authoritative",
                "that the Bible predicts this model",
                "that the optional Garden / fallen city / New Jerusalem mask is uniquely correct",
            ],
        },
    }


def main() -> None:
    result = witness()
    assert all(result["mechanical_claims"].values())  # type: ignore[union-attr]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
