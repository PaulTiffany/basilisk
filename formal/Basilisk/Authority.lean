/-
Authority.lean — formalize the standing-authority structure that Python
`StandingAuthority.covers` evaluates before the Script receives its collapsed
`authorized : Bool` input.

Expiry is represented here by the already-evaluated Boolean `expired`; parsing
wall-clock timestamps remains a Python/runtime concern. This makes the semantic
projection explicit without pretending Lean implements datetime parsing.
-/

import Basilisk.Script

namespace Basilisk

structure StandingAuthority where
  allowedActions : List String
  maxScope : RiskLevel
  allowExternalWrite : Bool
  allowAudienceChange : Bool
  allowPrivacyChange : Bool
  allowAuthorityExpansion : Bool
  active : Bool
  expired : Bool
  deriving DecidableEq, Repr

/-- Finite mirror of Python `StandingAuthority.covers` after expiry evaluation. -/
def StandingAuthority.covers
    (auth : StandingAuthority) (actionClass : String) (a : ActionIntent) : Bool :=
  auth.active &&
  !auth.expired &&
  auth.allowedActions.contains actionClass &&
  decide (a.scope.toNat ≤ auth.maxScope.toNat) &&
  (!a.affectsExternalSystem || auth.allowExternalWrite) &&
  (!a.audienceChange || auth.allowAudienceChange) &&
  (!a.privacyChange || auth.allowPrivacyChange) &&
  (!a.authorityExpansion || auth.allowAuthorityExpansion)

/-- Exact Boolean consumed by the lower-level finite Script. -/
def ActionIntent.authorizedBy
    (a : ActionIntent) (actionClass : String) (auth : Option StandingAuthority) : Bool :=
  a.currentTurnExplicitAuthorization ||
    match auth with
    | none => false
    | some standing => standing.covers actionClass a

/-- Authority-aware entry point preserving the existing finite Script as the
    post-projection gate function. -/
def ActionIntent.assessWithStanding
    (a : ActionIntent) (actionClass : String) (auth : Option StandingAuthority) : ActionGate :=
  a.assess (a.authorizedBy actionClass auth)

theorem StandingAuthority.inactive_never_covers
    (auth : StandingAuthority) (actionClass : String) (a : ActionIntent)
    (h : auth.active = false) :
    auth.covers actionClass a = false := by
  simp [StandingAuthority.covers, h]

theorem StandingAuthority.expired_never_covers
    (auth : StandingAuthority) (actionClass : String) (a : ActionIntent)
    (h : auth.expired = true) :
    auth.covers actionClass a = false := by
  simp [StandingAuthority.covers, h]

theorem StandingAuthority.external_effect_requires_permission
    (auth : StandingAuthority) (actionClass : String) (a : ActionIntent)
    (hEffect : a.affectsExternalSystem = true)
    (hPermission : auth.allowExternalWrite = false) :
    auth.covers actionClass a = false := by
  simp [StandingAuthority.covers, hEffect, hPermission]

theorem ActionIntent.current_authorization_dominates_projection
    (a : ActionIntent) (actionClass : String) (auth : Option StandingAuthority)
    (h : a.currentTurnExplicitAuthorization = true) :
    a.authorizedBy actionClass auth = true := by
  simp [ActionIntent.authorizedBy, h]

/-- The old Boolean Script is now explicitly a projection of structured authority. -/
theorem ActionIntent.assessWithStanding_eq_assess_projection
    (a : ActionIntent) (actionClass : String) (auth : Option StandingAuthority) :
    a.assessWithStanding actionClass auth = a.assess (a.authorizedBy actionClass auth) := by
  rfl

private def highExternalIntent : ActionIntent :=
  { withinContract := true
    hardBoundaryViolation := false
    currentTurnExplicitAuthorization := false
    reversible := true
    rollbackAvailable := true
    inspectable := true
    materialChange := false
    affectsExternalSystem := true
    audienceChange := false
    privacyChange := false
    authorityExpansion := false
    scope := .high
    uncertainty := .low
    judgmentMode := .none
    judgmentRequested := false
    concreteImmediateSafetyRisk := false
    destructive := false }

private def broadStanding : StandingAuthority :=
  { allowedActions := ["deploy"]
    maxScope := .critical
    allowExternalWrite := true
    allowAudienceChange := true
    allowPrivacyChange := true
    allowAuthorityExpansion := true
    active := true
    expired := false }

/-- Standing authority can satisfy ordinary boundary coverage but cannot satisfy
    the separate fresh-current-turn requirement for high-consequence scope. -/
theorem standing_authority_does_not_replace_fresh_high_scope_authorization :
    broadStanding.covers "deploy" highExternalIntent = true ∧
    highExternalIntent.assessWithStanding "deploy" (some broadStanding) = .checkpoint := by
  decide

end Basilisk
