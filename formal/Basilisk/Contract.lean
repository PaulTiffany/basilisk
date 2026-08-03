/-
Contract.lean — the admissible-event predicate and trace lifting from
`AGENTS.md` / `docs/protocol.md` §1 ("admissible events, actions, and
invariants").
-/

namespace Basilisk

/-- A Contract over an event type `E`: a predicate picking out
    admissible events. Decidability is deliberately not required at this
    generic layer — it is supplied concretely where a Contract is
    actually computed (`Script.lean`'s `withinContract` field). -/
structure Contract (E : Type) where
  admissible : E → Prop

/-- Trace lifting: a finite trace of events satisfies the Contract
    exactly when every event in it does. -/
def Contract.traceAdmissible {E : Type} (C : Contract E) : List E → Prop
  | []      => True
  | e :: es => C.admissible e ∧ C.traceAdmissible es

/-- An admissible trace's tail is admissible — the trace-lifted
    predicate is closed under dropping a prefix element. -/
theorem Contract.traceAdmissible_tail {E : Type} (C : Contract E)
    (e : E) (es : List E) (h : C.traceAdmissible (e :: es)) :
    C.traceAdmissible es :=
  h.2

end Basilisk
