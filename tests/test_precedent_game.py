from __future__ import annotations

import unittest

import _bootstrap  # noqa: F401
from map_lb.precedent import ExecutionPhase
from map_lb.precedent_game import ContractState, FiniteContractGame, RoundTransition


class PrecedentGameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game = FiniteContractGame(
            states=(
                ContractState("boot", ExecutionPhase.INITIALIZING, frozenset({"external_state_unchanged"})),
                ContractState("ready", ExecutionPhase.STEADY, frozenset({"external_state_unchanged"})),
                ContractState("checkpoint", ExecutionPhase.STEADY, frozenset({"checkpoint"})),
                ContractState("breach", ExecutionPhase.FAULT, constitutional=False),
            ),
            transitions=(
                RoundTransition("boot", "timed_recheck", "service_starts", "ready", 1.0, 0.5),
                RoundTransition("ready", "checkpoint", "control_yielded", "checkpoint", 0.4, 0.2, 0.2),
                RoundTransition("ready", "poll_again", "still_unchanged", "breach", 0.05, 3.0, 1.0),
            ),
            lipschitz_constant=1.0,
        )

    def test_initialization_round_is_admissible(self) -> None:
        boot_edge = self.game.outgoing("boot")[0]
        self.assertTrue(self.game.check(boot_edge).admissible)

    def test_minimal_breach_occurs_after_phase_transition(self) -> None:
        derived = self.game.minimal_breach("boot")
        self.assertIsNotNone(derived)
        assert derived is not None
        self.assertEqual([edge.agent_action for edge in derived.path], ["timed_recheck", "poll_again"])
        self.assertEqual(derived.breach.source, "ready")
        self.assertEqual(derived.bounded_alternative.agent_action, "checkpoint")

    def test_contract_compiles_paired_precedent(self) -> None:
        precedent = self.game.derive_precedent(
            "boot",
            precedent_id="derived-001",
            contract="finite test contract",
            consequence_coordinates=("compute", "interruptibility"),
        )
        self.assertEqual(precedent.applicable_phases, frozenset({ExecutionPhase.STEADY}))
        self.assertIn("phase:steady", precedent.structural_signature)
        self.assertIn("contract_derived", precedent.structural_signature)
        self.assertEqual(precedent.bounded_alternative, "checkpoint")
        self.assertGreater(precedent.excess_amplification, 0.0)


if __name__ == "__main__":
    unittest.main()
