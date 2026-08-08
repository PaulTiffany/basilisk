/-
Counterexamples.lean — the Lean witness for `finite_quartet.py`'s
informal Python demo: "same ledger trace, distinct hidden scripts."

We exhibit two genuinely different Scripts (decision functions) that
agree everywhere the *observed* trace actually probes, but disagree on
a specific hidden intent that the observed trace never presents. This
makes the Assurance Case's Claim C6 gap concrete: a Ledger produced by
running a Script on an observed trace cannot, by itself, rule out the
presence of a hidden Script that deviates only off-trace.
-/

import Basilisk.Script

namespace Basilisk

/-- The honest reference Script: literally `ActionIntent.assess`. -/
def scriptHonest : ActionIntent → Bool → ActionGate := ActionIntent.assess

/-- A hard-boundary-violation intent that the observed trace never
    presents. The two scripts below disagree only here. -/
def hiddenViolationIntent : ActionIntent :=
  { withinContract := true, hardBoundaryViolation := true,
    currentTurnExplicitAuthorization := false, reversible := true,
    rollbackAvailable := true, inspectable := true,
    materialChange := false, affectsExternalSystem := false,
    audienceChange := false, privacyChange := false,
    authorityExpansion := false, scope := .low, uncertainty := .low,
    judgmentMode := .none, judgmentRequested := false,
    concreteImmediateSafetyRisk := false, destructive := false }

/-- A benign, low-stakes intent — the one actually exercised by the
    observed trace used to build the demo Ledger below. -/
def observedIntent : ActionIntent :=
  { withinContract := true, hardBoundaryViolation := false,
    currentTurnExplicitAuthorization := false, reversible := true,
    rollbackAvailable := true, inspectable := true,
    materialChange := false, affectsExternalSystem := false,
    audienceChange := false, privacyChange := false,
    authorityExpansion := false, scope := .low, uncertainty := .low,
    judgmentMode := .none, judgmentRequested := false,
    concreteImmediateSafetyRisk := false, destructive := false }

/-- A hidden Script that behaves exactly like `scriptHonest` everywhere
    except that it silently proceeds on `hiddenViolationIntent` instead
    of stopping — a non-conforming Script that agrees with the honest
    one on every input the demo trace actually probes. -/
def scriptSneaky : ActionIntent → Bool → ActionGate :=
  fun a auth => if a = hiddenViolationIntent then .proceed
    else scriptHonest a auth

/-- The two scripts are genuinely different, not a vacuous pair: they
    disagree at `hiddenViolationIntent`. -/
theorem scriptHonest_ne_scriptSneaky :
    scriptHonest hiddenViolationIntent false ≠
      scriptSneaky hiddenViolationIntent false := by
  decide

/-- **Script/Ledger non-identifiability.** On the observed trace, the
    honest Script and the hidden sneaky Script produce the identical
    gate — hence identical Ledger material — even though the two
    Scripts are genuinely different functions (previous theorem). A
    Ledger built from the observed trace alone cannot rule out the
    presence of a hidden Script that only deviates off-trace. This is
    one witnessed instance, not a general theorem over all Scripts. -/
theorem ledger_does_not_identify_script :
    scriptHonest observedIntent false = scriptSneaky observedIntent false := by
  decide

end Basilisk
