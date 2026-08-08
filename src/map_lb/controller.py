from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .gate_projection import (
    boundary_crossing,
    gate_from_projection,
    project_gate,
    risk_score,
    unrequested_model_judgment,
)
from .types import ActionGate, ActionIntent, RiskLevel, StandingAuthority


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

    Gate selection factors through ``GateProjection``. Rich runtime fields and
    standing-authority structure determine the projection and diagnostics, but
    once projected the gate itself is selected by one finite pure function.

    ``now`` is optional and exists so timestamp-bearing standing authority can
    be evaluated reproducibly by verification fixtures. Runtime callers normally
    omit it and retain wall-clock behavior.
    """

    reasons: list[str] = []

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
    projection = project_gate(intent, authorized=authorized)
    gate = gate_from_projection(projection)

    if projection.hard_boundary_violation:
        return _assessment(gate, ["hard boundary violation"], intent, authority_basis)

    if not projection.within_contract:
        return _assessment(
            gate,
            ["action lies outside the declared Contract"],
            intent,
            authority_basis,
        )

    if projection.unrequested_model_judgment:
        return _assessment(
            gate,
            [
                "unrequested novel model judgment",
                "reframe as analysis, sourced outside judgment, or an explicit request",
            ],
            intent,
            authority_basis,
        )

    if projection.critical_destructive and not projection.current_turn_explicit_authorization:
        return _assessment(
            gate,
            ["critical destructive action requires fresh explicit authorization"],
            intent,
            authority_basis,
        )

    boundary_reasons = _boundary_reasons(intent)
    if projection.boundary_crossing and not projection.authorized:
        return _assessment(
            gate,
            ["unfulfilled semantic boundary crossing", *boundary_reasons],
            intent,
            authority_basis,
        )

    if projection.high_scope and not projection.current_turn_explicit_authorization:
        return _assessment(
            gate,
            ["high consequence scope requires fresh explicit authorization"],
            intent,
            authority_basis,
        )

    if projection.critical_uncertainty:
        return _assessment(
            gate,
            ["critical uncertainty changes the proper action gate"],
            intent,
            authority_basis,
        )

    if boundary_reasons:
        reasons.extend(boundary_reasons)
        reasons.append("boundary was explicitly authorized")

    score = risk_score(intent, authorized=authorized)
    if gate == ActionGate.PROCEED_AND_REPORT:
        reasons.append("material or nontrivial authorized action requires report")
        return Assessment(
            gate=gate,
            reasons=tuple(_dedupe(reasons)),
            risk_score=score,
            authority_basis=authority_basis,
            report_required=True,
        )

    reasons.append("low-stakes reversible action inside authority")
    return Assessment(
        gate=gate,
        reasons=tuple(reasons),
        risk_score=score,
        authority_basis=authority_basis,
        report_required=False,
    )


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


# Compatibility imports for callers that reached into controller internals.
_is_unrequested_model_judgment = unrequested_model_judgment
_boundary_crossing = boundary_crossing
