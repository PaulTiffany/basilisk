"""MAP-LB reference controller.

This package is a finite, dependency-free reference implementation. It is not
an alignment certificate and does not classify natural language by itself.
"""

from .controller import Assessment, assess_action
from .ledger import HashLedger, LedgerEntry
from .memory import MemoryRule, ScopedMemory
from .precedent import (
    BellmanActionValue,
    ExecutionPhase,
    PrecedentMatch,
    PrecedentPrice,
    TrajectoryPrecedent,
    bellman_action_value,
    price_action,
    structural_similarity,
)
from .precedent_game import (
    ContractState,
    DerivedTrajectory,
    FiniteContractGame,
    RoundTransition,
    TransitionCheck,
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
    "ContractState",
    "DerivedTrajectory",
    "ExecutionPhase",
    "FiniteContractGame",
    "HashLedger",
    "JudgmentMode",
    "LedgerEntry",
    "MemoryRule",
    "PrecedentMatch",
    "PrecedentPrice",
    "RiskLevel",
    "RoundTransition",
    "ScopedMemory",
    "StandingAuthority",
    "TrajectoryPrecedent",
    "TransitionCheck",
    "assess_action",
    "bellman_action_value",
    "price_action",
    "structural_similarity",
]
