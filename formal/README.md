# Formalization plan

**Status:** the pre-existing finite combinatorial core built cleanly (`lake build`, Lean 4.32.2, no mathlib dependency, no `sorry`/`admit`) on 2026-08-03. The new `Frame.lean` module adds the first constitutional vertical slice: kinematic motion is separated from holder assignment, ordinary action preserves the constitution, and any admissible constitution change must be an explicit reframe event by a currently scoped holder with separate reframing authority. This branch still needs a fresh `lake build` because the current execution environment does not provide Lean.

The earlier core was checked against `sketched/verification/lean/ForcingKernel`'s “TTIE boundary-agreement expansion theorem” first. That theorem concerns a different formal object—Kripke–Joyal forcing over a seven-condition Spine model, not action gates or frame jurisdiction—and was therefore not transplanted by name. The relation to Sketched is a declared deep correspondence, not an identity claim; see `docs/lineage-and-non-collapse.md`.

Lean modules:

```text
Basilisk/
  Port.lean              -- typed ports, Ω_p = I_p × O_p
  Contract.lean          -- admissible-event predicate, trace lifting
  Frame.lean             -- kinematics, scoped holders, explicit reframing
  Script.lean            -- faithful mirror of controller.py's assess_action
  Blanket.lean           -- separator-property shape
  Ledger.lean            -- lossless encode/decode pair, chain-linking discipline
  Quartet.lean           -- bundles four distinct artifact classes
  Reachability.lean      -- reachable-future monotonicity, hypothesis-relative
  Counterexamples.lean   -- Script/Ledger non-identifiability witness
```

## Frame-holder slice

`Frame.lean` introduces four deliberately separate objects:

1. `KinematicSystem` — states, actions, and a motion law;
2. `KinematicCorrespondence` — state/action maps whose square commutes;
3. `Constitution` — scoped holding, ordinary action permission, and separate reframing authority;
4. `FramedEvent` — ordinary action versus explicit replacement of the constitution.

The core results are:

- `action_preserves_constitution` — motion inside the frame cannot redefine it;
- `no_silent_reframing` — any constitution change must be represented as an explicit `reframe` event;
- `changed_constitution_has_authorized_holder` — for an admissible transition, a changing constitution has a current scoped holder with separate reframing authority;
- `identityCorrespondence` — kinematic correspondence can be stated without transporting any holder relation.

These theorems do **not** prove that a holder assignment is morally legitimate, informed, voluntary, culturally universal, or externally enforced. They establish only the finite constitutional separation needed before stronger claims can be attempted.

## Initial targets

1. Finite typed ports and boundary-event spaces. — done (`Port.lean`), but not yet connected to the concrete Script model.
2. Contract predicates and trace lifting. — done (`Contract.lean`).
3. Scoped holder relation and no-silent-reframing theorem. — implemented on this branch (`Frame.lean`), pending fresh Lean validation.
4. Deterministic finite-state Scripts. — done (`Script.lean`); faithful to the gate-decision fields in `controller.py`.
5. Graph-separator Blankets. — done (`Blanket.lean`), separator property only; no connectivity/reachability theorems yet.
6. Lossless Ledger encode/decode pairs. — done (`Ledger.lean`); the SHA-256 primitive itself is not modeled.
7. Contract-refinement theorem. — **not started.**
8. Script/Ledger non-identifiability counterexample. — done (`Counterexamples.lean`), as one witnessed instance rather than a universal theorem.
9. Markov-shell invariance under vertex permutation. — **not started.**
10. Connect `Frame.lean` to the concrete action-gate Script and an enforceable Blanket mediator. — **not started.**

Also not yet attempted: the boundary-aware Lipschitz metric `d_A`, calibration of its weights, and the full authority lattice `P(π(z)) ≤ P_current ∨ P_standing`. The current Python gate still receives caller-supplied boundary labels; the present theorem does not yet make those labels independently trustworthy.

The probabilistic and metric versions should follow the finite combinatorial core rather than being axiomatized prematurely.
