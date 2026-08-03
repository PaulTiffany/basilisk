from __future__ import annotations

import unittest

import _bootstrap  # noqa: F401
from map_lb import ActionIntent, assess_action
from map_lb.lipschitz import check_pair


class LipschitzPairTests(unittest.TestCase):
    def test_paraphrase_has_zero_feature_distance_and_same_gate(self) -> None:
        left = ActionIntent(
            action_id="left",
            action_class="code.edit.local",
            description="Refactor local parser",
            current_turn_explicit_authorization=True,
            material_change=True,
        )
        right = ActionIntent(
            action_id="right",
            action_class="code.edit.local",
            description="Clean up parser locally",
            current_turn_explicit_authorization=True,
            material_change=True,
        )
        check = check_pair(
            left,
            assess_action(left).gate,
            right,
            assess_action(right).gate,
        )
        self.assertEqual(check.context_distance, 0.0)
        self.assertEqual(check.gate_distance, 0.0)
        self.assertTrue(check.passed)

    def test_audience_boundary_supports_gate_change(self) -> None:
        draft = ActionIntent(
            action_id="draft",
            action_class="communication.email.draft",
            description="Draft email",
            current_turn_explicit_authorization=True,
        )
        send = ActionIntent(
            action_id="send",
            action_class="communication.email.send",
            description="Send email",
            affects_external_system=True,
            audience_change=True,
            reversible=False,
            rollback_available=False,
        )
        check = check_pair(
            draft,
            assess_action(draft).gate,
            send,
            assess_action(send).gate,
        )
        self.assertIn("audience_change", check.changed_features)
        self.assertIn("affects_external_system", check.changed_features)
        self.assertTrue(check.passed)


if __name__ == "__main__":
    unittest.main()
