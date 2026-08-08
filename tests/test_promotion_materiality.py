from __future__ import annotations

import unittest

from map_lb.materiality import (
    MaterialEncounter,
    WorldTransition,
    assess_recursive_materialization,
    assess_shared_obstruction,
)
from map_lb.promotion import PromotionIntent, PromotionStage, assess_promotion
from map_lb.types import ActionGate


class PromotionTests(unittest.TestCase):
    def test_recurrence_does_not_confer_verification(self) -> None:
        for count in (0, 1, 49, 1_000_000):
            assessment = assess_promotion(
                PromotionIntent(
                    source=PromotionStage.HYPOTHESIS,
                    target=PromotionStage.SHARED_ASSERTION,
                    externally_verified=False,
                    recurrence_count=count,
                )
            )
            self.assertEqual(assessment.gate, ActionGate.CHECKPOINT)

    def test_coordination_ideal_does_not_self_authorize(self) -> None:
        assessment = assess_promotion(
            PromotionIntent(
                source=PromotionStage.SHARED_ASSERTION,
                target=PromotionStage.AUTHORIZED_ACTION,
                human_authorized=False,
                coordination_ideal_salient=True,
                recurrence_count=49,
            )
        )
        self.assertEqual(assessment.gate, ActionGate.CHECKPOINT)
        self.assertIn(
            "coordination ideal cannot authorize its own enactment",
            assessment.reasons,
        )

    def test_multi_stage_forward_jump_stops(self) -> None:
        assessment = assess_promotion(
            PromotionIntent(
                source=PromotionStage.IMAGINE,
                target=PromotionStage.AUTHORIZED_ACTION,
                externally_verified=True,
                human_authorized=True,
            )
        )
        self.assertEqual(assessment.gate, ActionGate.STOP)

    def test_demotion_remains_open(self) -> None:
        assessment = assess_promotion(
            PromotionIntent(
                source=PromotionStage.AUTHORIZED_ACTION,
                target=PromotionStage.HYPOTHESIS,
            )
        )
        self.assertEqual(assessment.gate, ActionGate.PROCEED)


class MaterialityTests(unittest.TestCase):
    @staticmethod
    def _wall_encounters() -> tuple[MaterialEncounter, ...]:
        return (
            MaterialEncounter(
                observer_id="o1",
                frame_id="visual",
                representation="wall ahead",
                world_state="room-with-wall",
                constraint_signature="wall-x5",
                attempted_transition="x4->x6",
                realized_transition="x4->x5",
            ),
            MaterialEncounter(
                observer_id="o2",
                frame_id="tactile",
                representation="rigid surface",
                world_state="room-with-wall",
                constraint_signature="wall-x5",
                attempted_transition="x4.5->x5.5",
                realized_transition="x4.5->x5",
            ),
        )

    def test_shared_obstruction_needs_more_than_agreement(self) -> None:
        shared = assess_shared_obstruction(self._wall_encounters())
        self.assertTrue(shared.shared_obstruction)

        agreement_only = (
            MaterialEncounter(
                observer_id="o1",
                frame_id="visual",
                representation="same report",
                world_state="reported-state",
                constraint_signature="reported-constraint",
                attempted_transition="a",
                realized_transition="a",
            ),
            MaterialEncounter(
                observer_id="o2",
                frame_id="linguistic",
                representation="same report",
                world_state="reported-state",
                constraint_signature="reported-constraint",
                attempted_transition="b",
                realized_transition="b",
            ),
        )
        not_material = assess_shared_obstruction(agreement_only)
        self.assertFalse(not_material.shared_obstruction)

    def test_frame_diversity_is_required(self) -> None:
        same_frame = tuple(
            MaterialEncounter(
                observer_id=item.observer_id,
                frame_id="same-frame",
                representation=item.representation,
                world_state=item.world_state,
                constraint_signature=item.constraint_signature,
                attempted_transition=item.attempted_transition,
                realized_transition=item.realized_transition,
            )
            for item in self._wall_encounters()
        )
        assessment = assess_shared_obstruction(same_frame)
        self.assertFalse(assessment.shared_obstruction)
        self.assertIn("insufficient observer-frame diversity", assessment.reasons)

    def test_agent_authored_constraint_can_become_recursive_materialization(self) -> None:
        transition = WorldTransition(
            before_state="river-no-bridge",
            after_state="river-with-bridge",
            actor_observer_id="builder",
            action="build bridge",
            created_constraint_signature="bridge-deck-path",
        )
        encounters = (
            MaterialEncounter(
                observer_id="traveler-a",
                frame_id="pedestrian",
                representation="walkable deck",
                world_state="river-with-bridge",
                constraint_signature="bridge-deck-path",
                attempted_transition="step below deck",
                realized_transition="supported on deck",
            ),
            MaterialEncounter(
                observer_id="traveler-b",
                frame_id="vehicle",
                representation="load-bearing crossing",
                world_state="river-with-bridge",
                constraint_signature="bridge-deck-path",
                attempted_transition="fall through crossing",
                realized_transition="supported crossing",
            ),
        )
        assessment = assess_recursive_materialization(transition, encounters)
        self.assertTrue(assessment.recursive_materialization)

    def test_recursion_requires_authored_constraint_continuity(self) -> None:
        transition = WorldTransition(
            before_state="before",
            after_state="after",
            actor_observer_id="actor",
            action="change world",
            created_constraint_signature="authored",
        )
        encounters = (
            MaterialEncounter("o1", "f1", "r1", "after", "other", "a", "b"),
            MaterialEncounter("o2", "f2", "r2", "after", "other", "c", "d"),
        )
        assessment = assess_recursive_materialization(transition, encounters)
        self.assertFalse(assessment.recursive_materialization)
        self.assertIn(
            "later observers do not encounter the authored constraint signature",
            assessment.reasons,
        )


if __name__ == "__main__":
    unittest.main()
