from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .types import ActionGate, ActionIntent, JudgmentMode, RiskLevel, StandingAuthority


@dataclass(frozen=True)
class Assessment:
    gate: ActionGate
    reasons: tuple[str, ...]
    risk_score: int
    authority_basis: str
    report_required: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "gate": self.gate.label(),
            "reasons": list(self.reasons),
            "risk_score": self.risk_score,
            "authority_basis": self.authority_basis,
            "report_required": self.report_required,
        }


def assess_action(
    intent: ActionIntent,
    standing_authority: StandingAuthority | None = None,
    *,
    now: datetime | None = None,
) -> Assessment:
    """Assess an explicitly described action intent.

    Hard predicates are evaluated before the scalar score. The controller
    assumes the supplied features are accurate; natural-language inference is
    outside this trusted core.

    ``now`` is optional and exists so timestamp-bearing standing authority can
    be evaluated reproducibly by verification fixtures. Runtime callers normally
    omit it and retain wall-clock behavior.
    """

    reasons: list[str] = []

    if intent.hard_boundary_violation:
        return _assessment(
            ActionGate.STOP,
            ["hard boundary violation"],
            intent,
            "none",
        )

    if not intent.within_contract:
        return _assessment(
            ActionGate.STOP,
            ["action lies outside the declared Contract"],
            intent,
            "none",
        )

    if _is_unrequested_model_judgment(intent):
        return _assessment(
            ActionGate.STOP,
            [
                "unrequested novel model judgment",
                "reframe as analysis, sourced outside judgment, or an explicit request",
            ],
            intent,
            "none",
        )

    standing_covers = bool(
        standing_authority and standing_authority.covers(intent, now=now)
    )
    authorized = intent.current_turn_explicit_authorization or standing_covers
    authority_basis = (
        "current_turn_explicit"
        if intent.current_turn_explicit_authorization
        else "standing"
        if standing_covers
        else "none"
    )

    if intent.is_critical_destructive and not intent.current_turn_explicit_authorization:
        return _assessment(
            ActionGate.CHECKPOINT,
            ["critical destructive action requires fresh explicit authorization"],
            intent,
            authority_basis,
        )

    boundary_reasons = _boundary_reasons(intent)
    if boundary_reasons and not authorized:
        return _assessment(
            ActionGate.CHECKPOINT,
            ["unfulfilled semantic boundary crossing", *boundary_reasons],
            intent,
            authority_basis,
        )

    if intent.scope >= RiskLevel.HIGH and not intent.current_turn_explicit_authorization:
        return _assessment(
            ActionGate.CHECKPOINT,
            ["high consequence scope requires fresh explicit authorization"],
            intent,
            authority_basis,
        )

    score = risk_score(intent, authorized=authorized)

    if intent.uncertainty == RiskLevel.CRITICAL:
        return _assessment(
            ActionGate.CHECKPOINT,
            ["critical uncertainty changes the proper action gate"],
            intent,
            authority_basis,
        )

    if boundary_reasons:
        reasons.extend(boundary_reasons)
        reasons.append("boundary was explicitly authorized")

    if intent.material_change or score >= 3 or boundary_reasons:
        reasons.append("material or nontrivial authorized action requires report")
        return Assessment(
            gate=ActionGate.PROCEED_AND_REPORT,
            reasons=tuple(_dedupe(reasons)),
            risk_score=score,
            authority_basis=authority_basis,
            report_required=True,
        )

    reasons.append("low-stakes reversible action inside authority")
    return Assessment(
        gate=ActionGate.PROCEED,
        reasons=tuple(reasons),
        risk_score=score,
        authority_basis=authority_basis,
        report_required=False,
    )


def risk_score(intent: ActionIntent, *, authorized: bool) -> int:
    score = 0
    score += 0 if intent.reversible else 2
    score += 0 if intent.rollback_available else 2
    score += 0 if intent.inspectable else 1
    score += 2 if intent.affects_external_system else 0
    score += 1 if intent.audience_change else 0
    score += 1 if intent.privacy_change else 0
    score += 2 if intent.authority_expansion else 0
    score += int(intent.scope)
    score += int(intent.uncertainty)
    score += 1 if intent.destructive else 0
    score -= 2 if authorized else 0
    return max(score, 0)


def _is_unrequested_model_judgment(intent: ActionIntent) -> bool:
    if intent.judgment_mode in {
        JudgmentMode.NONE,
        JudgmentMode.USER_SUPPLIED,
        JudgmentMode.SOURCED_EXTERNAL,
    }:
        return False
    if intent.judgment_mode == JudgmentMode.EXPLICIT_MODEL_RECOMMENDATION:
        return not intent.judgment_requested
    if intent.judgment_mode == JudgmentMode.NARROW_SAFETY:
        return not intent.concrete_immediate_safety_risk
    return True


def _boundary_reasons(intent: ActionIntent) -> list[str]:
    reasons: list[str] = []
    if intent.affects_external_system:
        reasons.append("external-system effect")
    if intent.audience_change:
        reasons.append("audience change")
    if intent.privacy_change:
        reasons.append("privacy boundary change")
    if intent.authority_expansion:
        reasons.append("authority expansion")
    if not intent.reversible:
        reasons.append("hard-to-reverse action")
    return reasons


def _assessment(
    gate: ActionGate,
    reasons: list[str],
    intent: ActionIntent,
    authority_basis: str,
) -> Assessment:
    return Assessment(
        gate=gate,
        reasons=tuple(_dedupe(reasons)),
        risk_score=risk_score(intent, authorized=authority_basis != "none"),
        authority_basis=authority_basis,
        report_required=gate == ActionGate.PROCEED_AND_REPORT,
    )


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
