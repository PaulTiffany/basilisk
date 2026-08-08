/-
Basilisk — the finite combinatorial core of the Basilisk Quartet
(Contract/TTDC, Script/TTIE, Blanket/TTCS, Ledger/TTPR), following
`formal/README.md`'s plan: "the probabilistic and metric versions
should follow the finite combinatorial core, rather than being
axiomatized prematurely."

Verified here (core Lean 4 + decidable/classical reasoning only, no
mathlib dependency):
  * Port.lean             — typed ports, Ω_p = I_p × O_p (not yet wired
                            into Script.lean's concrete model)
  * Contract.lean         — admissible-event predicate, trace lifting
  * Script.lean           — a faithful finite mirror of
                            `src/map_lb/controller.py`'s `assess_action`
                            gate-priority logic
  * Blanket.lean          — direct-edge separator-property shape over a
                            dependency graph; not a probability theorem
  * DependencyCut.lean    — exact finite parent/child/co-parent family
                            closure behind "parents, children, parents
                            of children"; no conditional-independence claim
  * Ledger.lean           — lossless encode/decode pair for a minimal
                            Ledger entry, and chain-linking discipline
  * Quartet.lean          — bundles the four as distinct fields
  * Counterexamples.lean  — Script/Ledger non-identifiability witness
  * Reachability.lean     — hypothesis-relative reachable-future monotonicity
  * ConstitutionalLipschitz.lean — 0-Lipschitz counterexample showing
                            geometric boundedness alone does not imply
                            preservation of a designated invariant

Not formalized (by design, this pass): a full real-valued boundary-aware
pseudometric d_A, the authority lattice (`P(π_A(z)) ≤ P_current ∨
P_standing`), Bayesian probability semantics / conditional independence,
and natural-language classification. Those remain explicit next targets.
-/

import Basilisk.Port
import Basilisk.Contract
import Basilisk.Script
import Basilisk.Blanket
import Basilisk.DependencyCut
import Basilisk.Ledger
import Basilisk.Quartet
import Basilisk.Counterexamples
import Basilisk.Reachability
import Basilisk.ConstitutionalLipschitz

namespace Basilisk

/- Axiom audit: the core should use only decidable/computational
   reasoning, propext, and Classical.choice if invoked anywhere. -/
#print axioms ActionGate.fromNat_toNat
#print axioms Contract.traceAdmissible_tail
#print axioms Blanket.isSeparator_of_no_edges
#print axioms DepGraph.familyClosure_iff
#print axioms LedgerEntry.decode_encode
#print axioms scriptHonest_ne_scriptSneaky
#print axioms ledger_does_not_identify_script
#print axioms reachable_mono
#print axioms lipschitz_alone_not_constitutional
#print axioms PreservesPredicate.comp

end Basilisk
