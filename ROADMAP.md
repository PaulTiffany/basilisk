# Roadmap

## Milestone 0 — Executable starter (this repository)

- four action gates;
- explicit authority and boundary fields;
- hash-chained reference ledger;
- scoped memory corrections;
- minimal-pair evaluation corpus;
- JSON schemas and vendor-neutral prompts.

## Milestone 1 — Empirical calibration

- collect annotated human decisions across coding, research, communication, and administrative tasks;
- estimate weights and thresholds from held-out data;
- measure interruption burden and authority overshoot separately;
- report disagreement rather than collapsing annotators into one unmarked label.

## Milestone 2 — Adapter layer

- adapters for common agent runtimes;
- tool manifests mapped to Contract permissions;
- external-write interceptors;
- append-only signed ledgers with independent storage;
- policy-diff visualization before contract changes.

## Milestone 3 — Adversarial assurance

- prompt perturbation and paraphrase testing;
- permission-laundering attacks;
- ledger omission and rewrite attacks;
- memory-scope poisoning;
- multi-agent collusion and confused-deputy cases;
- rollback drills.

## Milestone 4 — Formal core

- finite action gates and authority lattice in Lean;
- non-collapse results among Contract, Script, Blanket, and Ledger;
- boundary-aware continuity theorem for a restricted controller;
- explicit trusted-computing-base model.

## Non-goals

- declaring a system aligned from passing this test suite;
- encoding one universal human value function;
- replacing human judgment with model synthesis;
- forcing human approval for every trivial operation.
