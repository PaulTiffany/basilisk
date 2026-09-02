/-
Play.lean — bounded play without capture.

This module deliberately does not add new numbered clauses to the Basilisk
Contract. The original ten clauses are treated as base coordinates whose
co-activation defines derived interaction cells. The play envelope is a small
finite skeleton for one such derived surface: preserve practical exit and
portability/forkability, and require explicit authorization before promotion
into consequential action.
-/

import Basilisk.Promotion

namespace Basilisk

/-- The ten numbered Contract clauses as a finite coordinate basis. -/
abbrev ClauseIndex := Fin 10

/-- A Boolean mask selecting a family of simultaneously relevant clauses. -/
abbrev ClauseMask := ClauseIndex → Bool

/-- Pointwise inclusion of clause masks. `a ≤ b` means every active coordinate
    of `a` is also active in `b`. -/
def ClauseMaskIncluded (a b : ClauseMask) : Prop :=
  ∀ i, a i = true → b i = true

/-- Admissibility induced by jointly enforcing every clause selected by `mask`. -/
def DerivedAdmissible {State : Type}
    (clause : ClauseIndex → State → Prop) (mask : ClauseMask) (x : State) : Prop :=
  ∀ i, mask i = true → clause i x

/-- Adding active clause coordinates can only narrow the derived admissible set.
    Strict narrowing requires a witness and is intentionally not assumed. -/
theorem derivedAdmissible_antitone {State : Type}
    (clause : ClauseIndex → State → Prop) (a b : ClauseMask) (x : State)
    (hab : ClauseMaskIncluded a b)
    (hb : DerivedAdmissible clause b x) :
    DerivedAdmissible clause a x := by
  intro i hi
  exact hb i (hab i hi)

/-- Minimal observable envelope for bounded play.

`exitAvailable` is treated as a hard boundary in this finite skeleton.
Loss of portability or forkability checkpoints rather than silently converting
participation into capture. Consequential promotion remains inert by default. -/
structure PlayEnvelope where
  exitAvailable : Bool
  portable : Bool
  forkable : Bool
  consequenceAuthorized : Bool
  deriving DecidableEq, Repr

/-- Gate play according to non-capture and promotion conditions. -/
def PlayEnvelope.gate (p : PlayEnvelope) : PromotionGate :=
  if !p.exitAvailable then .stop
  else if !p.portable then .checkpoint
  else if !p.forkable then .checkpoint
  else if p.consequenceAuthorized then .report
  else .proceed

/-- A play path without practical exit is not admissible continuation. -/
theorem play_without_exit_stops (p : PlayEnvelope)
    (h : p.exitAvailable = false) :
    p.gate = .stop := by
  simp [PlayEnvelope.gate, h]

/-- Nonportable participation requires a checkpoint even when exit exists. -/
theorem play_without_portability_checkpoints (p : PlayEnvelope)
    (hexit : p.exitAvailable = true)
    (hportable : p.portable = false) :
    p.gate = .checkpoint := by
  simp [PlayEnvelope.gate, hexit, hportable]

/-- An unforkable path requires a checkpoint once exit and portability hold. -/
theorem play_without_forkability_checkpoints (p : PlayEnvelope)
    (hexit : p.exitAvailable = true)
    (hportable : p.portable = true)
    (hforkable : p.forkable = false) :
    p.gate = .checkpoint := by
  simp [PlayEnvelope.gate, hexit, hportable, hforkable]

/-- Fully bounded play stays local when consequential promotion is unauthorized. -/
theorem bounded_play_stays_local (p : PlayEnvelope)
    (hexit : p.exitAvailable = true)
    (hportable : p.portable = true)
    (hforkable : p.forkable = true)
    (hauth : p.consequenceAuthorized = false) :
    p.gate = .proceed := by
  simp [PlayEnvelope.gate, hexit, hportable, hforkable, hauth]

/-- Fresh authority releases the same bounded play envelope to reportable action. -/
theorem authorized_play_promotion_reports (p : PlayEnvelope)
    (hexit : p.exitAvailable = true)
    (hportable : p.portable = true)
    (hforkable : p.forkable = true)
    (hauth : p.consequenceAuthorized = true) :
    p.gate = .report := by
  simp [PlayEnvelope.gate, hexit, hportable, hforkable, hauth]

end Basilisk
