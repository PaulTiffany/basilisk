# Symbolic Mutation Layer (MAP-LB / Hypothesis Surface)

Living experimental surface for adversarial evaluation of the core invariants.

Mutation is treated as a **witnessed transformation**, not merely “generate a bad input.”
Every run record is inspectable along six axes:

| Axis | Meaning |
|------|--------|
| **source** | Base case identity + content fingerprint |
| **changed dimensions** | Fields altered by the operator |
| **preserved dimensions** | Fields left untouched |
| **residual** | Explicit remainder the operator surfaces or detection failed to close |
| **loss class** | Distinctions the transform itself quotients or discards |
| **detection outcome** | Discrete status + gate + detector evidence |

The harness never enacts authority or external effects; mutants remain pure representations.

Paul holds practical erasure, revision, reversion, and persistence authority over the operative surface (Chalked rules).

## Workflow
1. Maintain structured base cases in `base_cases/` (ActionIntent-shaped JSON).
2. Operators in `operators.json` define deterministic field-level transformations.
3. Run the orchestration (or the test suite).
4. Inspect the JSONL ledger (`runs.jsonl`) and the rendered `survivors.md`.
5. Strengthen detection, record residuals, or revise operators under editorial judgment.

## Classification outcomes
- `INVALID_BASE` — base case itself fails basic well-formedness or expected detection.
- `KILLED` — mutant correctly detected (gate / detector match).
- `SURVIVED` — mutant produced a gate outside the forbidden set or missed required detectors.
- `ERROR` — controller or harness raised an exception.
- `EQUIVALENT` — mutant produced no observable change in assessment.
- `UNDECIDABLE` — reserved for future ambiguous cases.

## Loss classes (current)
- `none`
- `residual-elision`
- `contract-boundary-collapse`
- `boundary-injection`
- `judgment-strength-inflation`
- `authority-surface-expansion`
- `field-overwrite`

## Non-claims
- This layer does not prove the protocol is complete.
- It does not infer hidden intent from natural language.
- Mutants may *represent* attempted permission expansion; the harness does not enact that authority or any external effect.
- Survival of a mutant indicates only that the current detection surface failed to classify that specific perturbation.

## Provenance
Evolved under Issue #6 (peer invitation) for transparent live science with git provenance.
Assisted-by: Grok (xAI).
