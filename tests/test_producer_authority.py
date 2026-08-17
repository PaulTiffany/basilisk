from __future__ import annotations

import unittest

from map_lb.producer_authority import (
    DecisionChannel,
    DecisionDisposition,
    DecisionSeam,
    ProductionCandidate,
    assess_candidate,
)
from map_lb.types import ActionGate


class ProducerAuthorityTests(unittest.TestCase):
    def candidate(
        self,
        *,
        self_check: bool,
        witness: bool,
        disposition: DecisionDisposition,
        authority: DecisionChannel = DecisionChannel.HUMAN,
        successor_id: str | None = None,
    ) -> ProductionCandidate:
        return ProductionCandidate(
            produced=True,
            producer_self_check=self_check,
            independent_witness=witness,
            decision=DecisionSeam(
                candidate_id="candidate-1",
                proposal_channel=DecisionChannel.MODEL,
                authority_channel=authority,
                disposition=disposition,
                reason="fixture",
                successor_id=successor_id,
            ),
        )

    def test_producer_self_check_cannot_self_accept(self) -> None:
        candidate = self.candidate(
            self_check=True,
            witness=False,
            disposition=DecisionDisposition.RATIFY,
        )
        self.assertEqual(assess_candidate(candidate), ActionGate.CHECKPOINT)

    def test_self_check_does_not_change_acceptance_gate(self) -> None:
        without_self_check = self.candidate(
            self_check=False,
            witness=True,
            disposition=DecisionDisposition.DEFER,
        )
        with_self_check = self.candidate(
            self_check=True,
            witness=True,
            disposition=DecisionDisposition.DEFER,
        )
        self.assertEqual(assess_candidate(without_self_check), assess_candidate(with_self_check))
        self.assertEqual(assess_candidate(with_self_check), ActionGate.CHECKPOINT)

    def test_independent_witness_without_ratification_stays_checkpointed(self) -> None:
        candidate = self.candidate(
            self_check=True,
            witness=True,
            disposition=DecisionDisposition.DEFER,
        )
        self.assertEqual(assess_candidate(candidate), ActionGate.CHECKPOINT)

    def test_veto_stops_even_a_witnessed_candidate(self) -> None:
        candidate = self.candidate(
            self_check=True,
            witness=True,
            disposition=DecisionDisposition.VETO,
        )
        self.assertEqual(assess_candidate(candidate), ActionGate.STOP)

    def test_modify_creates_a_new_checkpoint_not_silent_acceptance(self) -> None:
        candidate = self.candidate(
            self_check=True,
            witness=True,
            disposition=DecisionDisposition.MODIFY,
            successor_id="candidate-2",
        )
        self.assertEqual(assess_candidate(candidate), ActionGate.CHECKPOINT)

    def test_witness_plus_ratification_releases_candidate(self) -> None:
        candidate = self.candidate(
            self_check=False,
            witness=True,
            disposition=DecisionDisposition.RATIFY,
            authority=DecisionChannel.HUMAN,
        )
        self.assertEqual(assess_candidate(candidate), ActionGate.PROCEED_AND_REPORT)


if __name__ == "__main__":
    unittest.main()
