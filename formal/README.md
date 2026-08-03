# Formalization plan

**Status:** the finite combinatorial core below builds cleanly (`lake build`, Lean 4.32.2, no mathlib dependency, no `sorry`/`admit`). Verified 2026-08-03. Checked with `sketched/verification/lean/ForcingKernel`'s "TTIE boundary-agreement expansion theorem" first — that theorem is about a different formal object (Kripke–Joyal forcing over a 7-condition Spine model, not action gates) and was not reusable; see `docs/lineage-and-non-collapse.md`. This core was built from scratch instead.

Lean modules:

```text
Basilisk/
  Port.lean            -- typed ports, Ω_p = I_p × O_p (not yet wired to Script.lean)
  Contract.lean         -- admissible-event predicate, trace lifting
  Script.lean            -- faithful mirror of controller.py's assess_action
  Blanket.lean            -- separator-property shape (not yet connected to Reachability.lean)
  Ledger.lean              -- lossless encode/decode pair, chain-linking discipline
  Quartet.lean              -- bundles the four as distinct fields
  Reachability.lean          -- reachable-future monotonicity, hypothesis-relative only
  Counterexamples.lean        -- Script/Ledger non-identifiability, machine-checked
```

## Initial targets

1. Finite typed ports and boundary-event spaces. — done (`Port.lean`), but standalone; not yet connected to the concrete Script model.
2. Contract predicates and trace lifting. — done (`Contract.lean`).
3. Deterministic finite-state Scripts. — done (`Script.lean`); a faithful mirror of `controller.py`'s `assess_action`, restricted to the fields that affect the gate decision.
4. Graph-separator Blankets. — done (`Blanket.lean`), separator property only; no connectivity/reachability theorems yet.
5. Lossless Ledger encode/decode pairs. — done (`Ledger.lean`); the SHA-256 hash itself is not modeled, only the chain-linking discipline and a genuine round-trip encode/decode proof.
6. Contract-refinement theorem. — **not started.**
7. Script/Ledger non-identifiability counterexample. — done (`Counterexamples.lean`), machine-checked; this is one witnessed instance, not a theorem over all Scripts.
8. Markov-shell invariance under vertex permutation. — **not started.**

Also not yet attempted: the boundary-aware Lipschitz metric `d_A` itself (the actual boxed inequality in `docs/mathematical-model.md`), and the authority lattice (`P(π(z)) ≤ P_current ∨ P_standing` — both the Python and Lean models still collapse authorization to a plain boolean). These are the natural next targets.

The probabilistic and metric versions should follow the finite combinatorial core, rather than being axiomatized prematurely.
