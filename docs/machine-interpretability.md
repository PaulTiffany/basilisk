# Machine interpretability

Basilisk's machine-readable assurance surface is intentionally split into canonical registries rather than one duplicated monolith. `verification/interpretability_index.json` is the entrypoint that names those sources and their join relations.

The deterministic resolver is `verification/query_project.py`.

Examples:

```bash
python3 verification/query_project.py summary
python3 verification/query_project.py claim C-MATH-008
python3 verification/query_project.py frontier CF-003
python3 verification/query_project.py all
```

The output is deterministic JSON. A claim view resolves its canonical statement/status/dependencies, Core/Theory/Bridge placement, exact provenance bindings, formal theorem symbols when present, and witness-graph transports/agreements when registered. A frontier view resolves open versus closed state, scheduling for open items, and closure claims/evidence for closed items.

`verification/check_machine_interpretability.py` validates the joins. In particular it requires every claim to have one scope placement and at least one exact provenance binding; Lean theorem claims must resolve to a formal-inventory module consistent with their bound Lean artifact; open frontier items must have schedules while closed items must not; closure claims/evidence and claim dependencies must resolve.

`verification/meta_mutation_machine_interpretability.py` attacks this surface by deleting claim evidence, drifting Lean module linkage, and reactivating closed frontier debt. These attacks are included in `make interpret`.

## Important non-claim

Machine interpretability is not epistemic correctness. The interface makes the project's declared semantics, evidence topology, dependencies, and debt state reconstructible without requiring a model to infer repository conventions from prose. It does not make any underlying theorem, engineering mechanism, empirical witness, or safety claim stronger than its declared evidence status.

The intended invariant is:

> important distinctions should be represented redundantly enough to inspect, but joined explicitly enough that disagreement or drift is mechanically visible.
