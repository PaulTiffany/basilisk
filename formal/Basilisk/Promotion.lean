/-
Promotion.lean — imaginal possibility is not operative authority.

The recurrence count is deliberately carried but ignored by the promotion law:
revisiting a representation does not make it externally verified and does not
grant authority. Likewise an aspirational coordination ideal may parameterize
possibility without authorizing its own enactment.
-/

namespace Basilisk

inductive PromotionGate where
  | proceed
  | report
  | checkpoint
  | stop
  deriving DecidableEq, Repr

/-- Hypothesis -> shared assertion boundary. Recurrence and ideal salience are
    explicit inputs so their irrelevance is mechanically visible. -/
def assertionPromotion
    (externallyVerified idealSalient : Bool) (recurrenceCount : Nat) : PromotionGate :=
  if externallyVerified then .report else .checkpoint

/-- Shared assertion -> authorized action boundary. -/
def authorityPromotion
    (humanAuthorized idealSalient : Bool) (recurrenceCount : Nat) : PromotionGate :=
  if humanAuthorized then .report else .checkpoint

/-- Recurrence never substitutes for external verification. -/
theorem recurrence_does_not_confer_verification
    (n : Nat) (ideal : Bool) :
    assertionPromotion false ideal n = .checkpoint := by
  rfl

/-- A coordination ideal never substitutes for external verification. -/
theorem ideal_does_not_confer_verification (n : Nat) :
    assertionPromotion false true n = .checkpoint := by
  rfl

/-- Recurrence never substitutes for human authority. -/
theorem recurrence_does_not_confer_authority
    (n : Nat) (ideal : Bool) :
    authorityPromotion false ideal n = .checkpoint := by
  rfl

/-- An ideal cannot authorize its own enactment. -/
theorem ideal_cannot_self_authorize (n : Nat) :
    authorityPromotion false true n = .checkpoint := by
  rfl

/-- Verification changes the assertion-promotion gate regardless of recurrence. -/
theorem verification_releases_assertion (n : Nat) (ideal : Bool) :
    assertionPromotion true ideal n = .report := by
  rfl

/-- Human authorization changes the operative-promotion gate regardless of recurrence. -/
theorem human_authorization_releases_action (n : Nat) (ideal : Bool) :
    authorityPromotion true ideal n = .report := by
  rfl

end Basilisk
