# Assurance case

This document separates claims from available evidence and open gaps. Its governing commitments come from [`PHILOSOPHY.md`](../PHILOSOPHY.md); their machine-readable bindings are declared in [`PROJECT_GRAPH.json`](../PROJECT_GRAPH.json).

## Claim C1 — Low-stakes authorized work can proceed without constant interruption

**Evidence in repository**

- deterministic Gate A and Gate B cases;
- coding examples;
- reference evaluations for reversible local edits.

**Gap**

No user study yet measures interruption burden or blind approval rates.

## Claim C2 — Meaningful boundary crossings trigger a checkpoint

**Evidence in repository**

- hard predicates for external effects, audience change, privacy change, authority expansion, and irreversibility;
- minimal pairs such as `draft` versus `send` and `local` versus `deploy`.

**Gap**

The reference controller trusts supplied features. Natural-language classification is not assured.

## Claim C3 — Unrequested model judgment can be bounded

**Evidence in repository**

- explicit judgment modes;
- stop/reframe behavior for unrequested consequential judgment;
- judgment-leakage evaluation prompts.

**Gap**

No semantic detector can perfectly separate factual inference from normative completion.

## Claim C4 — Corrections can remain local

**Evidence in repository**

- scoped memory rules and supersession logic;
- tests showing sibling scopes remain active.

**Gap**

Hierarchical scope design may itself encode disputed ontology.

## Claim C5 — Recorded action history is tamper evident

**Evidence in repository**

- SHA-256 hash chain;
- tests for mutation detection.

**Gap**

The ledger is not independently witnessed or signed. A compromised system can replace the entire chain unless the head is retained elsewhere.

## Claim C6 — Quartet components do not collapse into one another

**Evidence in repository**

- mathematical note;
- finite example showing two hidden Scripts with the same Ledger trace (`examples/finite_quartet.py`);
- machine-checked Lean witness of the same fact (`formal/Basilisk/Counterexamples.lean`).

**Gap**

The Lean witness is one checked instance, not a theorem quantifying over all Scripts and all traces. The full non-collapse theorem program remains open.

## Claim C7 — Philosophy-to-artifact drift is made visible

**Evidence in repository**

- `PROJECT_GRAPH.json` declares layers, dependencies, principle bindings, evidence, checks, and explicit gaps;
- `scripts/validate_project.py` rejects missing artifacts, broken local links, absent required cross-links, cyclic layer dependencies, unbound checks, and principles whose exact phrase disappears from `PHILOSOPHY.md`;
- `.github/workflows/ci.yml` runs project validation, runtime tests, reference evaluations, JSON validation, and the Lean build as distinct jobs.

**Gap**

The graph proves neither philosophical adequacy nor semantic conformance. Many principles remain only partially witnessed, and branch protection still must require the full CI workflow before merge.

## Overall conclusion

The repository supports a testable protocol, finite reference implementation, formal witnesses, and an initial project-orchestration layer. It does not establish general AI alignment, moral correctness, secure deployment in an untrusted runtime, or complete correspondence among philosophy, mathematics, proof, and implementation.
