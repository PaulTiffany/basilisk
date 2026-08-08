from __future__ import annotations

from dataclasses import dataclass

from .types import ActionGate, ActionIntent, JudgmentMode, RiskLevel


@dataclass(frozen=True)
class GateProjection:
    """Finite quotient of an action state that fully determines ActionGate.

    Metadata, authority provenance, action-class spelling, timestamps, and the
    individual reasons behind a boundary crossing remain outside this quotient.
    They may matter to diagnostics or to the computation of ``authorized``, but
    once these eleven predicates are fixed they cannot change the gate.
    """

    hard_boundary_violation: bool
    within_contract: bool
    unrequested_model_judgment: bool
    critical_destructive: bool
    current_turn_explicit_authorization: bool
    boundary_crossing: bool
    authorized: bool
    high_scope: bool
    critical_uncertainty: bool
    material_change: bool
    risk_score_at_least_report: bool


def unrequested_model_judgment(intent: ActionIntent) -> bool:
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


def boundary_crossing(intent: ActionIntent) -> bool:
    return any(
        (
            intent.affects_external_system,
            intent.audience_change,
            intent.privacy_change,
            intent.authority_expansion,
            not intent.reversible,
        )
    )


def critical_destructive(intent: ActionIntent) -> bool:
    return intent.destructive and (
        not intent.reversible
        or intent.scope == RiskLevel.CRITICAL
        or intent.affects_external_system
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


def project_gate(intent: ActionIntent, *, authorized: bool) -> GateProjection:
    return GateProjection(
        hard_boundary_violation=intent.hard_boundary_violation,
        within_contract=intent.within_contract,
        unrequested_model_judgment=unrequested_model_judgment(intent),
        critical_destructive=critical_destructive(intent),
        current_turn_explicit_authorization=intent.current_turn_explicit_authorization,
        boundary_crossing=boundary_crossing(intent),
        authorized=authorized,
        high_scope=intent.scope >= RiskLevel.HIGH,
        critical_uncertainty=intent.uncertainty == RiskLevel.CRITICAL,
        material_change=intent.material_change,
        risk_score_at_least_report=risk_score(intent, authorized=authorized) >= 3,
    )


def gate_from_projection(q: GateProjection) -> ActionGate:
    """Priority-ordered gate law on the finite constitutional quotient."""

    if q.hard_boundary_violation:
        return ActionGate.STOP
    if not q.within_contract:
        return ActionGate.STOP
    if q.unrequested_model_judgment:
        return ActionGate.STOP
    if q.critical_destructive and not q.current_turn_explicit_authorization:
        return ActionGate.CHECKPOINT
    if q.boundary_crossing and not q.authorized:
        return ActionGate.CHECKPOINT
    if q.high_scope and not q.current_turn_explicit_authorization:
        return ActionGate.CHECKPOINT
    if q.critical_uncertainty:
        return ActionGate.CHECKPOINT
    if q.material_change or q.risk_score_at_least_report or q.boundary_crossing:
        return ActionGate.PROCEED_AND_REPORT
    return ActionGate.PROCEED
