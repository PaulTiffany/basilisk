/-
AssumptionSurfaces.lean — finite countermodels lining the exterior of
`PreservesPredicate.comp`.

The composition theorem assumes both hT and hS. These witnesses show that
neither hypothesis is decorative: remove either one and the composition
conclusion can fail on the same two-point carrier used by the Lipschitz
counterexample.
-/

import Basilisk.ConstitutionalLipschitz

namespace Basilisk

/-- Dropping the first preservation hypothesis `hT` can make composition fail,
    even when the second map preserves its declared predicate. -/
theorem preserves_comp_needs_hT :
    ∃ T S : TwoPoint → TwoPoint,
      PreservesPredicate S (fun y => y = TwoPoint.good) (fun z => z = TwoPoint.good) ∧
      ¬ PreservesPredicate (fun x => S (T x)) (fun _ => True) (fun z => z = TwoPoint.good) := by
  refine ⟨collapseToBad, id, ?_, ?_⟩
  · intro y hy
    exact hy
  · intro h
    have hgood : (id (collapseToBad TwoPoint.good)) = TwoPoint.good :=
      h TwoPoint.good True.intro
    simp [collapseToBad] at hgood

/-- Dropping the second preservation hypothesis `hS` can make composition fail,
    even when the first map preserves its declared predicate. -/
theorem preserves_comp_needs_hS :
    ∃ T S : TwoPoint → TwoPoint,
      PreservesPredicate T (fun _ => True) (fun _ => True) ∧
      ¬ PreservesPredicate (fun x => S (T x)) (fun _ => True) (fun z => z = TwoPoint.good) := by
  refine ⟨id, collapseToBad, ?_, ?_⟩
  · intro x _
    exact True.intro
  · intro h
    have hgood : collapseToBad (id TwoPoint.good) = TwoPoint.good :=
      h TwoPoint.good True.intro
    simp [collapseToBad] at hgood

end Basilisk
