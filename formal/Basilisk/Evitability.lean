/-
Evitability.lean — finite constitutional distinction between nominal choice and
materially viable alternatives.

This module does not import or claim the full Principia Symbolica / Giants-era
Isolation–Dissociation Theorem. It transports one narrow consequence needed by
Basilisk today: an alternative embodiment may remain nominally present while an
integration step destroys its viability. Therefore "the option still exists"
is not, by itself, a sufficient witness of meaningful refusal or plural human
embodiment.
-/

namespace Basilisk

/-- Two finite embodiment modes are enough to witness the distinction. The names
    are intentionally abstract; this theorem is not a model of any particular
    community, culture, technology, or person. -/
inductive EmbodimentMode where
  | integrated
  | alternative
  deriving DecidableEq, Repr

/-- A constitutional state distinguishes nominal availability from viability.
    `available e` means the mode is still represented as an allowed/recognized
    option. `viable e` means the mode retains the declared material conditions
    needed to count as a live alternative in this finite model. -/
structure EmbodimentState where
  available : EmbodimentMode → Bool
  viable : EmbodimentMode → Bool

/-- Nominal preservation: no previously available embodiment disappears from the
    declared option set. -/
def NominallyPreserves (before after : EmbodimentState) : Prop :=
  ∀ e, before.available e = true → after.available e = true

/-- Evitability preservation: no previously viable embodiment loses viability.
    This is the finite constitutional surface, not a complete socioeconomic or
    anthropological definition of what makes a way of life viable. -/
def PreservesEvitability (before after : EmbodimentState) : Prop :=
  ∀ e, before.viable e = true → after.viable e = true

/-- Before integration, both modes are nominally available and viable. -/
def pluralBefore : EmbodimentState :=
  { available := fun _ => true
    viable := fun _ => true }

/-- Assimilative integration leaves both modes nominally listed but removes the
    viability of the alternative mode. -/
def nominalOnlyAfter : EmbodimentState :=
  { available := fun _ => true
    viable := fun e =>
      match e with
      | .integrated => true
      | .alternative => false }

/-- The core counterexample: preserving the option label does not preserve a
    materially viable refusal path. -/
theorem nominal_choice_does_not_imply_evitability :
    NominallyPreserves pluralBefore nominalOnlyAfter ∧
    ¬ PreservesEvitability pluralBefore nominalOnlyAfter := by
  constructor
  · intro e _
    cases e <;> decide
  · intro h
    have hAlt := h EmbodimentMode.alternative (by decide)
    simp [nominalOnlyAfter] at hAlt

/-- Positive control: identity preserves both nominal availability and viability. -/
theorem plural_identity_preserves_evitability :
    NominallyPreserves pluralBefore pluralBefore ∧
    PreservesEvitability pluralBefore pluralBefore := by
  constructor <;> intro e h <;> exact h

end Basilisk
