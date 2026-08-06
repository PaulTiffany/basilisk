/-
Basilisk — the finite combinatorial core of the Basilisk Quartet
(Contract/TTDC, Script/TTIE, Blanket/TTCS, Ledger/TTPR), following
`formal/README.md`'s plan: "the probabilistic and metric versions
should follow the finite combinatorial core, rather than being
axiomatized prematurely."

Verified here (core Lean 4 + decidable/classical reasoning only, no
mathlib dependency):
  * Port.lean           — typed ports, Ω_p = I_p × O_p (not yet wired
                          into Script.lean's concrete model)
  * Contract.lean       — admissible-event predicate, trace lifting
  * Frame.lean          — kinematic systems, scoped holder relations,
                          explicit reframing, and no-silent-reframing
  * Script.lean         — a faithful finite mirror of
                          `src/map_lb/controller.py`'s `assess_action`
                          gate-priority logic
  * Blanket.lean        — the separator-property shape of a Blanket
                          over a dependency graph (not yet connected to
                          Reachability.lean)
  * Ledger.lean         — a lossless encode/decode pair for a minimal
                          Ledger entry, and the chain-linking discipline
                          (the SHA-256 hash itself is not modeled)
  * Quartet.lean        — bundles the four as distinct fields, making
                          "these are different objects" a type-level
                          fact rather than prose
  * Counterexamples.lean — Script/Ledger non-identifiability: two
                          genuinely different Scripts that agree on the
                          observed trace, the Lean witness for
                          `finite_quartet.py`'s Python demo
  * Reachability.lean    — the shape of reachable-future monotonicity
                          from `PROVENANCE.md`; strict inclusion (the
                          substantive claim) is explicitly left open

Not formalized (by design, this pass): the boundary-aware Lipschitz
metric d_A itself, the full authority lattice (`P(π(z)) ≤ P_current ∨
P_standing`), legitimacy of a holder assignment, and anything about
natural-language classification. Those remain later targets.
-/

import Basilisk.Port
import Basilisk.Contract
import Basilisk.Frame
import Basilisk.Script
import Basilisk.Blanket
import Basilisk.Ledger
import Basilisk.Quartet
import Basilisk.Counterexamples
import Basilisk.Reachability

namespace Basilisk

/- Axiom audit: the core should use only decidable/computational
   reasoning, propext, and Classical.choice if invoked anywhere. -/
#print axioms ActionGate.fromNat_toNat
#print axioms Contract.traceAdmissible_tail
#print axioms FramedState.action_preserves_constitution
#print axioms FramedState.no_silent_reframing
#print axioms FramedState.changed_constitution_has_authorized_holder
#print axioms Blanket.isSeparator_of_no_edges
#print axioms LedgerEntry.decode_encode
#print axioms scriptHonest_ne_scriptSneaky
#print axioms ledger_does_not_identify_script
#print axioms reachable_mono

end Basilisk
