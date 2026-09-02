"""Finite exemplar: capability, reachability, architecture, privacy, and provenance.

The model is intentionally neutral about the real-world source that inspired it.
It mechanically witnesses finite relations among capabilities, access
requirements, a composed city architecture, private interiors, mutual
self-association, and a preserved ledger.

An optional mythic reading may map the three surfaces to Garden, fallen city,
and New Jerusalem / Garden-City. That reading is not part of the certificate.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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
class CivicUnit:
    """A bounded interior with public ports and self-declared associations."""

    name: str
    public_ports: frozenset[str]
    private_state: tuple[tuple[str, str], ...]
    declared_associations: frozenset[str]


@dataclass(frozen=True)
class Association:
    """A typed public connection between two bounded civic units."""

    name: str
    left: str
    left_port: str
    right: str
    right_port: str
    kind: str


@dataclass(frozen=True)
class CityArchitecture:
    units: tuple[CivicUnit, ...]
    associations: tuple[Association, ...]

    def unit_map(self) -> dict[str, CivicUnit]:
        return {unit.name: unit for unit in self.units}

    def association_map(self) -> dict[str, Association]:
        return {association.name: association for association in self.associations}

    def association_valid(self, association: Association) -> bool:
        units = self.unit_map()
        if association.left not in units or association.right not in units:
            return False
        left = units[association.left]
        right = units[association.right]
        return (
            association.left_port in left.public_ports
            and association.right_port in right.public_ports
            and association.name in left.declared_associations
            and association.name in right.declared_associations
        )

    def all_associations_self_authorized(self) -> bool:
        return all(self.association_valid(association) for association in self.associations)

    def public_view(self) -> dict[str, object]:
        """Expose ports and associations without serializing private interiors."""
        return {
            "units": [
                {"name": unit.name, "public_ports": sorted(unit.public_ports)}
                for unit in self.units
            ],
            "associations": [
                {
                    "name": association.name,
                    "left": association.left,
                    "left_port": association.left_port,
                    "right": association.right,
                    "right_port": association.right_port,
                    "kind": association.kind,
                }
                for association in self.associations
            ],
        }

    def private_interiors_hidden(self) -> bool:
        public = json.dumps(self.public_view(), sort_keys=True)
        private_tokens = {
            token
            for unit in self.units
            for pair in unit.private_state
            for token in pair
        }
        return all(token not in public for token in private_tokens)

    def connected(self) -> bool:
        if not self.units:
            return False

        adjacency = {unit.name: set() for unit in self.units}
        for association in self.associations:
            if not self.association_valid(association):
                continue
            adjacency[association.left].add(association.right)
            adjacency[association.right].add(association.left)

        start = self.units[0].name
        seen = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency[current] - seen:
                seen.add(neighbor)
                frontier.append(neighbor)
        return len(seen) == len(self.units)

    def has_market_loop(self) -> bool:
        """Household -> market -> transit -> household."""
        names = {"food_exchange", "market_logistics", "household_transit"}
        associations = self.association_map()
        return names <= set(associations) and all(
            self.association_valid(associations[name]) for name in names
        )

    def has_utility_delivery(self) -> bool:
        associations = self.association_map()
        return (
            "water_service" in associations
            and self.association_valid(associations["water_service"])
        )

    def has_communications_path(self) -> bool:
        associations = self.association_map()
        return (
            "communications" in associations
            and self.association_valid(associations["communications"])
        )

    def coherent(self) -> bool:
        return (
            self.all_associations_self_authorized()
            and self.private_interiors_hidden()
            and self.connected()
            and self.has_market_loop()
            and self.has_utility_delivery()
            and self.has_communications_path()
        )

    def architectural_signature(self) -> dict[str, object]:
        return self.public_view()


@dataclass(frozen=True)
class Surface:
    name: str
    affordances: tuple[Affordance, ...]
    architecture: CityArchitecture | None = None
    ledger: tuple[LedgerEntry, ...] = ()

    @property
    def capability_count(self) -> int:
        return len(self.affordances)

    @property
    def urban(self) -> bool:
        return self.architecture is not None and self.architecture.coherent()

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
            affordance.name
            for affordance in self.affordances
            if affordance.ledger_gated
        )


def build_city_architecture() -> CityArchitecture:
    units = (
        CivicUnit(
            "household",
            frozenset(
                {
                    "buyer",
                    "water_sink",
                    "rider",
                    "network_endpoint",
                    "civic_member",
                    "resident",
                }
            ),
            (("household_secret", "kept_local"),),
            frozenset(
                {
                    "food_exchange",
                    "household_transit",
                    "water_service",
                    "communications",
                    "civic_membership",
                    "residency",
                }
            ),
        ),
        CivicUnit(
            "market",
            frozenset({"seller", "freight"}),
            (("merchant_books", "private_market_state"),),
            frozenset({"food_exchange", "market_logistics"}),
        ),
        CivicUnit(
            "transit",
            frozenset({"rider", "freight"}),
            (("routing_state", "private_transit_state"),),
            frozenset({"market_logistics", "household_transit"}),
        ),
        CivicUnit(
            "utility",
            frozenset({"water_source", "service"}),
            (("reservoir_state", "private_utility_state"),),
            frozenset({"water_service"}),
        ),
        CivicUnit(
            "network",
            frozenset({"network_endpoint", "service"}),
            (("network_keys", "private_network_state"),),
            frozenset({"communications"}),
        ),
        CivicUnit(
            "civic",
            frozenset({"civic_member", "public_space"}),
            (("deliberation_notes", "private_civic_state"),),
            frozenset({"civic_membership"}),
        ),
        CivicUnit(
            "registry",
            frozenset({"resident", "record"}),
            (("registry_interior", "private_registry_state"),),
            frozenset({"residency"}),
        ),
    )

    associations = (
        Association(
            "food_exchange",
            "household",
            "buyer",
            "market",
            "seller",
            "market",
        ),
        Association(
            "market_logistics",
            "market",
            "freight",
            "transit",
            "freight",
            "road",
        ),
        Association(
            "household_transit",
            "transit",
            "rider",
            "household",
            "rider",
            "road",
        ),
        Association(
            "water_service",
            "utility",
            "service",
            "household",
            "water_sink",
            "utility",
        ),
        Association(
            "communications",
            "network",
            "service",
            "household",
            "network_endpoint",
            "network",
        ),
        Association(
            "civic_membership",
            "civic",
            "civic_member",
            "household",
            "civic_member",
            "civic",
        ),
        Association(
            "residency",
            "registry",
            "resident",
            "household",
            "resident",
            "registry",
        ),
    )

    return CityArchitecture(units=units, associations=associations)


def remove_association_consent(
    architecture: CityArchitecture,
    unit_name: str,
    association_name: str,
) -> CityArchitecture:
    """Finite mutation: one unit withdraws one declared association."""
    units = tuple(
        replace(
            unit,
            declared_associations=unit.declared_associations - {association_name},
        )
        if unit.name == unit_name
        else unit
        for unit in architecture.units
    )
    return CityArchitecture(units=units, associations=architecture.associations)


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

    city_architecture = build_city_architecture()
    city_ledger = (
        LedgerEntry("e1", "arrival"),
        LedgerEntry("e2", "contract_entered"),
        LedgerEntry("e3", "payment_missed"),
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
            Affordance(
                "communication",
                "network",
                frozenset({"money", "device"}),
            ),
            Affordance("public_space", "civic", frozenset({"public_access"})),
        ),
        architecture=city_architecture,
        ledger=city_ledger,
    )

    healed = Surface(
        "healed_city",
        (
            Affordance("food", "market", frozenset({"public_access"})),
            Affordance("water", "utility", frozenset({"public_access"})),
            Affordance("shelter", "registry", frozenset({"public_access"})),
            Affordance("movement", "transit", frozenset({"public_access"})),
            Affordance(
                "communication",
                "network",
                frozenset({"public_access"}),
            ),
            Affordance("public_space", "civic", frozenset({"public_access"})),
        ),
        architecture=city_architecture,
        ledger=city_ledger,
    )

    return direct, mediated, healed, observer_resources


def witness() -> dict[str, object]:
    direct, mediated, healed, held = build_surfaces()
    assert mediated.architecture is not None
    assert healed.architecture is not None

    direct_reachable = direct.reachable(held)
    mediated_reachable = mediated.reachable(held)
    healed_reachable = healed.reachable(held)

    broken_association = remove_association_consent(
        healed.architecture,
        "market",
        "food_exchange",
    )

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
                "ledger": [entry.__dict__ for entry in direct.ledger],
                "ledger_gated_actions": list(direct.ledger_gated_affordances()),
            },
            mediated.name: {
                "capabilities": mediated.capability_count,
                "reachable": len(mediated_reachable),
                "reachable_actions": list(mediated_reachable),
                "blocked_requirement_count": mediated.blocked_requirements(held),
                "urban": mediated.urban,
                "architecture": mediated.architecture.public_view(),
                "ledger": [entry.__dict__ for entry in mediated.ledger],
                "ledger_gated_actions": list(mediated.ledger_gated_affordances()),
            },
            healed.name: {
                "capabilities": healed.capability_count,
                "reachable": len(healed_reachable),
                "reachable_actions": list(healed_reachable),
                "blocked_requirement_count": healed.blocked_requirements(held),
                "urban": healed.urban,
                "architecture": healed.architecture.public_view(),
                "ledger": [entry.__dict__ for entry in healed.ledger],
                "ledger_gated_actions": list(healed.ledger_gated_affordances()),
            },
        },
        "architecture_witness": {
            "market_loop": healed.architecture.has_market_loop(),
            "utility_delivery": healed.architecture.has_utility_delivery(),
            "communications_path": healed.architecture.has_communications_path(),
            "connected": healed.architecture.connected(),
            "private_interiors_hidden": healed.architecture.private_interiors_hidden(),
            "all_links_mutually_self_declared": (
                healed.architecture.all_associations_self_authorized()
            ),
            "withdraw_one_endpoint_consent_breaks_coherence": (
                healed.architecture.coherent()
                and not broken_association.coherent()
            ),
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
            "restoration_preserves_coherent_city_architecture": (
                mediated.architecture.coherent()
                and healed.architecture.coherent()
                and mediated.architecture.architectural_signature()
                == healed.architecture.architectural_signature()
            ),
            "coherent_architecture_does_not_require_total_interior_exposure": (
                healed.architecture.coherent()
                and healed.architecture.private_interiors_hidden()
            ),
            "modeled_links_are_grounded_in_mutual_self_association": (
                healed.architecture.all_associations_self_authorized()
                and not broken_association.all_associations_self_authorized()
            ),
            "ledger_history_is_preserved_without_remaining_an_access_gate": (
                healed.ledger == mediated.ledger
                and bool(mediated.ledger_gated_affordances())
                and not healed.ledger_gated_affordances()
            ),
            "restoration_is_not_a_return_to_the_direct_surface": (
                healed.urban and not direct.urban
            ),
        },
        "certificate_scope": {
            "certifies": [
                "the finite counts and set-membership relations encoded here",
                "a counterexample to the implication: more modeled capability => more modeled observer reachability",
                "that the modeled city contains a connected typed-port architecture with a market loop, road/logistics links, utility delivery, communications, civic membership, and registry",
                "that the modeled coherent architecture exposes public ports and associations without exposing its encoded private interiors",
                "that every modeled association is declared by both endpoints and a one-sided consent mutation invalidates the affected architectural coherence",
                "that the modeled healed state preserves the modeled city architecture and ledger while removing ledger history from present access control",
            ],
            "does_not_certify": [
                "that any real jungle or city has these affordances or architecture",
                "that privacy or self-association are necessary or sufficient for all real cities",
                "that any particular real association is voluntary, legitimate, or mutually beneficial",
                "that money, contracts, credentials, devices, institutions, or historical records are intrinsically harmful",
                "that real institutions should remove any particular eligibility or safety requirement",
                "that preserved provenance is itself true, complete, or morally authoritative",
                "that the Bible predicts this model",
                "that the optional Garden / fallen city / New Jerusalem mask is uniquely correct",
            ],
        },
    }


def main() -> None:
    result = witness()
    assert all(result["architecture_witness"].values())  # type: ignore[union-attr]
    assert all(result["mechanical_claims"].values())  # type: ignore[union-attr]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
