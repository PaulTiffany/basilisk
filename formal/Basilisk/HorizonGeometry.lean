/-
HorizonGeometry.lean — finite combinatorial substrate for the Markov 10+
research bridge.

This file deliberately stops before graded ideals or Newton polyhedra. It proves
only the finite shapes we can currently witness without importing commutative
algebra:

* exact-horizon reachability composes across summed horizons;
* a linear horizon family has a scale-free normalized profile that is stable
  across horizons;
* normalized stability alone does not certify semantic faithfulness: a stable
  aggregate may still identify distinct protected coordinates.

The last point is the guardrail that keeps the limiting-body analogy from
certifying its own encoding.
-/

import Basilisk.ProtectedTen
import Basilisk.Reachability

namespace Basilisk

/-- Reachability in exactly `n` transitions. -/
def ReachableN {W : Type} (step : W → W → Prop) : Nat → W → W → Prop
  | 0, x, y => x = y
  | n + 1, x, z => ∃ y, step x y ∧ ReachableN step n y z

/-- Proof-producing horizon composition. This is the finite combinatorial
    analogue of the bridge obligation that horizon objects compose into the
    summed horizon. -/
def ReachableN.comp {W : Type} {step : W → W → Prop} {p q : Nat} {x y z : W} :
    ReachableN step p x y → ReachableN step q y z → ReachableN step (p + q) x z := by
  intro hxy hyz
  induction p generalizing x with
  | zero =>
      have hxy' : x = y := by
        simpa [ReachableN] using hxy
      subst y
      simpa using hyz
  | succ p ih =>
      have hxy' : ∃ u, step x u ∧ ReachableN step p u y := by
        simpa [ReachableN] using hxy
      rcases hxy' with ⟨u, hxu, huy⟩
      have huz : ReachableN step (p + q) u z := ih huy
      have hstep : ReachableN step ((p + q) + 1) x z := by
        show ∃ v, step x v ∧ ReachableN step (p + q) v z
        exact ⟨u, hxu, huz⟩
      simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using hstep

/-- Two finite operational coordinates for a horizon-indexed summary. The names
    are intentionally generic: this is not yet a Newton exponent vector. -/
structure HorizonProfile where
  protectedCount : Nat
  residual : Nat
  deriving DecidableEq, Repr

namespace HorizonProfile

def add (a b : HorizonProfile) : HorizonProfile :=
  ⟨a.protectedCount + b.protectedCount, a.residual + b.residual⟩

def scale (n : Nat) (a : HorizonProfile) : HorizonProfile :=
  ⟨n * a.protectedCount, n * a.residual⟩

end HorizonProfile

/-- Cross-multiplied equality of normalized profiles. This represents equality
    of `p / n` and `q / m` without introducing rationals into the finite core. -/
def SameNormalized (n m : Nat) (p q : HorizonProfile) : Prop :=
  m * p.protectedCount = n * q.protectedCount ∧
  m * p.residual = n * q.residual

/-- The simplest graded/compositional fixture: repeat one base contribution at
    each step. -/
def LinearHorizonFamily (base : HorizonProfile) (n : Nat) : HorizonProfile :=
  HorizonProfile.scale n base

/-- Linear horizon accumulation composes exactly under horizon addition. -/
theorem linearHorizonFamily_composes (base : HorizonProfile) (p q : Nat) :
    LinearHorizonFamily base (p + q) =
      HorizonProfile.add (LinearHorizonFamily base p) (LinearHorizonFamily base q) := by
  cases base with
  | mk protectedCount residual =>
      simp [LinearHorizonFamily, HorizonProfile.scale, HorizonProfile.add, Nat.add_mul]

/-- Dividing a linear family by its horizon removes horizon scale: all positive
    horizons are cross-multiplication equivalent. -/
theorem linearHorizonFamily_normalized_stable (base : HorizonProfile) (n m : Nat) :
    SameNormalized (n + 1) (m + 1)
      (LinearHorizonFamily base (n + 1)) (LinearHorizonFamily base (m + 1)) := by
  cases base with
  | mk protectedCount residual =>
      simp [SameNormalized, LinearHorizonFamily, HorizonProfile.scale,
        Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]

/-- Deliberately bad semantic encoding: every protected Contract coordinate is
    sent to the same aggregate profile. -/
def collapsedTenProfile : TenIndex → HorizonProfile := fun _ => ⟨1, 0⟩

/-- The collapsed encoding is visibly non-injective on the protected ten. -/
theorem collapsedTenProfile_not_injective :
    ¬ Function.Injective collapsedTenProfile := by
  intro h
  have h01 : (0 : TenIndex) = (1 : TenIndex) := h rfl
  simp at h01

/-- Core Markov 10+ guard: perfect normalized stability is compatible with a
    semantically invalid collapse of protected coordinates. Geometry therefore
    cannot certify the faithfulness of the encoding that produced it. -/
theorem normalized_stability_does_not_imply_protected_faithfulness :
    (∀ i n m, SameNormalized (n + 1) (m + 1)
      (LinearHorizonFamily (collapsedTenProfile i) (n + 1))
      (LinearHorizonFamily (collapsedTenProfile i) (m + 1))) ∧
    ¬ Function.Injective collapsedTenProfile := by
  constructor
  · intro i n m
    exact linearHorizonFamily_normalized_stable (collapsedTenProfile i) n m
  · exact collapsedTenProfile_not_injective

end Basilisk
