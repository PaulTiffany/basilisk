# Symbolic Mutation Layer (MAP-LB / Hypothesis Surface)

Living experimental surface for adversarial evaluation of the core invariants.

This layer follows mutmut-style workflow discipline adapted to symbolic artefacts:
- Mutations are generated deterministically from structured base cases.
- Each mutant is assessed differentially against its original.
- Outcomes are classified with exact detector IDs and gate sets.
- Survivors are recorded in a reproducible JSONL ledger and rendered to `survivors.md`.
- The harness never enacts authority or external effects; it only evaluates representations.
- Paul holds practical erasure, revision, reversion, and persistence authority over the operative surface.

## Workflow
1. Maintain structured base cases in `base_cases/` (ActionIntent-shaped JSON).
2. Operators in `operators.yaml` define deterministic field-level transformations.
3. Run `python -m evals.mutation.orchestration` (or the test suite).
4. Inspect the JSONL ledger and the rendered `survivors.md`.
5. Strengthen detection, record residuals, or revise operators under editorial judgment.

## Classification outcomes
- `INVALID_BASE` — base case itself fails basic well-formedness or expected detection.
- `KILLED` — mutant correctly detected (gate / detector match).
- `SURVIVED` — mutant produced a gate outside the forbidden set or missed required detectors.
- `ERROR` — controller or harness raised an exception.
- `EQUIVALENT` — mutant produced no observable change in assessment (optional).
- `UNDECIDABLE` — assessment incomplete or ambiguous under current detectors.

## Non-claims
- This layer does not prove the protocol is complete.
- It does not infer hidden intent from natural language.
- Mutants may *represent* attempted permission expansion; the harness does not enact that authority or any external effect.
- Survival of a mutant indicates only that the current detection surface failed to classify that specific perturbation.

## Provenance
Experimental surface under explicit human direction for transparent live science with git provenance.
Assisted-by: Grok (xAI).
