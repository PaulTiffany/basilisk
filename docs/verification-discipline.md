# White-box verification discipline

Basilisk treats verification machinery as part of the scientific surface.

## Derived artifacts

Large exhaustive tables are not repository source state when they can be reconstructed deterministically from a smaller executable law. The 11-bit gate-projection table is therefore recomputed in CI from `src/map_lb/gate_projection.py` and checked for:

- complete coverage of all 2,048 projections;
- deterministic repeated traversal;
- canonical JSON round-trip behavior;
- exact agreement between encoded gate counts and the recomputed table.

`verification/render_gate_projection_exhaustive.py` may still render the full JSON artifact on demand for inspection. The generated table itself is not committed.

## Formal witnesses

Lean witnesses should expose the mechanism needed for the proof rather than rely on opaque proposition-level computation when an explicit reduction or witness is available. This keeps failures local and interpretable across Lean toolchain changes.

## CI policy

CI is a public witness, not a substitute for understanding. Intermediate cleanup commits may use `[skip ci]` so one coherent repair tranche consumes one certification run; the final tranche commit must run the public verification surface.
