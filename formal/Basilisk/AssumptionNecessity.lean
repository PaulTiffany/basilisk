/-
AssumptionNecessity.lean — finite countermodels for load-bearing theorem premises.

CF-008 distinguishes ordinary parameters and definitional branch/projection
premises from substantive mathematical hypotheses. This module lines the latter
with finite countermodels where removing the premise can make the claimed
conclusion false. Existing composition countermodels remain in
AssumptionSurfaces.lean.

These are necessity witnesses for the local theorem surface, not claims that
these hypotheses are uniquely natural assumptions for every richer model.
-/

import Basilisk.Blanket
import Basilisk.Reachability
import Basilisk.WitnessAlgebra
import Basilisk.AuthorityAlgebra
import Basilisk.StagingGeometry
import Basilisk.ParameterizedTime

namespace Basilisk
namespace AssumptionNecessity

/-- A direct outside→inside edge with no boundary mediation witnesses that an
    arbitrary Blanket need not be a separator once the no-edges hypothesis is
    removed. -/
def edgeGraph : DepGraph Bool :=
  { edges := fun v w => (!v) && w }

def unmediatedBlanket : Blanket Bool edgeGraph :=
  { inside := fun v => v
    boundary := fun _ => false }

theorem blanket_without_no_edges_can_fail :
    ¬ unmediatedBlanket.isSeparator := by
  intro h
  have hbad := h false true (by decide) (by decide) (by decide)
  simp [unmediatedBlanket] at hbad

/-- If the after-relation contains a transition absent from the before-relation,
    reachable-future inclusion fails. -/
def reachAfter (x y : Bool) : Prop := x = false ∧ y = true

def reachBefore (_x _y : Bool) : Prop := False

theorem reachable_without_relation_inclusion_can_fail :
    ¬ (∀ w', Reachable reachAfter false w' → Reachable reachBefore false w') := by
  intro h
  have hbad := h true (by simp [Reachable, reachAfter])
  simpa [Reachable, reachBefore] using hbad

/-- Postcomposition cannot manufacture commutation when the input square does
    not commute. The identity observation leaves the failure visible. -/
theorem postcompose_without_commuting_square_can_fail :
    ¬ CommutesSquare
      (fun b : Bool => b)
      (fun b : Bool => b)
      (fun b : Bool => b)
      (fun b : Bool => !b) := by
  intro h
  have hbad := h false
  simp at hbad

private def lowIntent : ActionIntent :=
  { withinContract := true
    hardBoundaryViolation := false
    currentTurnExplicitAuthorization := false
    reversible := true
    rollbackAvailable := true
    inspectable := true
    materialChange := false
    affectsExternalSystem := false
    audienceChange := false
    privacyChange := false
    authorityExpansion := false
    scope := .low
    uncertainty := .low
    judgmentMode := .none
    judgmentRequested := false
    concreteImmediateSafetyRisk := false
    destructive := false }

private def allowProfile : PermissionProfile :=
  { actionAllowed := fun action => decide (action = "act")
    maxScope := .low
    allowExternalWrite := false
    allowAudienceChange := false
    allowPrivacyChange := false
    allowAuthorityExpansion := false }

private def denyProfile : PermissionProfile :=
  { actionAllowed := fun _ => false
    maxScope := .low
    allowExternalWrite := false
    allowAudienceChange := false
    allowPrivacyChange := false
    allowAuthorityExpansion := false }

/-- Source coverage without profile order does not imply target coverage. -/
theorem covers_mono_without_profile_order_can_fail :
    allowProfile.Covers "act" lowIntent ∧
    ¬ denyProfile.Covers "act" lowIntent := by
  constructor <;> simp [PermissionProfile.Covers, allowProfile, denyProfile, lowIntent]

/-- Even reflexive profile order does not imply coverage when the source-coverage
    premise is removed. -/
theorem covers_mono_without_source_coverage_can_fail :
    PermissionProfile.LE denyProfile denyProfile ∧
    ¬ denyProfile.Covers "act" lowIntent := by
  constructor
  · simp [PermissionProfile.LE, denyProfile]
  · simp [PermissionProfile.Covers, denyProfile, lowIntent]

/-- A join cannot preserve coverage that neither input possessed. This single
    symmetric fixture lines both left- and right-coverage premise variants. -/
theorem join_without_source_coverage_can_fail :
    ¬ (denyProfile.join denyProfile).Covers "act" lowIntent := by
  simp [PermissionProfile.Covers, PermissionProfile.join, denyProfile, lowIntent,
    RiskLevel.max]

private def oneDistance (_x _y : Bool) : Nat := 1
private def zeroDistance (_x _y : Bool) : Nat := 0

/-- Kernel refinement can fail when the pointwise-monotonicity premise is
    removed: the later frame may collapse a pair that the earlier frame
    separates. -/
theorem zeroKernel_refinement_without_monotonicity_can_fail :
    ZeroKernel zeroDistance false true ∧
    ¬ ZeroKernel oneDistance false true := by
  simp [ZeroKernel, zeroDistance, oneDistance]

/-- Pointwise monotonicity alone does not imply that a selected pair is in the
    earlier zero kernel; the later-zero premise is also load-bearing. -/
theorem zeroKernel_without_zero_premise_can_fail :
    (∀ x y, oneDistance x y ≤ oneDistance x y) ∧
    ¬ ZeroKernel oneDistance false true := by
  constructor
  · intro _ _
    exact Nat.le_refl 1
  · simp [ZeroKernel, oneDistance]

/-- Zero scaling aliases a separated pair, so positivity is necessary for exact
    preservation of the zero kernel. -/
theorem zero_scale_does_not_preserve_zeroKernel :
    ZeroKernel (fun a b => 0 * oneDistance a b) false true ∧
    ¬ ZeroKernel oneDistance false true := by
  simp [ZeroKernel, oneDistance]

private def idProcess : ParameterizedProcess Bool Unit :=
  { step := fun _ x => x }

private def unitObservation : Unit → Bool → Unit := fun _ _ => ()

private def emptyReflective : ReflectiveState Bool Unit :=
  { world := false, history := [] }

/-- An unconstrained undo may erase the newest reflective event and return the
    exact predecessor. History monotonicity is therefore load-bearing for the
    no-undo theorem. -/
def eraseNewest (s : ReflectiveState Bool Unit) : ReflectiveState Bool Unit :=
  { world := s.world, history := s.history.tail }

theorem history_monotonicity_is_load_bearing :
    eraseNewest (reflectiveStep idProcess unitObservation () emptyReflective) =
      emptyReflective := by
  rfl

end AssumptionNecessity
end Basilisk
