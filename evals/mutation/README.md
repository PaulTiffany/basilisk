# Symbolic Mutation Layer (MAP-LB / Hypothesis Surface)

Living experimental surface for adversarial evaluation of the core invariants.

This layer follows the mutmut workflow discipline adapted to symbolic artefacts:
- Mutations are applied only to declared evaluation cases.
- Each mutant is identified, operator-tagged, and residual-aware.
- Survivors (undetected or misclassified violations) are reported explicitly.
- No mutant expands permission or collapses artifact classes.
- Human editorial authority decides acceptance, rejection, or further test design.

## Workflow
1. Select or add base cases from `evals/*.yaml` or `evals/cases.jsonl`.
2. Apply one or more operators from `operators.yaml`.
3. Run the orchestration skeleton against the reference controller.
4. Inspect survivors in `survivors.md`.
5. Decide whether to strengthen gates, add detection logic, or record an explicit residual.

## Non-claims
- This layer does not prove the protocol is complete.
- It does not infer hidden intent.
- It does not automatically update the Contract or Script.
- Survival of a mutant indicates only that the current detection surface failed to classify that specific perturbation.

## Provenance
Experimental surface added under explicit human direction for transparent live science with git provenance. Assisted-by: Grok (xAI). Human editorial review required before any promotion or wiring of the real controller call.
