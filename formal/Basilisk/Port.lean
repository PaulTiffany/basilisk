/-
Port.lean — the typed port `p = (I_p, O_p)` from `docs/mathematical-model.md`
§1 / `README.md`'s Quartet section: `p = (I_p, O_p)`, `Ω_p = I_p × O_p`.

This is intentionally the lightest file in the core: a generic port is
just an input type and an output type. It is not yet wired into
`Script.lean`'s concrete `ActionIntent`/`ActionGate` model — that
connection (typing the reference controller's inputs/outputs as a
concrete `Port` instance) is future work, not attempted in this pass.
-/

namespace Basilisk

/-- A typed port: an input type and an output type. -/
structure Port where
  I : Type
  O : Type

/-- The event space `Ω_p = I_p × O_p` of a port. -/
def Port.Event (p : Port) : Type := p.I × p.O

end Basilisk
