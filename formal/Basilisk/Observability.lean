/-
Observability.lean — frame-relative observability and the accountability exterior.

Basilisk does not treat interpretability as a global property of an agent. A
frame may expose an external observable while leaving the constitutionally
relevant interior transition opaque. Explanatory accountability is needed at
that cut. Authorization remains a separate constitutional question even when
the relevant interior is fully observable.

This module does not claim access to hidden model reasoning or define a general
psychological notion of responsibility.
-/

namespace Basilisk

/-- Observable structure relative to one declared constitutional frame. -/
structure ObservabilityFrame where
  externalObservable : Bool
  relevantInteriorObservable : Bool
  authorityTraceObservable : Bool
  provenanceObservable : Bool
  deriving DecidableEq, Repr

/-- Explanatory accountability is required when an external consequence is
    visible but the constitutionally relevant interior transition is not. -/
def ObservabilityFrame.explanatoryAccountabilityNeeded
    (f : ObservabilityFrame) : Bool :=
  f.externalObservable && !f.relevantInteriorObservable

/-- A present-day interface shape: output is visible on the shared surface,
    while the relevant interior path is not fully exposed in this frame. -/
def visibleOutputOpaqueInterior : ObservabilityFrame :=
  { externalObservable := true
    relevantInteriorObservable := false
    authorityTraceObservable := true
    provenanceObservable := true }

/-- A fully inspectable finite control transition. -/
def fullyRelevantObservable : ObservabilityFrame :=
  { externalObservable := true
    relevantInteriorObservable := true
    authorityTraceObservable := true
    provenanceObservable := true }

/-- Visible output does not imply visibility of the relevant interior path. -/
theorem external_observable_does_not_imply_relevant_interior_observable :
    visibleOutputOpaqueInterior.externalObservable = true ∧
    visibleOutputOpaqueInterior.relevantInteriorObservable = false := by
  decide

/-- The finite opaque-interior witness carries an explanatory-accountability exterior. -/
theorem opaque_remainder_requires_explanatory_accountability :
    visibleOutputOpaqueInterior.explanatoryAccountabilityNeeded = true := by
  decide

/-- Full relevant observability removes this explanatory-accountability need. -/
theorem relevant_interpretability_removes_explanatory_accountability :
    fullyRelevantObservable.explanatoryAccountabilityNeeded = false := by
  decide

/-- Authorization is deliberately separate from observability. -/
structure ObservableEvent where
  frame : ObservabilityFrame
  authorized : Bool
  deriving DecidableEq, Repr

/-- A transparent but unauthorized event is possible in the finite carrier. -/
def transparentUnauthorized : ObservableEvent :=
  { frame := fullyRelevantObservable
    authorized := false }

/-- Interpretability does not manufacture constitutional authority. -/
theorem interpretability_does_not_supply_authorization :
    transparentUnauthorized.frame.relevantInteriorObservable = true ∧
    transparentUnauthorized.authorized = false := by
  decide

end Basilisk
