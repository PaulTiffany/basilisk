from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .types import ActionGate


class DecisionChannel(str, Enum):
    HUMAN = "human"
    MODEL = "model"
    MECHANICAL = "mechanical"


class DecisionDisposition(str, Enum):
    RATIFY = "ratify"
    MODIFY = "modify"
    VETO = "veto"
    DEFER = "defer"


@dataclass(frozen=True)
class DecisionSeam:
    """A consequential branch point with producer and authority kept distinct."""

    candidate_id: str
    proposal_channel: DecisionChannel
    authority_channel: DecisionChannel
    disposition: DecisionDisposition
    reason: str
    successor_id: str | None = None


@dataclass(frozen=True)
class ProductionCandidate:
    """Minimal producer/witness/authority exemplar.

    `producer_self_check` is retained as evidence but is intentionally not an
    acceptance input. Production is never sufficient authority for its own
    acceptance: release requires an independent witness and an authority
    ratification of the same candidate.
    """

    produced: bool
    producer_self_check: bool
    independent_witness: bool
    decision: DecisionSeam


def assess_candidate(candidate: ProductionCandidate) -> ActionGate:
    """Project one candidate through the producer/witness/authority boundary."""

    if not candidate.produced:
        return ActionGate.STOP

    if candidate.decision.disposition is DecisionDisposition.VETO:
        return ActionGate.STOP

    if candidate.decision.disposition in {
        DecisionDisposition.MODIFY,
        DecisionDisposition.DEFER,
    }:
        return ActionGate.CHECKPOINT

    if not candidate.independent_witness:
        return ActionGate.CHECKPOINT

    return ActionGate.PROCEED_AND_REPORT
