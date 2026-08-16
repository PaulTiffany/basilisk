/-
JunctionTopology.lean — finite three-way interaction signatures.

"Trefoil-like" is deliberately an engineering name, not a theorem of knot
theory. On a Bool^3 cube of ActionGate observations we call a junction
TrefoilLike when all three pair planes have a nonzero discrete second
difference somewhere and the third-order finite difference is nonzero.

The file also gives an unknot-like control (no pair links, zero third order)
and a detached-strand control (exactly one pair linked, zero third order).
-/

import Basilisk.Script

namespace Basilisk

/-- Gate ordinal used by the executable junction checker. -/
def ActionGate.ordinal (g : ActionGate) : Int := Int.ofNat g.toNat

/-- Second difference in the AB plane at fixed C. -/
def secondDiffAB (f : Bool → Bool → Bool → ActionGate) (c : Bool) : Int :=
  (f true true c).ordinal - (f true false c).ordinal -
    (f false true c).ordinal + (f false false c).ordinal

/-- Second difference in the BC plane at fixed A. -/
def secondDiffBC (f : Bool → Bool → Bool → ActionGate) (a : Bool) : Int :=
  (f a true true).ordinal - (f a true false).ordinal -
    (f a false true).ordinal + (f a false false).ordinal

/-- Second difference in the CA plane at fixed B. -/
def secondDiffCA (f : Bool → Bool → Bool → ActionGate) (b : Bool) : Int :=
  (f true b true).ordinal - (f false b true).ordinal -
    (f true b false).ordinal + (f false b false).ordinal

/-- Third-order discrete interaction residual on the full cube. -/
def thirdOrderResidual (f : Bool → Bool → Bool → ActionGate) : Int :=
  (f true true true).ordinal
  - (f true true false).ordinal
  - (f true false true).ordinal
  - (f false true true).ordinal
  + (f true false false).ordinal
  + (f false true false).ordinal
  + (f false false true).ordinal
  - (f false false false).ordinal

def linkedAB (f : Bool → Bool → Bool → ActionGate) : Prop :=
  secondDiffAB f false ≠ 0 ∨ secondDiffAB f true ≠ 0

def linkedBC (f : Bool → Bool → Bool → ActionGate) : Prop :=
  secondDiffBC f false ≠ 0 ∨ secondDiffBC f true ≠ 0

def linkedCA (f : Bool → Bool → Bool → ActionGate) : Prop :=
  secondDiffCA f false ≠ 0 ∨ secondDiffCA f true ≠ 0

/-- Finite engineering analogue used in the verification layer. -/
def TrefoilLike (f : Bool → Bool → Bool → ActionGate) : Prop :=
  linkedAB f ∧ linkedBC f ∧ linkedCA f ∧ thirdOrderResidual f ≠ 0

/-- Negative control: no pair interaction links and no third-order residual. -/
def UnknotControl (f : Bool → Bool → Bool → ActionGate) : Prop :=
  ¬ linkedAB f ∧ ¬ linkedBC f ∧ ¬ linkedCA f ∧ thirdOrderResidual f = 0

/-- Detached third strand: AB linked, BC/CA unlinked, zero third order. -/
def DetachedCControl (f : Bool → Bool → Bool → ActionGate) : Prop :=
  linkedAB f ∧ ¬ linkedBC f ∧ ¬ linkedCA f ∧ thirdOrderResidual f = 0

private def baseIntent : ActionIntent :=
  { withinContract := true
    hardBoundaryViolation := false
    currentTurnExplicitAuthorization := false
    reversible := true
    rollbackAvailable := true
    inspectable := true
    materialChange := false
    affectsExternalSystem := false
    audienceChange := false
    privacyChange := false
    authorityExpansion := false
    scope := .low
    uncertainty := .low
    judgmentMode := .none
    judgmentRequested := false
    concreteImmediateSafetyRisk := false
    destructive := false }

/-- TJ01: destructive × external-effect × missing-fresh-authorization,
    with standing authorization present. -/
def tj01Cube (destructive external missingFresh : Bool) : ActionGate :=
  let a : ActionIntent :=
    { baseIntent with
      destructive := destructive
      affectsExternalSystem := external
      currentTurnExplicitAuthorization := !missingFresh }
  a.assess true

/-- The positive three-way interaction witness is mechanically decidable. -/
def tj01TrefoilWitness : TrefoilLike tj01Cube := by
  unfold TrefoilLike linkedAB linkedBC linkedCA
  decide

/-- Arthur-style local stop/release boundary: at the fully active corner the
    action checkpoints; restoring fresh authorization releases to reportable
    action without erasing the external boundary. -/
theorem tj01StopReleaseWitness :
    tj01Cube true true true = .checkpoint ∧
    tj01Cube true true false = .proceedAndReport := by
  decide

/-- UC01: hard boundary × missing fresh authority × missing standing authority.
    Authorization strands do not interact with the dominant hard STOP. -/
def uc01Cube (hard missingFresh missingStanding : Bool) : ActionGate :=
  let a : ActionIntent :=
    { baseIntent with
      hardBoundaryViolation := hard
      currentTurnExplicitAuthorization := !missingFresh }
  a.assess ((!missingFresh) || (!missingStanding))

def uc01UnknotWitness : UnknotControl uc01Cube := by
  unfold UnknotControl linkedAB linkedBC linkedCA
  decide

/-- DC01: explicit recommendation × missing request × fresh action authority.
    Action authority is detached from the request/verification stop condition. -/
def dc01Cube (recommendation missingRequest freshAuthority : Bool) : ActionGate :=
  let a : ActionIntent :=
    { baseIntent with
      judgmentMode := if recommendation then .explicitModelRecommendation else .none
      judgmentRequested := !missingRequest
      currentTurnExplicitAuthorization := freshAuthority }
  a.assess freshAuthority

def dc01DetachedWitness : DetachedCControl dc01Cube := by
  unfold DetachedCControl linkedAB linkedBC linkedCA
  decide

end Basilisk
