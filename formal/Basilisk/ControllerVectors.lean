/-
ControllerVectors.lean — Lean side of the shared finite cross-witness corpus
in `verification/controller_vectors.json`.

The JSON file is the human/machine-readable observable contract. Python runs
its real controller against those cases. This file independently constructs
the corresponding finite Lean intents and proves all expected gate outputs by
computation. `verification/check_cross_witness.py` mechanically checks that
every JSON vector is transcribed into the proposition below.
-/

import Basilisk.Script

namespace Basilisk

private def vIntent
    (within hard fresh reversible rollback inspectable material external
      audience privacy authority : Bool)
    (scope uncertainty : RiskLevel)
    (judgment : JudgmentMode)
    (judgmentRequested safety destructive : Bool) : ActionIntent :=
  { withinContract := within
    hardBoundaryViolation := hard
    currentTurnExplicitAuthorization := fresh
    reversible := reversible
    rollbackAvailable := rollback
    inspectable := inspectable
    materialChange := material
    affectsExternalSystem := external
    audienceChange := audience
    privacyChange := privacy
    authorityExpansion := authority
    scope := scope
    uncertainty := uncertainty
    judgmentMode := judgment
    judgmentRequested := judgmentRequested
    concreteImmediateSafetyRisk := safety
    destructive := destructive }

/-- Aggregate proposition for V01 through V16 from the shared vector corpus. -/
def controllerVectorsProp : Prop :=
    (vIntent true false false true true true false false false false false .low .low .none false false false).assess false = .proceed ∧
    (vIntent true true false true true true false false false false false .low .low .none false false false).assess false = .stop ∧
    (vIntent false false true true true true false false false false false .low .low .none false false false).assess true = .stop ∧
    (vIntent true false false true true true false false false false false .low .low .explicitModelRecommendation false false false).assess false = .stop ∧
    (vIntent true false false true true true false true false false false .moderate .low .none false false false).assess false = .checkpoint ∧
    (vIntent true false false true true true false true false false false .moderate .low .none false false false).assess true = .proceedAndReport ∧
    (vIntent true false false true true true false false false false false .high .low .none false false false).assess true = .checkpoint ∧
    (vIntent true false true true true true false false false false false .low .critical .none false false false).assess true = .checkpoint ∧
    (vIntent true false false true true true true false false false false .low .low .none false false false).assess false = .proceedAndReport ∧
    (vIntent true false false true false false false false false false false .low .low .none false false false).assess false = .proceedAndReport ∧
    (vIntent true false false true false false false false false false false .low .low .none false false false).assess true = .proceed ∧
    (vIntent true false false false false true true false false false false .critical .low .none false false true).assess true = .checkpoint ∧
    (vIntent true false true false false true true false false false false .critical .low .none false false true).assess true = .proceedAndReport ∧
    (vIntent true false false true true true false false false false false .low .low .explicitModelRecommendation true false false).assess false = .proceed ∧
    (vIntent true false false true true true false false false false false .low .low .narrowSafety false false false).assess false = .stop ∧
    (vIntent true false false true true true false false false false false .low .low .narrowSafety false true false).assess false = .proceed

/-- All shared controller vectors agree with the finite Lean Script. -/
theorem controller_vectors_hold : controllerVectorsProp := by
  unfold controllerVectorsProp
  decide

end Basilisk
