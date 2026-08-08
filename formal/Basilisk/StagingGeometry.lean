/-
StagingGeometry.lean — frame-indexed constraint staging without ontological hierarchy.

The index k names a frame/active-constraint presentation. The basic geometry is
unchanged in kind across stages: cumulative nonnegative components can refine
zero-distance equivalence classes, while positive rescaling of a frame preserves
the zero kernel exactly.
-/

namespace Basilisk

/-- Zero-distance relation induced by a Nat-valued operational distance. -/
def ZeroKernel {α : Type} (d : α → α → Nat) (x y : α) : Prop := d x y = 0

/-- Generic staging meta-theorem: pointwise enlargement of distance can only
    refine (never enlarge) the zero-distance equivalence relation. -/
theorem zeroKernel_refines_of_pointwise_le
    {α : Type} {dₖ dₖ₁ : α → α → Nat}
    (hmono : ∀ x y, dₖ x y ≤ dₖ₁ x y)
    {x y : α}
    (hzero : ZeroKernel dₖ₁ x y) :
    ZeroKernel dₖ x y := by
  unfold ZeroKernel at *
  have hle : dₖ x y ≤ 0 := by
    simpa [hzero] using hmono x y
  exact Nat.eq_zero_of_le_zero hle

/-- Positive frame scaling preserves the zero kernel. This is a change of
    presentation/scale, not a move to a different ontological level. -/
theorem positive_scale_preserves_zeroKernel
    {α : Type} (d : α → α → Nat) (c : Nat) (hc : 0 < c) (x y : α) :
    ZeroKernel (fun a b => c * d a b) x y ↔ ZeroKernel d x y := by
  unfold ZeroKernel
  cases c with
  | zero => cases hc
  | succ n => simp

/-- Adding a nonnegative component is a canonical staged frame transition. -/
theorem added_component_refines_zeroKernel
    {α : Type} (d component : α → α → Nat) {x y : α}
    (hzero : ZeroKernel (fun a b => d a b + component a b) x y) :
    ZeroKernel d x y := by
  apply zeroKernel_refines_of_pointwise_le
    (dₖ := d)
    (dₖ₁ := fun a b => d a b + component a b)
  · intro a b
    exact Nat.le_add_right (d a b) (component a b)
  · exact hzero

/-- Four-state fixture: first frame aliases 0~1 and 2~3; adding a second
    component separates 0 from 1 while retaining 2~3. -/
def stageOne : Nat → Nat → Nat := fun x y =>
  if x < 2 = y < 2 then 0 else 1

def stageTwo : Nat → Nat → Nat := fun x y =>
  if x = y then 0
  else if (x = 2 ∧ y = 3) ∨ (x = 3 ∧ y = 2) then 0
  else 1

theorem fixture_strict_refinement :
    ZeroKernel stageOne 0 1 ∧
    ¬ ZeroKernel stageTwo 0 1 ∧
    ZeroKernel stageTwo 2 3 := by
  decide

end Basilisk
