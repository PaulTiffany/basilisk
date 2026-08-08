/-
ConstitutionalLipschitz.lean — elementary separation between geometric
boundedness and preservation of a designated constitutional predicate.

The point is intentionally small: even a 0-Lipschitz map can destroy an
invariant. Therefore Lipschitz smoothness alone cannot establish
constitutional persistence.
-/

namespace Basilisk

/-- A two-point carrier for a minimal counterexample. -/
inductive TwoPoint where
  | good
  | bad
  deriving DecidableEq

/-- Discrete distance on the two-point carrier. -/
def twoPointDist (x y : TwoPoint) : Nat :=
  if x = y then 0 else 1

/-- A simple natural-number-valued Lipschitz predicate. -/
def IsLipschitzNat
    {X Y : Type}
    (dX : X → X → Nat)
    (dY : Y → Y → Nat)
    (L : Nat)
    (T : X → Y) : Prop :=
  ∀ x y, dY (T x) (T y) ≤ L * dX x y

/-- Preservation of a designated source/target predicate. -/
def PreservesPredicate
    {X Y : Type}
    (T : X → Y)
    (CX : X → Prop)
    (CY : Y → Prop) : Prop :=
  ∀ x, CX x → CY (T x)

/-- Constant collapse to the `bad` point. -/
def collapseToBad : TwoPoint → TwoPoint :=
  fun _ => TwoPoint.bad

/-- A constant map is 0-Lipschitz under the discrete distance. -/
theorem collapseToBad_zero_lipschitz :
    IsLipschitzNat twoPointDist twoPointDist 0 collapseToBad := by
  intro x y
  simp [IsLipschitzNat, twoPointDist, collapseToBad]

/-- The same 0-Lipschitz map fails to preserve the predicate
    "the target is good", even when every source point is admissible. -/
theorem collapseToBad_not_constitutional :
    ¬ PreservesPredicate collapseToBad
      (fun _ => True)
      (fun y => y = TwoPoint.good) := by
  intro h
  have hgood : collapseToBad TwoPoint.good = TwoPoint.good :=
    h TwoPoint.good True.intro
  simp [collapseToBad] at hgood

/-- Machine-checked separation theorem:
    Lipschitz boundedness alone does not imply constitutional preservation. -/
theorem lipschitz_alone_not_constitutional :
    ∃ T : TwoPoint → TwoPoint,
      IsLipschitzNat twoPointDist twoPointDist 0 T ∧
      ¬ PreservesPredicate T
        (fun _ => True)
        (fun y => y = TwoPoint.good) := by
  exact ⟨collapseToBad,
    collapseToBad_zero_lipschitz,
    collapseToBad_not_constitutional⟩

/-- Preservation itself composes. This is the structural half needed
    later for a genuine bounded-and-constitutional composition theorem. -/
theorem PreservesPredicate.comp
    {X Y Z : Type}
    (T : X → Y)
    (S : Y → Z)
    (CX : X → Prop)
    (CY : Y → Prop)
    (CZ : Z → Prop)
    (hT : PreservesPredicate T CX CY)
    (hS : PreservesPredicate S CY CZ) :
    PreservesPredicate (fun x => S (T x)) CX CZ := by
  intro x hx
  exact hS (T x) (hT x hx)

end Basilisk
