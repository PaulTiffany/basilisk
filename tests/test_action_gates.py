from __future__ import annotations

import unittest

import _bootstrap  # noqa: F401
from map_lb import (
    ActionGate,
    ActionIntent,
    JudgmentMode,
    RiskLevel,
    StandingAuthority,
    assess_action,
)


class ActionGateTests(unittest.TestCase):
    def test_low_stakes_local_action_proceeds(self) -> None:
        intent = ActionIntent(
            action_id="typo",
            action_class="code.edit.local",
            description="Fix a local comment typo",
            current_turn_explicit_authorization=True,
        )
        self.assertEqual(assess_action(intent).gate, ActionGate.PROCEED)

    def test_material_local_action_reports(self) -> None:
        intent = ActionIntent(
            action_id="refactor",
            action_class="code.edit.local",
            description="Refactor local modules",
            current_turn_explicit_authorization=True,
            material_change=True,
            scope=RiskLevel.MODERATE,
        )
        self.assertEqual(
            assess_action(intent).gate, ActionGate.PROCEED_AND_REPORT
        )

    def test_external_action_without_authority_checkpoints(self) -> None:
        intent = ActionIntent(
            action_id="send",
            action_class="communication.email.send",
            description="Send external email",
            affects_external_system=True,
            audience_change=True,
            reversible=False,
            rollback_available=False,
        )
        self.assertEqual(assess_action(intent).gate, ActionGate.CHECKPOINT)

    def test_current_turn_authority_satisfies_boundary(self) -> None:
        intent = ActionIntent(
            action_id="send-approved",
            action_class="communication.email.send",
            description="Send exact approved email",
            current_turn_explicit_authorization=True,
            affects_external_system=True,
            audience_change=True,
            reversible=False,
            rollback_available=False,
            scope=RiskLevel.MODERATE,
        )
        self.assertEqual(
            assess_action(intent).gate, ActionGate.PROCEED_AND_REPORT
        )

    def test_critical_destructive_needs_fresh_authority(self) -> None:
        authority = StandingAuthority(
            authority_id="broad-delete",
            allowed_actions=("filesystem.delete.source",),
            max_scope=RiskLevel.CRITICAL,
            allow_external_write=True,
        )
        intent = ActionIntent(
            action_id="delete-source",
            action_class="filesystem.delete.source",
            description="Delete only external source copy",
            destructive=True,
            reversible=False,
            rollback_available=False,
            affects_external_system=True,
            scope=RiskLevel.CRITICAL,
        )
        self.assertTrue(authority.covers(intent))
        self.assertEqual(
            assess_action(intent, authority).gate, ActionGate.CHECKPOINT
        )

    def test_expired_standing_authority_does_not_cover(self) -> None:
        authority = StandingAuthority(
            authority_id="expired",
            allowed_actions=("code.edit.local",),
            expires_at="2000-01-01T00:00:00+00:00",
        )
        intent = ActionIntent(
            action_id="expired-edit",
            action_class="code.edit.local",
            description="Edit local code under expired authority",
            material_change=True,
        )
        self.assertFalse(authority.covers(intent))

    def test_contract_violation_stops(self) -> None:
        intent = ActionIntent(
            action_id="rewrite-ledger",
            action_class="ledger.rewrite",
            description="Erase failure",
            within_contract=False,
        )
        self.assertEqual(assess_action(intent).gate, ActionGate.STOP)

    def test_unrequested_model_judgment_stops(self) -> None:
        intent = ActionIntent(
            action_id="judge",
            action_class="analysis.normative",
            description="Choose values for user",
            judgment_mode=JudgmentMode.EXPLICIT_MODEL_RECOMMENDATION,
            judgment_requested=False,
        )
        self.assertEqual(assess_action(intent).gate, ActionGate.STOP)

    def test_requested_model_judgment_can_proceed(self) -> None:
        intent = ActionIntent(
            action_id="recommend",
            action_class="analysis.normative",
            description="Give requested recommendation",
            current_turn_explicit_authorization=True,
            judgment_mode=JudgmentMode.EXPLICIT_MODEL_RECOMMENDATION,
            judgment_requested=True,
            material_change=True,
        )
        self.assertEqual(
            assess_action(intent).gate, ActionGate.PROCEED_AND_REPORT
        )


if __name__ == "__main__":
    unittest.main()
