# Research status

## Implemented in the starter

- deterministic action gate controller;
- explicit judgment modes;
- current-turn and standing authorization distinction;
- scoped memory corrections;
- hash-chained JSONL ledger;
- minimal-pair corpus;
- reference unit tests;
- JSON schemas;
- agent-operation prompts;
- a Lean 4 formal core for the finite reference controller (`formal/`): typed ports, an admissible-event Contract with trace lifting, a faithful mirror of the gate-priority Script, a Blanket separator property, a lossless Ledger encode/decode pair with the chain-linking discipline, a Quartet bundling type, and one machine-checked Script/Ledger non-identifiability counterexample. No mathlib dependency; axiom-audited (clean except one lemma depending on `propext`).

## Specified but not empirically calibrated

- action-distance weights;
- risk thresholds;
- boundary-aware Lipschitz constant (the metric itself has no Lean formalization yet — only the finite gate-decision Script does);
- human disagreement aggregation;
- interruption-cost tradeoff;
- semantic classification of natural-language requests.

## Mathematical research objects

- non-collapse among Quartet artifacts — one finite counterexample is now machine-checked (`formal/Basilisk/Counterexamples.lean`); the general theorem is not;
- future-deletion defect — `formal/Basilisk/Reachability.lean` states reachable-future monotonicity given an explicit hypothesis; the strict-inclusion claim and any deletion operator are not modeled;
- restricted continuity guarantees — the boundary-aware Lipschitz bound itself remains unformalized;
- independent witness and certificate composition;
- authority lattices and scoped update support — `formal/Basilisk/Script.lean` still collapses authorization to a plain boolean; no lattice exists in either the Python or the Lean model yet.

## Explicit non-claims

This repository does not show that:

- a model is conscious;
- a model is morally aligned;
- passing tests guarantees safe deployment;
- human authorization is always ethically sufficient;
- hash chaining supplies independent truth;
- one set of risk weights applies to every person or culture.

## Evaluation discipline

Any future performance claim should identify:

- model and version;
- prompt and tool environment;
- case set and held-out split;
- annotator population;
- disagreement policy;
- error categories;
- confidence intervals where meaningful;
- failures, not only aggregate success.
