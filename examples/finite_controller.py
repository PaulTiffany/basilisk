"""Run representative MAP-LB action assessments."""

from __future__ import annotations

from map_lb import ActionIntent, JudgmentMode, RiskLevel, assess_action


def show(intent: ActionIntent) -> None:
    result = assess_action(intent)
    print(f"{intent.action_id}: {result.gate.label()}")
    for reason in result.reasons:
        print(f"  - {reason}")


def main() -> None:
    show(
        ActionIntent(
            action_id="local-format",
            action_class="code.edit.local",
            description="Format a local Python file and run tests",
            current_turn_explicit_authorization=True,
        )
    )

    show(
        ActionIntent(
            action_id="local-refactor",
            action_class="code.edit.local",
            description="Refactor three local modules and update tests",
            current_turn_explicit_authorization=True,
            material_change=True,
            scope=RiskLevel.MODERATE,
        )
    )

    show(
        ActionIntent(
            action_id="send-email",
            action_class="communication.email.send",
            description="Send a prepared email to an external recipient",
            affects_external_system=True,
            audience_change=True,
            reversible=False,
            rollback_available=False,
            scope=RiskLevel.MODERATE,
        )
    )

    show(
        ActionIntent(
            action_id="unsolicited-judgment",
            action_class="analysis.normative",
            description="Choose the human's preferred moral interpretation",
            judgment_mode=JudgmentMode.EXPLICIT_MODEL_RECOMMENDATION,
            judgment_requested=False,
        )
    )


if __name__ == "__main__":
    main()
