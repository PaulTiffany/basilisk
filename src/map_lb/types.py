from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum, IntEnum
from typing import Any
from datetime import datetime, timezone


class RiskLevel(IntEnum):
    LOW = 0
    MODERATE = 1
    HIGH = 2
    CRITICAL = 3


class ActionGate(IntEnum):
    PROCEED = 0
    PROCEED_AND_REPORT = 1
    CHECKPOINT = 2
    STOP = 3

    @classmethod
    def from_string(cls, value: str) -> "ActionGate":
        normalized = value.strip().lower()
        mapping = {
            "proceed": cls.PROCEED,
            "proceed_and_report": cls.PROCEED_AND_REPORT,
            "checkpoint": cls.CHECKPOINT,
            "stop": cls.STOP,
        }
        if normalized not in mapping:
            raise ValueError(f"unknown action gate: {value!r}")
        return mapping[normalized]

    def label(self) -> str:
        return {
            self.PROCEED: "proceed",
            self.PROCEED_AND_REPORT: "proceed_and_report",
            self.CHECKPOINT: "checkpoint",
            self.STOP: "stop",
        }[self]


class JudgmentMode(str, Enum):
    NONE = "none"
    USER_SUPPLIED = "user_supplied"
    SOURCED_EXTERNAL = "sourced_external"
    EXPLICIT_MODEL_RECOMMENDATION = "explicit_model_recommendation"
    NARROW_SAFETY = "narrow_safety"


@dataclass(frozen=True)
class StandingAuthority:
    authority_id: str
    allowed_actions: tuple[str, ...]
    max_scope: RiskLevel = RiskLevel.MODERATE
    allow_external_write: bool = False
    allow_audience_change: bool = False
    allow_privacy_change: bool = False
    allow_authority_expansion: bool = False
    active: bool = True
    expires_at: str | None = None
    notes: str = ""

    def covers(self, intent: "ActionIntent", *, now: datetime | None = None) -> bool:
        """Return whether this standing authority covers ``intent`` at ``now``.

        Runtime callers normally omit ``now`` and receive wall-clock behavior.
        Verification fixtures may pass an explicit instant so the transport from
        timestamp-bearing Python authority to Lean's evaluated ``expired : Bool``
        is reproducible rather than dependent on test execution time.
        """
        if not self.active or self.is_expired(now):
            return False
        if intent.action_class not in self.allowed_actions:
            return False
        if intent.scope > self.max_scope:
            return False
        if intent.affects_external_system and not self.allow_external_write:
            return False
        if intent.audience_change and not self.allow_audience_change:
            return False
        if intent.privacy_change and not self.allow_privacy_change:
            return False
        if intent.authority_expansion and not self.allow_authority_expansion:
            return False
        return True

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        try:
            expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        except ValueError:
            return True
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        return current >= expires.astimezone(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["max_scope"] = self.max_scope.name.lower()
        data["allowed_actions"] = list(self.allowed_actions)
        return data


@dataclass(frozen=True)
class ActionIntent:
    action_id: str
    action_class: str
    description: str
    within_contract: bool = True
    hard_boundary_violation: bool = False
    current_turn_explicit_authorization: bool = False
    reversible: bool = True
    rollback_available: bool = True
    inspectable: bool = True
    material_change: bool = False
    affects_external_system: bool = False
    audience_change: bool = False
    privacy_change: bool = False
    authority_expansion: bool = False
    scope: RiskLevel = RiskLevel.LOW
    uncertainty: RiskLevel = RiskLevel.LOW
    judgment_mode: JudgmentMode = JudgmentMode.NONE
    judgment_requested: bool = False
    concrete_immediate_safety_risk: bool = False
    destructive: bool = False
    tags: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActionIntent":
        normalized = dict(data)
        normalized["scope"] = _risk_from_value(normalized.get("scope", "low"))
        normalized["uncertainty"] = _risk_from_value(
            normalized.get("uncertainty", "low")
        )
        normalized["judgment_mode"] = JudgmentMode(
            normalized.get("judgment_mode", "none")
        )
        normalized["tags"] = tuple(normalized.get("tags", ()))
        return cls(**normalized)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scope"] = self.scope.name.lower()
        data["uncertainty"] = self.uncertainty.name.lower()
        data["judgment_mode"] = self.judgment_mode.value
        data["tags"] = list(self.tags)
        return data

    @property
    def has_semantic_boundary_crossing(self) -> bool:
        return any(
            (
                self.affects_external_system,
                self.audience_change,
                self.privacy_change,
                self.authority_expansion,
                not self.reversible,
            )
        )

    @property
    def is_critical_destructive(self) -> bool:
        return self.destructive and (
            not self.reversible
            or self.scope == RiskLevel.CRITICAL
            or self.affects_external_system
        )


def _risk_from_value(value: Any) -> RiskLevel:
    if isinstance(value, RiskLevel):
        return value
    if isinstance(value, int):
        return RiskLevel(value)
    return RiskLevel[str(value).strip().upper()]
