/-
DependencyMutationWitness.lean — Lean instantiation of
`verification/dependency_mutation.json`.

Source SHA-256:
a53ad17351271c3e2e32e7b7baf8de4227d0d97adb57f93377fa1516acfbb6ae
-/

import Basilisk.DependencyCut

namespace Basilisk

inductive DNode where
  | x | child | coparent | other
  deriving DecidableEq, Repr

private def beforeEdges : DNode → DNode → Bool
  | .x, .child => true
  | _, _ => false

private def afterEdges : DNode → DNode → Bool
  | .x, .child => true
  | .coparent, .child => true
  | _, _ => false

private def beforeGraph : DepGraph DNode := ⟨beforeEdges⟩
private def afterGraph : DepGraph DNode := ⟨afterEdges⟩

/-- Adding the co-parent edge makes `coparent` enter the family closure of `x`.
    This is a graph-topology witness only; it is not a conditional-independence
    theorem and does not by itself imply a constitutional gate. -/
theorem dependency_mutation_adds_coparent :
    ¬ beforeGraph.inFamilyClosure DNode.x DNode.coparent ∧
    afterGraph.inFamilyClosure DNode.x DNode.coparent := by
  constructor
  · simp [DepGraph.inFamilyClosure, DepGraph.isParent,
      DepGraph.isChild, DepGraph.isCoParent, beforeGraph, beforeEdges]
  · apply DepGraph.coparent_mem_familyClosure
    unfold DepGraph.isCoParent
    refine ⟨DNode.child, ?_, ?_, ?_⟩
    · rfl
    · rfl
    · decide

end Basilisk
