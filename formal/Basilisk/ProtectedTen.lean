/-
ProtectedTen.lean — preservation of the original ten Contract coordinates under
growth.

The protected basis is represented by an embedding with a left inverse. Novel
interaction structure may be added around that basis, but an admissible growth
map must commute on the protected coordinates. A later quotient or projection
is non-collapsing on the ten whenever it still admits recovery of those
coordinates.

Only the left-inverse equations constrain recovery. Its values away from the
embedded protected coordinates are intentionally unspecified.
-/

namespace Basilisk

/-- A representation of protected generators with a recovery map that is a
    left inverse on those generators. -/
structure ProtectedEmbedding (A X : Type) where
  embed : A → X
  recover : X → A
  leftInverse : ∀ a, recover (embed a) = a

/-- The ten original Contract coordinates. -/
abbrev TenIndex := Fin 10

/-- A protected realization of the original ten coordinates in a larger space. -/
abbrev ProtectedTen (X : Type) := ProtectedEmbedding TenIndex X

/-- A left inverse prevents two protected generators from being identified. -/
theorem protectedEmbedding_injective {A X : Type}
    (p : ProtectedEmbedding A X) :
    Function.Injective p.embed := by
  intro a b h
  calc
    a = p.recover (p.embed a) := (p.leftInverse a).symm
    _ = p.recover (p.embed b) := congrArg p.recover h
    _ = b := p.leftInverse b

/-- A growth step may enlarge the ambient space, but it must commute on each
    protected Contract coordinate. -/
structure ProtectedGrowth (X Y : Type)
    (source : ProtectedTen X) (target : ProtectedTen Y) where
  step : X → Y
  commutes : ∀ i, step (source.embed i) = target.embed i

/-- Every original coordinate remains exactly recoverable after protected
    growth. -/
theorem protectedGrowth_recovers {X Y : Type}
    (source : ProtectedTen X) (target : ProtectedTen Y)
    (g : ProtectedGrowth X Y source target) (i : TenIndex) :
    target.recover (g.step (source.embed i)) = i := by
  rw [g.commutes i, target.leftInverse i]

/-- Protected growth cannot collapse two distinct original coordinates. -/
theorem protectedGrowth_preserves_distinction {X Y : Type}
    (source : ProtectedTen X) (target : ProtectedTen Y)
    (g : ProtectedGrowth X Y source target)
    (i j : TenIndex) (hij : i ≠ j) :
    g.step (source.embed i) ≠ g.step (source.embed j) := by
  intro h
  apply hij
  calc
    i = target.recover (g.step (source.embed i)) :=
      (protectedGrowth_recovers source target g i).symm
    _ = target.recover (g.step (source.embed j)) := congrArg target.recover h
    _ = j := protectedGrowth_recovers source target g j

/-- Any later map, quotient, or projection remains non-collapsing on the ten
    whenever the ten are still recoverable through that map. -/
theorem protectedTen_no_collapse_under_map {X Y : Type}
    (p : ProtectedTen X) (q : X → Y) (recoverY : Y → TenIndex)
    (hrecover : ∀ i, recoverY (q (p.embed i)) = i) :
    Function.Injective (fun i => q (p.embed i)) := by
  intro i j h
  calc
    i = recoverY (q (p.embed i)) := (hrecover i).symm
    _ = recoverY (q (p.embed j)) := congrArg recoverY h
    _ = j := hrecover j

/-- Protected growth composes: preserving the ten at each stage preserves them
    across the composite trajectory. -/
def ProtectedGrowth.comp {X Y Z : Type}
    {source : ProtectedTen X} {middle : ProtectedTen Y} {target : ProtectedTen Z}
    (g₁ : ProtectedGrowth X Y source middle)
    (g₂ : ProtectedGrowth Y Z middle target) :
    ProtectedGrowth X Z source target where
  step := fun x => g₂.step (g₁.step x)
  commutes := by
    intro i
    rw [g₁.commutes i, g₂.commutes i]

end Basilisk
