/-
GateProjection.lean — finite constitutional quotient that fully determines ActionGate.

The runtime system carries richer metadata, authority provenance, timestamps, and
boundary diagnostics. Once standing authority has been reduced to `authorized`,
the gate itself depends only on the eleven Bool coordinates below.
-/

import Basilisk.Script

namespace Basilisk

structure GateProjection where
  hardBoundaryViolation : Bool
  withinContract : Bool
  unrequestedModelJudgment : Bool
  criticalDestructive : Bool
  currentTurnExplicitAuthorization : Bool
  boundaryCrossing : Bool
  authorized : Bool
  highScope : Bool
  criticalUncertainty : Bool
  materialChange : Bool
  riskScoreAtLeastReport : Bool
  deriving DecidableEq, Repr

/-- Priority-ordered gate law on the finite quotient. -/
def GateProjection.gate (q : GateProjection) : ActionGate :=
  if q.hardBoundaryViolation then .stop
  else if !q.withinContract then .stop
  else if q.unrequestedModelJudgment then .stop
  else if q.criticalDestructive && !q.currentTurnExplicitAuthorization then .checkpoint
  else if q.boundaryCrossing && !q.authorized then .checkpoint
  else if q.highScope && !q.currentTurnExplicitAuthorization then .checkpoint
  else if q.criticalUncertainty then .checkpoint
  else if q.materialChange || q.riskScoreAtLeastReport || q.boundaryCrossing then
    .proceedAndReport
  else .proceed

/-- Exact quotient map from the finite Script carrier. -/
def ActionIntent.gateProjection (a : ActionIntent) (authorized : Bool) : GateProjection :=
  { hardBoundaryViolation := a.hardBoundaryViolation
    withinContract := a.withinContract
    unrequestedModelJudgment := a.isUnrequestedModelJudgment
    criticalDestructive := a.isCriticalDestructive
    currentTurnExplicitAuthorization := a.currentTurnExplicitAuthorization
    boundaryCrossing := a.hasBoundaryCrossing
    authorized := authorized
    highScope := decide (RiskLevel.high.toNat ≤ a.scope.toNat)
    criticalUncertainty := decide (a.uncertainty = RiskLevel.critical)
    materialChange := a.materialChange
    riskScoreAtLeastReport := decide (3 ≤ a.riskScore authorized) }

/-- The existing Script factors exactly through the finite quotient. -/
theorem ActionIntent.assess_eq_gateProjection
    (a : ActionIntent) (authorized : Bool) :
    a.assess authorized = (a.gateProjection authorized).gate := by
  rfl

end Basilisk
