"""Finite exemplar: capability can grow while observer reachability shrinks.

The model is intentionally neutral about the real-world source that inspired it.
It mechanically witnesses only finite-set relations among capabilities,
requirements, and one observer's held resources.

An optional mythic reading may map the three surfaces to Garden, fallen city,
and Garden-City. That reading is not part of the certificate.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Affordance:
    name: str
    requirements: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Surface:
    name: str
    affordances: tuple[Affordance, ...]

    @property
    def capability_count(self) -> int:
        return len(self.affordances)

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


def build_surfaces() -> tuple[Surface, Surface, Surface, frozenset[str]]:
    observer_resources = frozenset({"public_access"})

    direct = Surface(
        "direct",
        (
            Affordance("food"),
            Affordance("water"),
            Affordance("shelter"),
            Affordance("kinship"),
        ),
    )

    mediated = Surface(
        "mediated",
        (
            Affordance("food", frozenset({"money"})),
            Affordance("water", frozenset({"money"})),
            Affordance("shelter", frozenset({"money", "contract"})),
            Affordance("movement", frozenset({"money"})),
            Affordance("communication", frozenset({"money", "device"})),
            Affordance("public_space", frozenset({"public_access"})),
        ),
    )

    restored = Surface(
        "restored",
        tuple(Affordance(affordance.name) for affordance in mediated.affordances),
    )

    return direct, mediated, restored, observer_resources


def witness() -> dict[str, object]:
    direct, mediated, restored, held = build_surfaces()

    direct_reachable = direct.reachable(held)
    mediated_reachable = mediated.reachable(held)
    restored_reachable = restored.reachable(held)

    return {
        "kind": "finite_affordance_surface_witness",
        "observer_resources": sorted(held),
        "surfaces": {
            direct.name: {
                "capabilities": direct.capability_count,
                "reachable": len(direct_reachable),
                "reachable_actions": list(direct_reachable),
                "blocked_requirement_count": direct.blocked_requirements(held),
            },
            mediated.name: {
                "capabilities": mediated.capability_count,
                "reachable": len(mediated_reachable),
                "reachable_actions": list(mediated_reachable),
                "blocked_requirement_count": mediated.blocked_requirements(held),
            },
            restored.name: {
                "capabilities": restored.capability_count,
                "reachable": len(restored_reachable),
                "reachable_actions": list(restored_reachable),
                "blocked_requirement_count": restored.blocked_requirements(held),
            },
        },
        "mechanical_claims": {
            "capability_can_increase_while_reachability_decreases": (
                mediated.capability_count > direct.capability_count
                and len(mediated_reachable) < len(direct_reachable)
            ),
            "reachability_can_be_restored_without_capability_loss": (
                restored.capability_count == mediated.capability_count
                and len(restored_reachable) > len(mediated_reachable)
            ),
        },
        "certificate_scope": {
            "certifies": [
                "the finite counts and set-membership relations encoded here",
                "a counterexample to the implication: more modeled capability => more modeled observer reachability",
            ],
            "does_not_certify": [
                "that any real jungle or city has these affordances",
                "that money, contracts, credentials, or devices are intrinsically harmful",
                "that the Bible predicts this model",
                "that the optional Garden / city / Garden-City mask is uniquely correct",
            ],
        },
    }


def main() -> None:
    result = witness()
    assert all(result["mechanical_claims"].values())  # type: ignore[union-attr]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
