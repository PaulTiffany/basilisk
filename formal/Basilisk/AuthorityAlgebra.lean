/-
AuthorityAlgebra.lean — separate permission breadth from authorization freshness.

A standing permission profile forms a pointwise preorder with a join that can
only broaden permission. Separately, the controller's authority basis has the
freshness order none < standing < current. These are deliberately not collapsed
into one structure: current-turn authorization is stronger evidence of present
human authorization, while standing authority carries typed permission scope.
-/

import Basilisk.Authority

namespace Basilisk

/-- Maximum finite risk/scope level. -/
def RiskLevel.max (a b : RiskLevel) : RiskLevel :=
  if decide (a.toNat ≤ b.toNat) then b else a

theorem RiskLevel.le_max_left (a b : RiskLevel) :
    a.toNat ≤ (RiskLevel.max a b).toNat := by
  cases a <;> cases b <;> decide

theorem RiskLevel.le_max_right (a b : RiskLevel) :
    b.toNat ≤ (RiskLevel.max a b).toNat := by
  cases a <;> cases b <;> decide

/-- Permission breadth, independent of active/expiry state and provenance. -/
structure PermissionProfile where
  actionAllowed : String → Bool
  maxScope : RiskLevel
  allowExternalWrite : Bool
  allowAudienceChange : Bool
  allowPrivacyChange : Bool
  allowAuthorityExpansion : Bool

/-- `a ≤ b` means every permission represented by `a` is also represented by `b`. -/
def PermissionProfile.LE (a b : PermissionProfile) : Prop :=
  (∀ action, a.actionAllowed action = true → b.actionAllowed action = true) ∧
  a.maxScope.toNat ≤ b.maxScope.toNat ∧
  (a.allowExternalWrite = true → b.allowExternalWrite = true) ∧
  (a.allowAudienceChange = true → b.allowAudienceChange = true) ∧
  (a.allowPrivacyChange = true → b.allowPrivacyChange = true) ∧
  (a.allowAuthorityExpansion = true → b.allowAuthorityExpansion = true)

/-- Join broadens either input, without inventing any permission dimension other
    than those explicitly present in one of the inputs. -/
def PermissionProfile.join (a b : PermissionProfile) : PermissionProfile :=
  { actionAllowed := fun action => a.actionAllowed action || b.actionAllowed action
    maxScope := RiskLevel.max a.maxScope b.maxScope
    allowExternalWrite := a.allowExternalWrite || b.allowExternalWrite
    allowAudienceChange := a.allowAudienceChange || b.allowAudienceChange
    allowPrivacyChange := a.allowPrivacyChange || b.allowPrivacyChange
    allowAuthorityExpansion := a.allowAuthorityExpansion || b.allowAuthorityExpansion }

theorem PermissionProfile.le_join_left (a b : PermissionProfile) :
    PermissionProfile.LE a (a.join b) := by
  constructor
  · intro action h
    simp [PermissionProfile.join, h]
  constructor
  · exact RiskLevel.le_max_left a.maxScope b.maxScope
  constructor
  · intro h; simp [PermissionProfile.join, h]
  constructor
  · intro h; simp [PermissionProfile.join, h]
  constructor
  · intro h; simp [PermissionProfile.join, h]
  · intro h; simp [PermissionProfile.join, h]

theorem PermissionProfile.le_join_right (a b : PermissionProfile) :
    PermissionProfile.LE b (a.join b) := by
  constructor
  · intro action h
    simp [PermissionProfile.join, h]
  constructor
  · exact RiskLevel.le_max_right a.maxScope b.maxScope
  constructor
  · intro h; simp [PermissionProfile.join, h]
  constructor
  · intro h; simp [PermissionProfile.join, h]
  constructor
  · intro h; simp [PermissionProfile.join, h]
  · intro h; simp [PermissionProfile.join, h]

/-- Prop-level coverage predicate for permission-monotonicity reasoning. -/
def PermissionProfile.Covers
    (p : PermissionProfile) (actionClass : String) (a : ActionIntent) : Prop :=
  p.actionAllowed actionClass = true ∧
  a.scope.toNat ≤ p.maxScope.toNat ∧
  (a.affectsExternalSystem = true → p.allowExternalWrite = true) ∧
  (a.audienceChange = true → p.allowAudienceChange = true) ∧
  (a.privacyChange = true → p.allowPrivacyChange = true) ∧
  (a.authorityExpansion = true → p.allowAuthorityExpansion = true)

/-- Broadening a permission profile cannot revoke an already-covered intent. -/
theorem PermissionProfile.covers_mono
    {p q : PermissionProfile} {actionClass : String} {a : ActionIntent}
    (hLE : PermissionProfile.LE p q)
    (hCovers : p.Covers actionClass a) :
    q.Covers actionClass a := by
  rcases hLE with ⟨hAction, hScope, hExternal, hAudience, hPrivacy, hExpansion⟩
  rcases hCovers with ⟨hActionP, hScopeP, hExternalP, hAudienceP, hPrivacyP, hExpansionP⟩
  constructor
  · exact hAction actionClass hActionP
  constructor
  · exact Nat.le_trans hScopeP hScope
  constructor
  · intro h; exact hExternal (hExternalP h)
  constructor
  · intro h; exact hAudience (hAudienceP h)
  constructor
  · intro h; exact hPrivacy (hPrivacyP h)
  · intro h; exact hExpansion (hExpansionP h)

theorem PermissionProfile.join_preserves_left_coverage
    (p q : PermissionProfile) (actionClass : String) (a : ActionIntent)
    (h : p.Covers actionClass a) :
    (p.join q).Covers actionClass a :=
  PermissionProfile.covers_mono (PermissionProfile.le_join_left p q) h

theorem PermissionProfile.join_preserves_right_coverage
    (p q : PermissionProfile) (actionClass : String) (a : ActionIntent)
    (h : q.Covers actionClass a) :
    (p.join q).Covers actionClass a :=
  PermissionProfile.covers_mono (PermissionProfile.le_join_right p q) h

/-- Evidence freshness used by the controller after permission coverage. -/
inductive AuthorityBasis where
  | none
  | standing
  | current
  deriving DecidableEq, Repr

def AuthorityBasis.toNat : AuthorityBasis → Nat
  | .none => 0
  | .standing => 1
  | .current => 2

def AuthorityBasis.join (a b : AuthorityBasis) : AuthorityBasis :=
  if decide (a.toNat ≤ b.toNat) then b else a

theorem AuthorityBasis.join_comm (a b : AuthorityBasis) :
    AuthorityBasis.join a b = AuthorityBasis.join b a := by
  cases a <;> cases b <;> decide

theorem AuthorityBasis.join_assoc (a b c : AuthorityBasis) :
    AuthorityBasis.join (AuthorityBasis.join a b) c =
      AuthorityBasis.join a (AuthorityBasis.join b c) := by
  cases a <;> cases b <;> cases c <;> decide

theorem AuthorityBasis.join_idem (a : AuthorityBasis) :
    AuthorityBasis.join a a = a := by
  cases a <;> decide

theorem AuthorityBasis.standing_join_current :
    AuthorityBasis.join .standing .current = .current := by
  decide

theorem AuthorityBasis.none_join_standing :
    AuthorityBasis.join .none .standing = .standing := by
  decide

end Basilisk
