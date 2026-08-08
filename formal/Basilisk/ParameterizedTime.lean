/-
ParameterizedTime.lean — finite bridge from parameterized process to reflective time.

This module does not claim that physical time is exhausted by parameterization.
It formalizes a narrower Principia-style statement: an observer-relative state
carries both a world state and a finite reflective history. Observer update can
therefore co-constitute an operational time coordinate by extending that history.
If admissible reverse transformations are required not to erase reflective
history, the resulting reflective step has no admissible undo at that state,
even when the underlying world dynamics may themselves be reversible.

Amortization is represented separately as a change in parameter placement whose
observable step commutes with the explicit parameterization.
-/

namespace Basilisk

structure ParameterizedProcess (X Θ : Type) where
  step : Θ → X → X

structure Reparameterization
    {X Θ Φ Y : Type}
    (explicit : ParameterizedProcess X Θ)
    (amortized : ParameterizedProcess X Φ)
    (observe : X → Y) where
  mapParameter : Θ → Φ
  commutes : ∀ θ x,
    observe (explicit.step θ x) = observe (amortized.step (mapParameter θ) x)

structure ReflectiveState (X E : Type) where
  world : X
  history : List E
  deriving Repr

def ReflectiveState.operationalTime {X E : Type} (s : ReflectiveState X E) : Nat :=
  s.history.length

def reflectiveStep
    {X Θ E : Type}
    (process : ParameterizedProcess X Θ)
    (observe : Θ → X → E)
    (θ : Θ)
    (s : ReflectiveState X E) : ReflectiveState X E :=
  { world := process.step θ s.world
    history := observe θ s.world :: s.history }

/-- One reflective observer update increments the finite operational-time
    coordinate exactly once. This is the finite Memory-Axiom witness. -/
theorem operationalTime_reflectiveStep
    {X Θ E : Type}
    (process : ParameterizedProcess X Θ)
    (observe : Θ → X → E)
    (θ : Θ)
    (s : ReflectiveState X E) :
    (reflectiveStep process observe θ s).operationalTime = s.operationalTime + 1 := by
  simp [reflectiveStep, ReflectiveState.operationalTime]

/-- Admissible reflective transformations may preserve or extend history but do
    not erase it. This is an explicit constitutional assumption, not a law of
    arbitrary physical dynamics. -/
def HistoryMonotone {X E : Type}
    (T : ReflectiveState X E → ReflectiveState X E) : Prop :=
  ∀ s, s.operationalTime ≤ (T s).operationalTime

/-- A history-monotone transformation cannot undo a reflective update at the
    same reflective state, because the update has strictly increased history. -/
theorem reflectiveStep_no_historyMonotone_undo
    {X Θ E : Type}
    (process : ParameterizedProcess X Θ)
    (observe : Θ → X → E)
    (θ : Θ)
    (s : ReflectiveState X E)
    (undo : ReflectiveState X E → ReflectiveState X E)
    (hmono : HistoryMonotone undo) :
    undo (reflectiveStep process observe θ s) ≠ s := by
  intro hundo
  have hle := hmono (reflectiveStep process observe θ s)
  rw [hundo] at hle
  have hlt : s.operationalTime < (reflectiveStep process observe θ s).operationalTime := by
    simp [operationalTime_reflectiveStep]
  exact (Nat.not_lt_of_ge hle) hlt

/-- Even granting an inverse for the underlying world-state transition does not
    remove the reflective arrow when admissible undo is history-monotone. -/
theorem reversible_world_does_not_remove_reflective_arrow
    {X Θ E : Type}
    (process : ParameterizedProcess X Θ)
    (observe : Θ → X → E)
    (θ : Θ)
    (worldUndo : X → X)
    (_hworld : ∀ x, worldUndo (process.step θ x) = x)
    (s : ReflectiveState X E)
    (undo : ReflectiveState X E → ReflectiveState X E)
    (hmono : HistoryMonotone undo) :
    undo (reflectiveStep process observe θ s) ≠ s :=
  reflectiveStep_no_historyMonotone_undo process observe θ s undo hmono

private def explicitAdd : ParameterizedProcess Nat (Nat × Nat) :=
  { step := fun θ x => x + θ.1 + θ.2 }

private def amortizedAdd : ParameterizedProcess Nat Nat :=
  { step := fun θ x => x + θ }

/-- Finite amortization witness: two explicit parameter contributions can be
    compiled into one parameter without changing the realized state update. -/
theorem amortized_parameter_compilation_fixture (a b x : Nat) :
    explicitAdd.step (a, b) x = amortizedAdd.step (a + b) x := by
  simp [explicitAdd, amortizedAdd, Nat.add_assoc]

end Basilisk
