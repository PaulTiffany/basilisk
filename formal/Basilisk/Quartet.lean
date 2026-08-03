/-
Quartet.lean — bundles Contract, Script, Blanket, and Ledger as four
distinct fields, per `README.md`: "these are different objects. A
ledger does not identify the hidden script; a script does not define
its own contract; a blanket is not merely a wall; a contract is not
execution." This structure makes that non-identification a type-level
fact — there is no field or coercion collapsing any two of these into
one another — rather than leaving it as prose.
-/

import Basilisk.Contract
import Basilisk.Script
import Basilisk.Blanket
import Basilisk.Ledger

namespace Basilisk

/-- A Basilisk Quartet `Q_p = (C_p, S_p, B_p, Λ_p)` for a fixed event
    type `E`, vertex type `V`, and dependency graph `G`. -/
structure Quartet (E V : Type) (G : DepGraph V) where
  contract : Contract E
  script : ActionIntent → Bool → ActionGate
  blanket : Blanket V G
  ledger : Ledger

end Basilisk
