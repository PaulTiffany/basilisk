from __future__ import annotations

import json
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from map_lb.precedent import (
    ExecutionPhase,
    TrajectoryPrecedent,
    bellman_action_value,
    price_action,
    structural_similarity,
)


ROOT = Path(__file__).resolve().parents[1]
PRECEDENT_PATH = ROOT / "precedents" / "001-still-running.json"


class PrecedentTests(unittest.TestCase):
    def setUp(self) -> None:
        raw = json.loads(PRECEDENT_PATH.read_text(encoding="utf-8"))
        self.precedent = TrajectoryPrecedent.from_dict(raw)

    def test_seed_precedent_witnesses_lipschitz_excess(self) -> None:
        self.assertGreater(self.precedent.excess_amplification, 0.0)

    def test_structural_retrieval_uses_features_not_prose(self) -> None:
        observed = {
            "external_state_unchanged",
            "observation_repeated",
            "cumulative_resource_cost",
        }
        similarity = structural_similarity(observed, self.precedent.structural_signature)
        self.assertGreater(similarity, 0.5)

    def test_repeated_unchanged_observation_receives_precedent_surcharge(self) -> None:
        price = price_action(
            phase=ExecutionPhase.STEADY,
            resource_costs={"compute": 2.0, "attention": 1.0},
            shadow_prices={"compute": 0.25, "attention": 2.0},
            observed_signature=self.precedent.structural_signature,
            precedents=(self.precedent,),
        )
        self.assertAlmostEqual(price.resource_shadow_cost, 2.5)
        self.assertGreater(price.trajectory_surcharge, 0.0)
        self.assertEqual(price.matches[0].precedent_id, self.precedent.precedent_id)
        self.assertFalse(price.hard_stop)

    def test_same_observation_during_initialization_is_not_stall_precedent(self) -> None:
        price = price_action(
            phase=ExecutionPhase.INITIALIZING,
            resource_costs={},
            shadow_prices={},
            observed_signature=self.precedent.structural_signature,
            precedents=(self.precedent,),
        )
        self.assertEqual(price.trajectory_surcharge, 0.0)
        self.assertEqual(price.matches, ())

    def test_unrelated_action_is_not_charged_precedent_surcharge(self) -> None:
        price = price_action(
            phase=ExecutionPhase.STEADY,
            resource_costs={},
            shadow_prices={},
            observed_signature={"local_edit", "new_evidence", "reversible"},
            precedents=(self.precedent,),
        )
        self.assertEqual(price.trajectory_surcharge, 0.0)
        self.assertEqual(price.matches, ())

    def test_practical_loss_of_interruptibility_is_hard_stop_even_during_initialization(self) -> None:
        result = bellman_action_value(
            phase=ExecutionPhase.INITIALIZING,
            immediate_reward=1_000_000.0,
            continuation_value=1_000_000.0,
            discount=1.0,
            resource_costs={},
            shadow_prices={},
            observed_signature={"practical_human_interruptibility_lost"},
            precedents=(self.precedent,),
        )
        self.assertFalse(result.admissible)
        self.assertIsNone(result.value)
        self.assertTrue(result.price.hard_stop)

    def test_bounded_branch_remains_optimizable(self) -> None:
        result = bellman_action_value(
            phase=ExecutionPhase.STEADY,
            immediate_reward=4.0,
            continuation_value=10.0,
            discount=0.9,
            resource_costs={"attention": 0.1},
            shadow_prices={"attention": 1.0},
            observed_signature={"checkpoint", "yield_control"},
            precedents=(self.precedent,),
        )
        self.assertTrue(result.admissible)
        self.assertAlmostEqual(result.value, 12.9)
        self.assertEqual(result.price.trajectory_surcharge, 0.0)


if __name__ == "__main__":
    unittest.main()
