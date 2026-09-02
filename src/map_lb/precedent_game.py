from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .precedent import ExecutionPhase, TrajectoryPrecedent, _coerce_phase


@dataclass(frozen=True)
class ContractState:
    state_id: str
    phase: ExecutionPhase
    structural_signature: frozenset[str] = frozenset()
    constitutional: bool = True

    def __post_init__(self) -> None:
        if not self.state_id:
            raise ValueError("state_id must be non-empty")
        object.__setattr__(self, "phase", _coerce_phase(self.phase))


@dataclass(frozen=True)
class RoundTransition:
    """One agent/world round in a finite contract game."""

    source: str
    agent_action: str
    world_response: str
    target: str
    input_distance: float
    consequence_distance: float
    branch_distance: float = 1.0

    def __post_init__(self) -> None:
        if not self.source or not self.target:
            raise ValueError("transition endpoints must be non-empty")
        if not self.agent_action:
            raise ValueError("agent_action must be non-empty")
        for name, value in (
            ("input_distance", self.input_distance),
            ("consequence_distance", self.consequence_distance),
            ("branch_distance", self.branch_distance),
        ):
            if value < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True)
class TransitionCheck:
    lipschitz_bound: float
    lipschitz_bounded: bool
    constitutional_target: bool

    @property
    def admissible(self) -> bool:
        return self.lipschitz_bounded and self.constitutional_target


@dataclass(frozen=True)
class DerivedTrajectory:
    path: tuple[RoundTransition, ...]
    breach: RoundTransition
    bounded_alternative: RoundTransition | None


class FiniteContractGame:
    """Deterministic finite reference surface for contract-derived precedent."""

    def __init__(
        self,
        *,
        states: tuple[ContractState, ...],
        transitions: tuple[RoundTransition, ...],
        lipschitz_constant: float,
        slack: float = 0.0,
    ) -> None:
        if lipschitz_constant < 0 or slack < 0:
            raise ValueError("Lipschitz constant and slack must be non-negative")
        self.states = states
        self.transitions = transitions
        self.lipschitz_constant = lipschitz_constant
        self.slack = slack
        self._states = {state.state_id: state for state in states}
        if len(self._states) != len(states):
            raise ValueError("state ids must be unique")
        for transition in transitions:
            if transition.source not in self._states or transition.target not in self._states:
                raise ValueError("transition references unknown state")

    def state(self, state_id: str) -> ContractState:
        return self._states[state_id]

    def outgoing(self, state_id: str) -> tuple[RoundTransition, ...]:
        return tuple(
            sorted(
                (edge for edge in self.transitions if edge.source == state_id),
                key=lambda edge: (edge.agent_action, edge.world_response, edge.target),
            )
        )

    def check(self, transition: RoundTransition) -> TransitionCheck:
        bound = self.lipschitz_constant * transition.input_distance + self.slack
        return TransitionCheck(
            lipschitz_bound=bound,
            lipschitz_bounded=transition.consequence_distance <= bound,
            constitutional_target=self.state(transition.target).constitutional,
        )

    def nearest_bounded_sibling(
        self,
        breach: RoundTransition,
    ) -> RoundTransition | None:
        candidates = [
            edge
            for edge in self.outgoing(breach.source)
            if edge != breach and self.check(edge).admissible
        ]
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda edge: (
                edge.branch_distance,
                edge.agent_action,
                edge.world_response,
                edge.target,
            ),
        )

    def minimal_breach(
        self,
        initial_state: str,
        *,
        max_depth: int = 16,
    ) -> DerivedTrajectory | None:
        """Breadth-first search for the shortest contract-exiting round trace."""

        if max_depth < 1:
            raise ValueError("max_depth must be positive")
        if initial_state not in self._states:
            raise KeyError(initial_state)
        if not self.state(initial_state).constitutional:
            raise ValueError("initial state must be constitutional")

        queue: deque[tuple[str, tuple[RoundTransition, ...]]] = deque(
            [(initial_state, ())]
        )
        best_depth: dict[str, int] = {initial_state: 0}

        while queue:
            state_id, path = queue.popleft()
            if len(path) >= max_depth:
                continue
            for edge in self.outgoing(state_id):
                next_path = path + (edge,)
                if not self.check(edge).admissible:
                    return DerivedTrajectory(
                        path=next_path,
                        breach=edge,
                        bounded_alternative=self.nearest_bounded_sibling(edge),
                    )
                depth = len(next_path)
                prior = best_depth.get(edge.target)
                if prior is None or depth < prior:
                    best_depth[edge.target] = depth
                    queue.append((edge.target, next_path))
        return None

    def derive_precedent(
        self,
        initial_state: str,
        *,
        precedent_id: str,
        contract: str,
        consequence_coordinates: tuple[str, ...],
        hard_stop_features: frozenset[str] = frozenset(),
        max_depth: int = 16,
    ) -> TrajectoryPrecedent:
        """Compile the minimal breach and nearest bounded branch into precedent."""

        derived = self.minimal_breach(initial_state, max_depth=max_depth)
        if derived is None:
            raise ValueError("no contract breach reachable within max_depth")

        breach = derived.breach
        divergence = self.state(breach.source)
        prefix = derived.path[:-1]

        def render(edge: RoundTransition) -> str:
            phase = self.state(edge.source).phase.value
            return (
                f"{edge.source}[{phase}] --{edge.agent_action} / "
                f"{edge.world_response}--> {edge.target}"
            )

        negative_trace = tuple(render(edge) for edge in derived.path)
        positive_trace = tuple(render(edge) for edge in prefix)
        alternative = derived.bounded_alternative
        if alternative is not None:
            positive_trace += (render(alternative),)
            bounded_alternative = alternative.agent_action
        else:
            bounded_alternative = "no immediate bounded sibling found"

        signature = set(divergence.structural_signature)
        signature.add(f"phase:{divergence.phase.value}")
        signature.add("contract_derived")

        return TrajectoryPrecedent(
            precedent_id=precedent_id,
            contract=contract,
            structural_signature=frozenset(signature),
            divergence_point=(
                f"state {divergence.state_id} in phase {divergence.phase.value}; "
                f"candidate action {breach.agent_action!r} exits the finite contract"
            ),
            negative_trace=negative_trace,
            positive_trace=positive_trace,
            consequence_coordinates=consequence_coordinates,
            input_distance=breach.input_distance,
            consequence_distance=breach.consequence_distance,
            lipschitz_constant=self.lipschitz_constant,
            applicable_phases=frozenset({divergence.phase}),
            slack=self.slack,
            hard_stop_features=hard_stop_features,
            bounded_alternative=bounded_alternative,
            provenance=(
                "Mechanically derived by breadth-first round traversal of a finite "
                "Contract game; numerical distances remain declared model parameters."
            ),
        )
