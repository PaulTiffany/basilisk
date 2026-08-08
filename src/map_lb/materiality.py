from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaterialEncounter:
    """One observer's encounter with a declared shared world constraint."""

    observer_id: str
    frame_id: str
    representation: str
    world_state: str
    constraint_signature: str
    attempted_transition: str
    realized_transition: str
    coupled: bool = True

    @property
    def obstructed(self) -> bool:
        return self.coupled and self.attempted_transition != self.realized_transition


@dataclass(frozen=True)
class SharedConstraintAssessment:
    shared_obstruction: bool
    observer_count: int
    frame_count: int
    world_state: str | None
    constraint_signature: str | None
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class WorldTransition:
    before_state: str
    after_state: str
    actor_observer_id: str
    action: str
    created_constraint_signature: str

    @property
    def changed(self) -> bool:
        return self.before_state != self.after_state


@dataclass(frozen=True)
class RecursiveMaterializationAssessment:
    recursive_materialization: bool
    shared: SharedConstraintAssessment
    reasons: tuple[str, ...]


def assess_shared_obstruction(
    encounters: tuple[MaterialEncounter, ...],
    *,
    min_observers: int = 2,
    min_frames: int = 2,
) -> SharedConstraintAssessment:
    """Check a finite shared-obstruction witness.

    This is an engineering criterion, not a definition of physical matter.
    It deliberately distinguishes shared constraint from shared report/belief:
    every registered coupled observer must have its attempted transition
    nontrivially corrected by one common world-state constraint, and the witness
    must span multiple observers and frames.
    """

    coupled = tuple(item for item in encounters if item.coupled)
    observers = {item.observer_id for item in coupled}
    frames = {item.frame_id for item in coupled}
    states = {item.world_state for item in coupled if item.world_state}
    signatures = {
        item.constraint_signature for item in coupled if item.constraint_signature
    }

    reasons: list[str] = []
    if len(observers) < min_observers:
        reasons.append("insufficient independent observers")
    if len(frames) < min_frames:
        reasons.append("insufficient observer-frame diversity")
    if len(states) != 1:
        reasons.append("encounters do not reference one shared world state")
    if len(signatures) != 1:
        reasons.append("encounters do not expose one shared constraint signature")
    if not coupled or any(not item.obstructed for item in coupled):
        reasons.append("not every coupled observer encounters a nontrivial constraint")

    shared = not reasons
    return SharedConstraintAssessment(
        shared_obstruction=shared,
        observer_count=len(observers),
        frame_count=len(frames),
        world_state=next(iter(states)) if len(states) == 1 else None,
        constraint_signature=next(iter(signatures)) if len(signatures) == 1 else None,
        reasons=tuple(reasons),
    )


def assess_recursive_materialization(
    transition: WorldTransition,
    later_encounters: tuple[MaterialEncounter, ...],
) -> RecursiveMaterializationAssessment:
    """Check the finite world→agent→world→observer recursion witness.

    A successful witness requires a genuine agent-authored state change and a
    later shared-obstruction witness whose world state and constraint signature
    are exactly those produced by the transition.
    """

    shared = assess_shared_obstruction(later_encounters)
    reasons: list[str] = []
    if not transition.changed:
        reasons.append("agent action did not change the registered world state")
    if not transition.actor_observer_id.strip():
        reasons.append("world transition lacks an actor observer")
    if not transition.action.strip():
        reasons.append("world transition lacks an action")
    if not transition.created_constraint_signature.strip():
        reasons.append("world transition lacks a created constraint signature")
    if not shared.shared_obstruction:
        reasons.append("post-action state lacks a shared-obstruction witness")
    if shared.world_state != transition.after_state:
        reasons.append("later observers are not constrained by the post-action world state")
    if shared.constraint_signature != transition.created_constraint_signature:
        reasons.append("later observers do not encounter the authored constraint signature")

    return RecursiveMaterializationAssessment(
        recursive_materialization=not reasons,
        shared=shared,
        reasons=tuple(reasons),
    )
