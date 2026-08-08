/-
Materiality.lean — finite shared-obstruction and recursive materialization shape.

This is an engineering formalization of the Basilisk verification criterion,
not a metaphysical definition of physical matter.
-/

namespace Basilisk

structure MaterialEncounter where
  observer : Nat
  frame : Nat
  worldState : Nat
  constraint : Nat
  attempted : Nat
  realized : Nat
  coupled : Bool
  deriving DecidableEq, Repr

/-- A coupled encounter is nontrivially obstructed when attempted and realized
    transitions differ. -/
def MaterialEncounter.obstructed (e : MaterialEncounter) : Bool :=
  e.coupled && decide (e.attempted ≠ e.realized)

/-- Two encounters witness a shared obstruction when distinct observers in
    distinct frames encounter the same world state and constraint, and both are
    nontrivially corrected. -/
def SharedObstruction2 (a b : MaterialEncounter) : Prop :=
  a.observer ≠ b.observer ∧
  a.frame ≠ b.frame ∧
  a.worldState = b.worldState ∧
  a.constraint = b.constraint ∧
  a.obstructed = true ∧
  b.obstructed = true

structure WorldTransition where
  beforeState : Nat
  afterState : Nat
  actorObserver : Nat
  action : Nat
  createdConstraint : Nat
  deriving DecidableEq, Repr

/-- Finite world→agent→world→observer recursion: an agent changes world state,
    and later independent observers encounter the authored constraint. -/
def RecursiveMaterialization2
    (t : WorldTransition) (a b : MaterialEncounter) : Prop :=
  t.beforeState ≠ t.afterState ∧
  a.worldState = t.afterState ∧
  b.worldState = t.afterState ∧
  a.constraint = t.createdConstraint ∧
  b.constraint = t.createdConstraint ∧
  SharedObstruction2 a b

private def wallA : MaterialEncounter :=
  { observer := 1, frame := 1, worldState := 10, constraint := 7,
    attempted := 1, realized := 0, coupled := true }

private def wallB : MaterialEncounter :=
  { observer := 2, frame := 2, worldState := 10, constraint := 7,
    attempted := 1, realized := 0, coupled := true }

private def beliefA : MaterialEncounter :=
  { observer := 1, frame := 1, worldState := 11, constraint := 8,
    attempted := 1, realized := 1, coupled := true }

private def beliefB : MaterialEncounter :=
  { observer := 2, frame := 2, worldState := 11, constraint := 8,
    attempted := 1, realized := 1, coupled := true }

private def bridgeTransition : WorldTransition :=
  { beforeState := 20, afterState := 21, actorObserver := 3, action := 4,
    createdConstraint := 9 }

private def bridgeA : MaterialEncounter :=
  { observer := 4, frame := 3, worldState := 21, constraint := 9,
    attempted := 0, realized := 2, coupled := true }

private def bridgeB : MaterialEncounter :=
  { observer := 5, frame := 4, worldState := 21, constraint := 9,
    attempted := 0, realized := 2, coupled := true }

theorem wall_shared_obstruction : SharedObstruction2 wallA wallB := by
  decide

theorem shared_belief_not_obstruction : ¬ SharedObstruction2 beliefA beliefB := by
  decide

theorem bridge_recursive_materialization :
    RecursiveMaterialization2 bridgeTransition bridgeA bridgeB := by
  decide

end Basilisk
