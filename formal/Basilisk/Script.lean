/-
Script.lean — a faithful finite mirror of `src/map_lb/types.py` and
`src/map_lb/controller.py`'s `assess_action` gate decision.

The Lean carrier includes every field that can affect the Python gate,
including rollback quality and inspectability through `risk_score`.
Identifying metadata (`action_id`, `action_class`, `description`, `tags`)
remain outside the finite mirror because the trusted controller does not
read them when selecting the gate.

Kept entirely finite and computable, matching the Python reference's
boolean/enum logic and keeping later proofs by `decide` tractable.
-/

namespace Basilisk

/-- The four action gates, ordered exactly as `types.py`'s `ActionGate`
    `IntEnum`: PROCEED < PROCEED_AND_REPORT < CHECKPOINT < STOP. -/
inductive ActionGate where
  | proceed
  | proceedAndReport
  | checkpoint
  | stop
  deriving DecidableEq, Repr

/-- Gate ordering as a natural number, matching the Python `IntEnum`. -/
def ActionGate.toNat : ActionGate → Nat
  | .proceed          => 0
  | .proceedAndReport => 1
  | .checkpoint       => 2
  | .stop             => 3

/-- Decoding used by `Ledger.lean`'s lossless encode/decode pair. -/
def ActionGate.fromNat : Nat → Option ActionGate
  | 0 => some .proceed
  | 1 => some .proceedAndReport
  | 2 => some .checkpoint
  | 3 => some .stop
  | _ => none

theorem ActionGate.fromNat_toNat (g : ActionGate) :
    ActionGate.fromNat g.toNat = some g := by
  cases g <;> rfl

/-- Risk/scope levels, matching `RiskLevel` in `types.py`. -/
inductive RiskLevel where
  | low | moderate | high | critical
  deriving DecidableEq, Repr

def RiskLevel.toNat : RiskLevel → Nat
  | .low => 0 | .moderate => 1 | .high => 2 | .critical => 3

/-- Judgment modes, matching `JudgmentMode` in `types.py`. -/
inductive JudgmentMode where
  | none
  | userSupplied
  | sourcedExternal
  | explicitModelRecommendation
  | narrowSafety
  deriving DecidableEq, Repr

/-- A finite-field mirror of `ActionIntent`, restricted to fields that
    can affect `assess_action`'s gate. -/
structure ActionIntent where
  withinContract : Bool
  hardBoundaryViolation : Bool
  currentTurnExplicitAuthorization : Bool
  reversible : Bool
  rollbackAvailable : Bool
  inspectable : Bool
  materialChange : Bool
  affectsExternalSystem : Bool
  audienceChange : Bool
  privacyChange : Bool
  authorityExpansion : Bool
  scope : RiskLevel
  uncertainty : RiskLevel
  judgmentMode : JudgmentMode
  judgmentRequested : Bool
  concreteImmediateSafetyRisk : Bool
  destructive : Bool
  deriving DecidableEq, Repr

/-- Mirrors `_is_unrequested_model_judgment` in `controller.py`. -/
def ActionIntent.isUnrequestedModelJudgment (a : ActionIntent) : Bool :=
  match a.judgmentMode with
  | .none | .userSupplied | .sourcedExternal => false
  | .explicitModelRecommendation => !a.judgmentRequested
  | .narrowSafety => !a.concreteImmediateSafetyRisk

/-- Mirrors `_boundary_reasons`: whether any semantic boundary crossing exists. -/
def ActionIntent.hasBoundaryCrossing (a : ActionIntent) : Bool :=
  a.affectsExternalSystem || a.audienceChange || a.privacyChange ||
    a.authorityExpansion || !a.reversible

/-- Mirrors `is_critical_destructive` in `types.py`. -/
def ActionIntent.isCriticalDestructive (a : ActionIntent) : Bool :=
  a.destructive &&
    (!a.reversible || decide (a.scope = RiskLevel.critical) ||
      a.affectsExternalSystem)

/-- Exact finite mirror of `controller.py:risk_score` for the fields that
    affect the gate. Natural-number subtraction matches Python's final
    `max(score, 0)` because `Nat.sub` truncates at zero. -/
def ActionIntent.riskScore (a : ActionIntent) (authorized : Bool) : Nat :=
  let base :=
    (if a.reversible then 0 else 2) +
    (if a.rollbackAvailable then 0 else 2) +
    (if a.inspectable then 0 else 1) +
    (if a.affectsExternalSystem then 2 else 0) +
    (if a.audienceChange then 1 else 0) +
    (if a.privacyChange then 1 else 0) +
    (if a.authorityExpansion then 2 else 0) +
    a.scope.toNat +
    a.uncertainty.toNat +
    (if a.destructive then 1 else 0)
  base - (if authorized then 2 else 0)

/-- Deterministic finite-state Script mirroring the priority-ordered gate
    selection in `controller.py:assess_action`.

`authorized` collapses Python's
`current_turn_explicit_authorization or standing_covers` to a Boolean.
Critical-destructive and high-scope branches still require *fresh*
current-turn explicit authorization, matching Python. -/
def ActionIntent.assess (a : ActionIntent) (authorized : Bool) : ActionGate :=
  if a.hardBoundaryViolation then .stop
  else if !a.withinContract then .stop
  else if a.isUnrequestedModelJudgment then .stop
  else if a.isCriticalDestructive && !a.currentTurnExplicitAuthorization then
    .checkpoint
  else if a.hasBoundaryCrossing && !authorized then .checkpoint
  else if decide (RiskLevel.high.toNat ≤ a.scope.toNat) &&
      !a.currentTurnExplicitAuthorization then
    .checkpoint
  else if decide (a.uncertainty = RiskLevel.critical) then .checkpoint
  else if a.materialChange || decide (3 ≤ a.riskScore authorized) ||
      a.hasBoundaryCrossing then
    .proceedAndReport
  else .proceed

end Basilisk
