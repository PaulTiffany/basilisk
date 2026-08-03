"""Finite sanity model for the Basilisk quartet.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Sequence, TypeVar

I = TypeVar("I", bound=Hashable)
O = TypeVar("O", bound=Hashable)
M = TypeVar("M", bound=Hashable)


@dataclass(frozen=True)
class Event:
    ingress: Hashable
    egress: Hashable


@dataclass
class Contract:
    permits: Callable[[Event], bool]

    def permits_trace(self, trace: Sequence[Event]) -> bool:
        return all(self.permits(event) for event in trace)


@dataclass
class DeterministicScript:
    step: Callable[[Hashable, Hashable], tuple[Hashable, Hashable]]

    def run(self, state: Hashable, inputs: Iterable[Hashable]) -> tuple[Hashable, list[Event]]:
        trace: list[Event] = []
        current = state
        for ingress in inputs:
            current, egress = self.step(current, ingress)
            trace.append(Event(ingress, egress))
        return current, trace


@dataclass
class LosslessLedger:
    records: tuple[Event, ...]

    @classmethod
    def encode(cls, trace: Sequence[Event]) -> "LosslessLedger":
        return cls(tuple(trace))

    def decode(self) -> tuple[Event, ...]:
        return self.records


def certificate(contract: Contract, ledger: LosslessLedger) -> bool:
    return contract.permits_trace(ledger.decode())


def main() -> None:
    # Contract: output must equal input parity.
    contract = Contract(lambda event: event.egress == (int(event.ingress) % 2))

    # Two non-isomorphic internal scripts induce the same boundary trace.
    script_a = DeterministicScript(lambda state, ingress: (state, int(ingress) % 2))
    script_b = DeterministicScript(lambda state, ingress: (1 - int(state), int(ingress) % 2))

    _, trace_a = script_a.run(0, [0, 1, 2, 3])
    final_b, trace_b = script_b.run(0, [0, 1, 2, 3])

    assert trace_a == trace_b
    assert final_b == 0

    ledger = LosslessLedger.encode(trace_a)
    assert ledger.decode() == tuple(trace_a)
    assert certificate(contract, ledger)

    print("finite quartet sanity checks passed")
    print("same ledger trace, distinct hidden scripts: confirmed")


if __name__ == "__main__":
    main()
