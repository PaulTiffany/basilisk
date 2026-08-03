/-
Script.lean — a faithful finite mirror of `src/map_lb/types.py` and
`src/map_lb/controller.py`'s `assess_action`. This is the executable
policy/transducer half of the Quartet (Script/TTIE); it is deliberately
restricted to the decision-relevant fields (`action_id`, `description`,
`tags` are identifying metadata in the Python model, not decision
inputs, and are omitted here).

Kept entirely `Bool`-valued and computable (no `Prop`/`Decidable`
machinery beyond `decide`), matching the Python reference's plain
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

/-- Gate ordering as a natural number, matching the Python `IntEnum`
    values used by the gate-distance term of the Lipschitz metric. -/
def ActionGate.toNat : ActionGate → Nat
  | .proceed          => 0
  | .proceedAndReport => 1
  | .checkpoint       => 2
  | .stop             => 3

/-- Decoding used by `Ledger.lean`'s lossless encode/decode pair. Named
    `fromNat`, not `ofNat` — Lean 4 already auto-declares
    `ActionGate.ofNat` (the `OfNat`-derived numeral-literal support for
    this inductive type), so `ofNat` is a reserved name here. -/
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

/-- A finite-field mirror of `ActionIntent` (`types.py`), restricted to
    the fields `assess_action` (`controller.py`) actually reads. -/
structure ActionIntent where
  withinContract : Bool
  hardBoundaryViolation : Bool
  currentTurnExplicitAuthorization : Bool
  reversible : Bool
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

/-- Mirrors `_boundary_reasons` in `controller.py`: whether any semantic
    boundary crossing is present. -/
def ActionIntent.hasBoundaryCrossing (a : ActionIntent) : Bool :=
  a.affectsExternalSystem || a.audienceChange || a.privacyChange ||
    a.authorityExpansion || !a.reversible

/-- Mirrors `is_critical_destructive` in `types.py`. -/
def ActionIntent.isCriticalDestructive (a : ActionIntent) : Bool :=
  a.destructive &&
    (!a.reversible || decide (a.scope = RiskLevel.critical) ||
      a.affectsExternalSystem)

/-- The deterministic finite-state Script: the same priority-ordered
    hard-predicate decision as `assess_action` in `controller.py`,
    stripped of the reasons/risk-score audit payload (that is Ledger
    material, not gate-decision logic). `authorized` collapses the
    Python code's `current_turn_explicit_authorization or
    standing_covers` boolean; the standing-authority lattice itself is
    out of scope for this pass (see `formal/README.md`). -/
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
  else if a.materialChange || a.hasBoundaryCrossing then .proceedAndReport
  else .proceed

end Basilisk
