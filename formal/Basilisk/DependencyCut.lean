/-
DependencyCut.lean — finite graph-theoretic family closure behind the
"parents, children, parents of children" mnemonic.

This file deliberately proves only graph-structural membership facts.
It does NOT claim conditional independence: that requires probability
semantics plus an appropriate graph-Markov assumption.
-/

import Basilisk.Blanket

namespace Basilisk

/-- `v` is a parent of `x` when there is a directed edge `v → x`. -/
def DepGraph.isParent {V : Type} (G : DepGraph V) (x v : V) : Prop :=
  G.edges v x = true

/-- `v` is a child of `x` when there is a directed edge `x → v`. -/
def DepGraph.isChild {V : Type} (G : DepGraph V) (x v : V) : Prop :=
  G.edges x v = true

/-- `v` is a co-parent of `x` when some child `c` has both `x` and `v`
    as parents. We exclude `v = x` so the closure does not count the
    distinguished node as its own co-parent. -/
def DepGraph.isCoParent {V : Type} (G : DepGraph V) (x v : V) : Prop :=
  ∃ c, G.edges x c = true ∧ G.edges v c = true ∧ v ≠ x

/-- The finite graph-theoretic family closure of `x`:
    parents ∪ children ∪ co-parents ("parents of children"). -/
def DepGraph.inFamilyClosure {V : Type} (G : DepGraph V) (x v : V) : Prop :=
  G.isParent x v ∨ G.isChild x v ∨ G.isCoParent x v

/-- Every parent belongs to the family closure. -/
theorem DepGraph.parent_mem_familyClosure
    {V : Type} (G : DepGraph V) (x v : V)
    (h : G.isParent x v) :
    G.inFamilyClosure x v := by
  exact Or.inl h

/-- Every child belongs to the family closure. -/
theorem DepGraph.child_mem_familyClosure
    {V : Type} (G : DepGraph V) (x v : V)
    (h : G.isChild x v) :
    G.inFamilyClosure x v := by
  exact Or.inr (Or.inl h)

/-- Every co-parent (parent of a child) belongs to the family closure. -/
theorem DepGraph.coparent_mem_familyClosure
    {V : Type} (G : DepGraph V) (x v : V)
    (h : G.isCoParent x v) :
    G.inFamilyClosure x v := by
  exact Or.inr (Or.inr h)

/-- The family closure contains exactly the three declared dependency
    roles; this is a definitional decomposition, not a probability theorem. -/
theorem DepGraph.familyClosure_iff
    {V : Type} (G : DepGraph V) (x v : V) :
    G.inFamilyClosure x v ↔
      G.isParent x v ∨ G.isChild x v ∨ G.isCoParent x v := by
  rfl

end Basilisk
