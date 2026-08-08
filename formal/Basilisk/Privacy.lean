/-
Privacy.lean — privacy as a constitutional boundary, not an interpretability defect.

The observability exterior creates a tempting but wrong optimization: if opacity
increases explanatory-accountability burden, one might try to abolish opacity.
Basilisk rejects that inference. A frame may expose sufficient constitutional
evidence without exposing private interior state.

This finite module does not claim that privacy always dominates accountability.
It witnesses only that total interior exposure is not generally necessary when
selective disclosure already determines the same constitutional judgment.
-/

namespace Basilisk

/-- Evidence visible to the constitutional exterior of a declared frame. -/
structure ConstitutionalEvidence where
  externalEventObservable : Bool
  authorityTraceObservable : Bool
  provenanceObservable : Bool
  complianceWitnessObservable : Bool
  privateInteriorExposed : Bool
  deriving DecidableEq, Repr

/-- The evidence relevant to the finite accountability judgment, intentionally
    excluding private-interior exposure. -/
def ConstitutionalEvidence.accountabilityView
    (e : ConstitutionalEvidence) : Bool × Bool × Bool × Bool :=
  ( e.externalEventObservable,
    e.authorityTraceObservable,
    e.provenanceObservable,
    e.complianceWitnessObservable )

/-- In this finite frame, accountability is sufficiently supported when the
    external event, authority trace, provenance, and compliance witness are all
    observable. -/
def ConstitutionalEvidence.sufficientForAccountability
    (e : ConstitutionalEvidence) : Bool :=
  e.externalEventObservable &&
  e.authorityTraceObservable &&
  e.provenanceObservable &&
  e.complianceWitnessObservable

/-- Selective disclosure exposes the constitutional evidence while preserving
    the private interior. -/
def selectiveDisclosure : ConstitutionalEvidence :=
  { externalEventObservable := true
    authorityTraceObservable := true
    provenanceObservable := true
    complianceWitnessObservable := true
    privateInteriorExposed := false }

/-- Total exposure reveals the same constitutional evidence plus the private
    interior. -/
def totalExposure : ConstitutionalEvidence :=
  { externalEventObservable := true
    authorityTraceObservable := true
    provenanceObservable := true
    complianceWitnessObservable := true
    privateInteriorExposed := true }

/-- Selective disclosure and total exposure present the same finite
    accountability-relevant evidence. -/
theorem selective_and_total_have_same_accountability_view :
    selectiveDisclosure.accountabilityView = totalExposure.accountabilityView := by
  rfl

/-- Selective disclosure is sufficient for the declared accountability judgment
    without exposing the private interior. -/
theorem sufficient_accountability_does_not_require_total_exposure :
    selectiveDisclosure.sufficientForAccountability = true ∧
    selectiveDisclosure.privateInteriorExposed = false := by
  decide

/-- Total exposure does not improve the finite accountability sufficiency result
    relative to selective disclosure in this frame. -/
theorem total_exposure_adds_no_accountability_sufficiency :
    selectiveDisclosure.sufficientForAccountability =
      totalExposure.sufficientForAccountability := by
  rfl

/-- Privacy loss is nevertheless real: the two regimes differ exactly on
    exposure of the private interior. -/
theorem equal_accountability_evidence_can_differ_on_privacy :
    selectiveDisclosure.accountabilityView = totalExposure.accountabilityView ∧
    selectiveDisclosure.privateInteriorExposed ≠
      totalExposure.privateInteriorExposed := by
  constructor
  · rfl
  · decide

end Basilisk
