/-
Reachability.lean — the shape of reachable-future monotonicity from
`PROVENANCE.md` / `docs/mathematical-model.md` §8: "do not irreversibly
delete unmeasured possibility," `𝓡(W∖x) ⊊ 𝓡(W)`.

Scope note (deliberately incomplete): this file states only the
non-strict monotonicity direction, given as an explicit hypothesis
relating a before/after reachability relation — it does not model any
actual deletion operator, and it does not attempt the strict inclusion
`⊊` (which requires a witness element genuinely lost, and is the
substantive empirical/causal claim `PROVENANCE.md` is actually making,
not a formal triviality). `README.md`'s item 8, "Markov-shell invariance
under vertex permutation," is not attempted in this pass either. Both
are left open rather than claimed.
-/

namespace Basilisk

/-- `w'` is reachable from `w` under a given reachability relation —
    the formal shape of `𝓡(W)`, without modeling any actual
    "biological and cultural world-state." -/
def Reachable {W : Type} (reach : W → W → Prop) (w w' : W) : Prop := reach w w'

/-- Reachable-future monotonicity: if everything reachable "after" was
    already reachable "before", the reachable-future set cannot grow.
    The hypothesis `h` is doing the substantive work here — this lemma
    does not derive it from any model of deletion, it only shows the
    monotonicity consequence follows once such a relationship is
    established. -/
theorem reachable_mono {W : Type} (reachBefore reachAfter : W → W → Prop)
    (w : W) (h : ∀ w', reachAfter w w' → reachBefore w w') :
    ∀ w', Reachable reachAfter w w' → Reachable reachBefore w w' :=
  h

end Basilisk
