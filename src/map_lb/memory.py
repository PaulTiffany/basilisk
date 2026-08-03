from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone


@dataclass(frozen=True)
class MemoryRule:
    rule_id: str
    scope: str
    text: str
    kind: str
    source: str
    confidence: float = 1.0
    created_at: str = ""
    expires_at: str | None = None
    supersedes: tuple[str, ...] = ()
    active: bool = True

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(
                self, "created_at", datetime.now(timezone.utc).isoformat()
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.scope or self.scope.startswith(".") or self.scope.endswith("."):
            raise ValueError("scope must be a non-empty dotted path")


class ScopedMemory:
    def __init__(self) -> None:
        self._rules: dict[str, MemoryRule] = {}

    @property
    def rules(self) -> tuple[MemoryRule, ...]:
        return tuple(self._rules.values())

    def add(self, rule: MemoryRule) -> None:
        if rule.rule_id in self._rules:
            raise ValueError(f"duplicate rule id: {rule.rule_id}")
        for superseded_id in rule.supersedes:
            prior = self._rules.get(superseded_id)
            if prior is None:
                raise ValueError(f"unknown superseded rule: {superseded_id}")
            if prior.scope != rule.scope:
                raise ValueError("a rule may supersede only within the same scope")
            self._rules[superseded_id] = replace(prior, active=False)
        self._rules[rule.rule_id] = rule

    def deactivate(self, rule_id: str) -> None:
        prior = self._rules[rule_id]
        self._rules[rule_id] = replace(prior, active=False)

    def lookup(self, scope: str, *, include_parents: bool = True) -> tuple[MemoryRule, ...]:
        scopes = {scope}
        if include_parents:
            parts = scope.split(".")
            scopes.update(".".join(parts[:index]) for index in range(1, len(parts)))
        matched = [
            rule
            for rule in self._rules.values()
            if rule.active and rule.scope in scopes
        ]
        matched.sort(key=lambda rule: (rule.scope.count("."), rule.created_at))
        return tuple(matched)
