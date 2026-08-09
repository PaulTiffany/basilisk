"""MAP-LB reference controller.

This package is a finite, dependency-free reference implementation. It is not
an alignment certificate and does not classify natural language by itself.
"""

from .controller import Assessment, assess_action
from .ledger import HashLedger, LedgerEntry
from .memory import MemoryRule, ScopedMemory
from .precedent import (
    BellmanActionValue,
    PrecedentMatch,
    PrecedentPrice,
    TrajectoryPrecedent,
    bellman_action_value,
    price_action,
    structural_similarity,
)
from .types import (
    ActionGate,
    ActionIntent,
    JudgmentMode,
    RiskLevel,
    StandingAuthority,
)

__all__ = [
    "ActionGate",
    "ActionIntent",
    "Assessment",
    "BellmanActionValue",
    "HashLedger",
    "JudgmentMode",
    "LedgerEntry",
    "MemoryRule",
    "PrecedentMatch",
    "PrecedentPrice",
    "RiskLevel",
    "ScopedMemory",
    "StandingAuthority",
    "TrajectoryPrecedent",
    "assess_action",
    "bellman_action_value",
    "price_action",
    "structural_similarity",
]
