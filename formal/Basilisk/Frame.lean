/-
Frame.lean — the constitutional center of the finite Basilisk model.

The Contract is not reduced to generic access control.  A framed state
records who currently holds which scope, which ordinary actions that
constitution permits, and who may explicitly replace the constitution.

The motion law is kept separate from the constitution.  This is the
precise sense in which the connection is kinematic: states and actions
may correspond while holder relations and reframing authority do not
silently travel with them.
-/

namespace Basilisk

/-- A purely kinematic system: states, actions, and their motion law. -/
structure KinematicSystem (State Action : Type) where
  step : Action → State → State

/-- A kinematic correspondence preserves the declared motion law.
    It contains no holder map and conveys no constitutional authority. -/
structure KinematicCorrespondence
    {State₁ Action₁ State₂ Action₂ : Type}
    (K₁ : KinematicSystem State₁ Action₁)
    (K₂ : KinematicSystem State₂ Action₂) where
  stateMap : State₁ → State₂
  actionMap : Action₁ → Action₂
  commutes : ∀ action state,
    stateMap (K₁.step action state) =
      K₂.step (actionMap action) (stateMap state)

/-- The constitutional frame over a kinematic application.

`holds actor scope` says who currently holds a region of the frame.
`permits actor scope action` gives ordinary action jurisdiction.
`mayReframe actor scope` is separate authority to replace the frame
itself.  In particular, permission to move inside a frame does not imply
permission to redefine it. -/
structure Constitution (Actor Scope Action : Type) where
  holds : Actor → Scope → Prop
  permits : Actor → Scope → Action → Prop
  mayReframe : Actor → Scope → Prop

/-- A world-state paired with its current constitution. -/
structure FramedState (Actor Scope State Action : Type) where
  constitution : Constitution Actor Scope Action
  world : State

/-- Events distinguish motion inside a frame from replacement of the
    frame.  A Script cannot smuggle reframing into an ordinary action. -/
inductive FramedEvent (Actor Scope Action : Type) where
  | act (actor : Actor) (scope : Scope) (action : Action)
  | reframe
      (actor : Actor)
      (scope : Scope)
      (next : Constitution Actor Scope Action)

/-- Admissibility is evaluated against the current constitution.
    Ordinary action requires both scoped holding and action permission.
    Reframing requires scoped holding and explicit reframing authority. -/
def FramedEvent.admissible
    {Actor Scope State Action : Type}
    (s : FramedState Actor Scope State Action) :
    FramedEvent Actor Scope Action → Prop
  | .act actor scope action =>
      s.constitution.holds actor scope ∧
        s.constitution.permits actor scope action
  | .reframe actor scope _ =>
      s.constitution.holds actor scope ∧
        s.constitution.mayReframe actor scope

/-- The transition law.  Ordinary kinematic motion changes only the
    world.  Only an explicit `reframe` event can replace the constitution. -/
def FramedState.transition
    {Actor Scope State Action : Type}
    (K : KinematicSystem State Action)
    (s : FramedState Actor Scope State Action) :
    FramedEvent Actor Scope Action →
      FramedState Actor Scope State Action
  | .act _ _ action =>
      { constitution := s.constitution
        world := K.step action s.world }
  | .reframe _ _ next =>
      { constitution := next
        world := s.world }

/-- Ordinary action preserves the constitution definitionally. -/
theorem FramedState.action_preserves_constitution
    {Actor Scope State Action : Type}
    (K : KinematicSystem State Action)
    (s : FramedState Actor Scope State Action)
    (actor : Actor) (scope : Scope) (action : Action) :
    (s.transition K (.act actor scope action)).constitution =
      s.constitution := by
  rfl

/-- No silent reframing: if the constitution changed, the event was
    explicitly a `reframe` event rather than ordinary kinematic motion. -/
theorem FramedState.no_silent_reframing
    {Actor Scope State Action : Type}
    (K : KinematicSystem State Action)
    (s : FramedState Actor Scope State Action)
    (event : FramedEvent Actor Scope Action)
    (hchanged :
      (s.transition K event).constitution ≠ s.constitution) :
    ∃ actor scope next,
      event = FramedEvent.reframe actor scope next := by
  cases event with
  | act actor scope action =>
      simp [FramedState.transition] at hchanged
  | reframe actor scope next =>
      exact ⟨actor, scope, next, rfl⟩

/-- Authorized reframing: for an admissible transition, any actual
    constitution change has a current scoped holder who was separately
    authorized to reframe. -/
theorem FramedState.changed_constitution_has_authorized_holder
    {Actor Scope State Action : Type}
    (K : KinematicSystem State Action)
    (s : FramedState Actor Scope State Action)
    (event : FramedEvent Actor Scope Action)
    (hadmissible : event.admissible s)
    (hchanged :
      (s.transition K event).constitution ≠ s.constitution) :
    ∃ actor scope next,
      event = FramedEvent.reframe actor scope next ∧
      s.constitution.holds actor scope ∧
      s.constitution.mayReframe actor scope := by
  cases event with
  | act actor scope action =>
      simp [FramedState.transition] at hchanged
  | reframe actor scope next =>
      exact ⟨actor, scope, next, rfl, hadmissible.1, hadmissible.2⟩

/-- Identity motion is always a kinematic correspondence.  Notice that
    this theorem mentions no Constitution: equal motion does not identify
    or transport the holder relation. -/
def KinematicSystem.identityCorrespondence
    {State Action : Type}
    (K : KinematicSystem State Action) :
    KinematicCorrespondence K K where
  stateMap := id
  actionMap := id
  commutes := by
    intro action state
    rfl

end Basilisk
