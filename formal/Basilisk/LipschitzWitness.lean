/-
LipschitzWitness.lean — Lean instantiation of
`verification/lipschitz_counterexample.json`.

Source SHA-256:
755992326f6ad45b1f5b5be02af942ee3b1fa2fa7225079487ae717d6dba2399
-/

import Basilisk.ConstitutionalLipschitz

namespace Basilisk

/-- Shared finite witness: the registered constant collapse is 0-Lipschitz
    and fails the registered constitutional predicate. -/
theorem shared_lipschitz_counterexample :
    IsLipschitzNat twoPointDist twoPointDist 0 collapseToBad ∧
    ¬ PreservesPredicate collapseToBad
      (fun _ => True)
      (fun y => y = TwoPoint.good) := by
  exact ⟨collapseToBad_zero_lipschitz, collapseToBad_not_constitutional⟩

end Basilisk
