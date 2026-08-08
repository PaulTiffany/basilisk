# Formalization plan

**Status:** the finite combinatorial core below builds in Lean 4 without mathlib and is intended to stay conservative about what has actually been formalized. The probabilistic and real-valued metric layers should follow the finite core rather than being axiomatized prematurely.

Lean modules:

```text
Basilisk/
  Port.lean                    -- typed ports, Ω_p = I_p × O_p
  Contract.lean                -- admissible-event predicate, trace lifting
  Script.lean                  -- finite mirror of controller gate logic
  Blanket.lean                 -- direct-edge separator-property shape only
  DependencyCut.lean           -- parent/child/co-parent family closure
  Ledger.lean                  -- lossless encode/decode, chain-linking discipline
  Quartet.lean                 -- four distinct artifact classes
  Reachability.lean            -- hypothesis-relative reachable-future monotonicity
  Counterexamples.lean         -- Script/Ledger non-identifiability witness
  ConstitutionalLipschitz.lean -- Lipschitz ≠ constitutional preservation
```

## What is proved now

1. **Finite typed ports and boundary-event spaces** — done (`Port.lean`), still not fully connected to the concrete Script model.
2. **Contract predicates and trace lifting** — done (`Contract.lean`).
3. **Deterministic finite-state Script gate logic** — done (`Script.lean`).
4. **Direct-edge graph separator shape** — done (`Blanket.lean`). This is *not* yet a path-separation theorem and *not* a conditional-independence theorem.
5. **Parent/child/co-parent family closure** — done (`DependencyCut.lean`). This formalizes the graph construction behind “parents, children, parents of children” only.
6. **Lossless Ledger encode/decode pair** — done (`Ledger.lean`); SHA-256 itself is not modeled.
7. **Script/Ledger non-identifiability counterexample** — done (`Counterexamples.lean`), one witnessed instance rather than a universal theorem over all Scripts.
8. **Hypothesis-relative reachable-future monotonicity** — done (`Reachability.lean`); strict loss remains open.
9. **Lipschitz boundedness does not imply constitutional preservation** — done (`ConstitutionalLipschitz.lean`) by a minimal two-point, 0-Lipschitz counterexample.
10. **Constitutional predicate preservation composes** — done (`ConstitutionalLipschitz.lean`).

## Important non-claims

- The current `Blanket.lean` does **not** prove a Bayesian-network Markov blanket theorem.
- The current graph core has no probability distribution and therefore cannot state conditional independence honestly.
- The operational action “metric” has not yet been formalized; until a separation hypothesis is supplied, the natural weighted construction should be called a **pseudometric**.
- The authority lattice is not implemented; Python and Lean still compress much of authority into booleans.
- The boundary-aware Lipschitz inequality is a target specification, not a proved property of an LLM or the reference controller.
- “Constitutional completion of integrability” is currently a programmatic construction: boundedness plus explicitly chosen preservation predicates. It is not yet a single general theorem.

## Next theorem targets

1. **Weighted pseudometric theorem.** Formalize a finite product/feature pseudometric and prove sufficient separation conditions for metricity.
2. **Lipschitz composition theorem.** Prove explicit constant multiplication in a numeric setting suitable for the finite core.
3. **Bounded + constitutional composition theorem.** Combine Lipschitz composition with `PreservesPredicate.comp`.
4. **Authority lattice.** Introduce a finite join-semilattice and prove permission monotonicity against current ∨ standing authority.
5. **Family-closure topology change.** Prove concrete graph updates that do and do not alter the parent/child/co-parent closure.
6. **Path separator connection.** Connect `Blanket.lean` to `Reachability.lean` and prove appropriate path-separation statements.
7. **Finite probability semantics.** Only after the graph layer is stable, add a finite probability model and state a Bayesian-network Markov assumption sufficient for a genuine conditional-independence blanket theorem.
8. **Boundary-aware piecewise theorem.** Characterize composition when boundary signatures stay fixed and how jump terms accumulate when they change.
9. **Minimal countermodels.** For every proposed hypothesis, seek a smallest counterexample when it is dropped.

See [`../docs/mathematical-foundations.md`](../docs/mathematical-foundations.md) for the mathematician-facing claim boundary and notation discipline.
