/-
WitnessAlgebra.lean — a tiny generic kernel for cross-representation witnesses.

Interpretability here is not identified with one representation. We distinguish:
  * representations/carriers;
  * transports between them;
  * declared loss class of a transport;
  * commuting observations across different paths.

The loss classes reuse the CertifiedTransport vocabulary developed in the
broader Principia work: exact, quotient, projective, interpretive.
-/

namespace Basilisk

/-- Information-loss class of a representation transport.

`exact` means the transport is intended to preserve all distinctions in scope.
The other constructors make increasingly explicit that some distinctions are
collapsed, selected, or semantically reconstructed. These labels are metadata;
their substantive adequacy still requires witness-specific checks. -/
inductive LossClass where
  | exact
  | quotient
  | projective
  | interpretive
  deriving DecidableEq, Repr

/-- A typed transport from representation `A` to representation `B`, carrying
    an explicit loss classification rather than pretending every translation
    is information-preserving. -/
structure WitnessTransport (A B : Type) where
  map : A → B
  loss : LossClass

/-- Two paths from `A` to a common observable `D` commute when they agree for
    every source value. This is the generic mathematical shape behind a
    cross-witness agreement check. -/
def CommutesSquare
    {A B C D : Type}
    (top : A → B)
    (left : A → C)
    (right : B → D)
    (bottom : C → D) : Prop :=
  ∀ a, right (top a) = bottom (left a)

/-- The identity square always commutes. -/
theorem CommutesSquare.identity
    {A B : Type}
    (f : A → B) :
    CommutesSquare f f id id := by
  intro a
  rfl

/-- If a square commutes, applying the same observable map to both outputs
    preserves commutation. This supports refinement from a rich shared result
    to a smaller observable without inventing a new agreement proof. -/
theorem CommutesSquare.postcompose
    {A B C D E : Type}
    (top : A → B)
    (left : A → C)
    (right : B → D)
    (bottom : C → D)
    (observe : D → E)
    (h : CommutesSquare top left right bottom) :
    CommutesSquare top left (fun b => observe (right b))
      (fun c => observe (bottom c)) := by
  intro a
  exact congrArg observe (h a)

/-- Exactness is not inferred from commutation. Two lossy transports may still
    agree on a chosen observable. This constructor packages the two facts as
    separate fields so callers cannot silently identify them. -/
structure WitnessAgreement
    {A B C D : Type}
    (top : WitnessTransport A B)
    (left : WitnessTransport A C)
    (right : B → D)
    (bottom : C → D) where
  commutes : CommutesSquare top.map left.map right bottom

end Basilisk
