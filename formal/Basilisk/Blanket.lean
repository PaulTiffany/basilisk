/-
Blanket.lean — the separator-property shape of a Blanket (information,
tool, and dependency boundary) over a dependency graph.

Scope note: this file states the separator *property* only — every
direct edge crossing from outside to inside must be mediated by a
boundary vertex. Path-based reachability/connectivity theorems belong
in `Reachability.lean` and are not yet connected to this file; that
connection is future work, not attempted in this pass.
-/

namespace Basilisk

/-- A finite directed dependency graph on vertex type `V`: `edges v w`
    holds when `v` may directly cause an effect visible to `w` (a tool
    call, a data flow, a private note read). -/
structure DepGraph (V : Type) where
  edges : V → V → Bool

/-- A Blanket over a dependency graph: `inside` marks what the boundary
    treats as inside the trust boundary, `boundary` marks the mediating
    vertices themselves. -/
structure Blanket (V : Type) (_G : DepGraph V) where
  inside : V → Bool
  boundary : V → Bool

/-- The separator condition: no direct edge from a strictly-outside
    vertex to a strictly-inside vertex bypasses the boundary. -/
def Blanket.isSeparator {V : Type} {G : DepGraph V} (B : Blanket V G) : Prop :=
  ∀ v w, G.edges v w → B.inside w → !B.inside v → (B.boundary v || B.boundary w)

/-- Sanity check: a graph with no edges is vacuously separated by any
    Blanket, regardless of how `inside`/`boundary` are chosen. -/
theorem Blanket.isSeparator_of_no_edges {V : Type} {G : DepGraph V}
    (B : Blanket V G) (hNoEdges : ∀ v w, G.edges v w = false) :
    B.isSeparator := by
  intro v w hEdge _ _
  rw [hNoEdges v w] at hEdge
  exact absurd hEdge (by decide)

end Basilisk
