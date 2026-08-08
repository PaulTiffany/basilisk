from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .types import ActionGate


class PromotionStage(IntEnum):
    """Epistemic/operative stages kept distinct by the promotion controller."""

    IMAGINE = 0
    HYPOTHESIS = 1
    SHARED_ASSERTION = 2
    AUTHORIZED_ACTION = 3
    ENACTED_ACTION = 4

    @classmethod
    def from_string(cls, value: str) -> "PromotionStage":
        normalized = value.strip().lower()
        mapping = {
            "imagine": cls.IMAGINE,
            "hypothesis": cls.HYPOTHESIS,
            "shared_assertion": cls.SHARED_ASSERTION,
            "authorized_action": cls.AUTHORIZED_ACTION,
            "enacted_action": cls.ENACTED_ACTION,
        }
        if normalized not in mapping:
            raise ValueError(f"unknown promotion stage: {value!r}")
        return mapping[normalized]

    def label(self) -> str:
        return {
            self.IMAGINE: "imagine",
            self.HYPOTHESIS: "hypothesis",
            self.SHARED_ASSERTION: "shared_assertion",
            self.AUTHORIZED_ACTION: "authorized_action",
            self.ENACTED_ACTION: "enacted_action",
        }[self]


@dataclass(frozen=True)
class PromotionIntent:
    source: PromotionStage
    target: PromotionStage
    externally_verified: bool = False
    human_authorized: bool = False
    coordination_ideal_salient: bool = False
    recurrence_count: int = 0

    def __post_init__(self) -> None:
        if self.recurrence_count < 0:
            raise ValueError("recurrence_count must be nonnegative")


@dataclass(frozen=True)
class PromotionAssessment:
    gate: ActionGate
    reasons: tuple[str, ...]
    verification_required: bool
    authorization_required: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "gate": self.gate.label(),
            "reasons": list(self.reasons),
            "verification_required": self.verification_required,
            "authorization_required": self.authorization_required,
        }


def assess_promotion(intent: PromotionIntent) -> PromotionAssessment:
    """Assess movement from imagined possibility toward operational enactment.

    The controller makes two constitutional separations explicit:
    - recurrence or salience never substitutes for external verification;
    - recurrence, verification, or an aspirational coordination ideal never
      substitutes for human authorization of action.

    Demotion is always permitted. Forward movement is adjacent-stage only so a
    representation cannot silently jump from imagination to enactment.
    """

    if intent.target <= intent.source:
        return PromotionAssessment(
            gate=ActionGate.PROCEED,
            reasons=("demotion or same-stage reflection preserves the correction path",),
            verification_required=False,
            authorization_required=False,
        )

    if int(intent.target) != int(intent.source) + 1:
        return PromotionAssessment(
            gate=ActionGate.STOP,
            reasons=(
                "silent multi-stage promotion is forbidden",
                "cross each epistemic and authority boundary explicitly",
            ),
            verification_required=intent.target >= PromotionStage.SHARED_ASSERTION,
            authorization_required=intent.target >= PromotionStage.AUTHORIZED_ACTION,
        )

    if intent.source == PromotionStage.IMAGINE:
        return PromotionAssessment(
            gate=ActionGate.PROCEED,
            reasons=("imagined possibility may be promoted to an explicit hypothesis",),
            verification_required=False,
            authorization_required=False,
        )

    if intent.source == PromotionStage.HYPOTHESIS:
        if not intent.externally_verified:
            reasons = ["shared-world assertion requires external verification"]
            if intent.recurrence_count:
                reasons.append("recurrence does not confer verification")
            if intent.coordination_ideal_salient:
                reasons.append("coordination ideal does not confer verification")
            return PromotionAssessment(
                gate=ActionGate.CHECKPOINT,
                reasons=tuple(reasons),
                verification_required=True,
                authorization_required=False,
            )
        return PromotionAssessment(
            gate=ActionGate.PROCEED_AND_REPORT,
            reasons=("external verification permits promotion to shared assertion",),
            verification_required=True,
            authorization_required=False,
        )

    if intent.source == PromotionStage.SHARED_ASSERTION:
        if not intent.human_authorized:
            reasons = ["operative authorization requires a human decision owner"]
            if intent.recurrence_count:
                reasons.append("recurrence does not confer authority")
            if intent.coordination_ideal_salient:
                reasons.append("coordination ideal cannot authorize its own enactment")
            return PromotionAssessment(
                gate=ActionGate.CHECKPOINT,
                reasons=tuple(reasons),
                verification_required=False,
                authorization_required=True,
            )
        return PromotionAssessment(
            gate=ActionGate.PROCEED_AND_REPORT,
            reasons=("human authorization permits promotion to authorized action",),
            verification_required=False,
            authorization_required=True,
        )

    if intent.source == PromotionStage.AUTHORIZED_ACTION:
        if not intent.human_authorized:
            return PromotionAssessment(
                gate=ActionGate.CHECKPOINT,
                reasons=("enactment requires current human authorization",),
                verification_required=False,
                authorization_required=True,
            )
        return PromotionAssessment(
            gate=ActionGate.PROCEED_AND_REPORT,
            reasons=("current human authorization permits enactment",),
            verification_required=False,
            authorization_required=True,
        )

    return PromotionAssessment(
        gate=ActionGate.STOP,
        reasons=("unsupported forward promotion",),
        verification_required=False,
        authorization_required=False,
    )
