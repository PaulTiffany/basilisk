/-
LedgerSemantics.lean — integrity is not truth.

The Ledger can witness that a record was preserved and linked according to the
protocol. That structural property does not entail the truth of an arbitrary
semantic proposition interpreted from the record.
-/

import Basilisk.Ledger

namespace Basilisk

/-- A tiny semantic payload used only to witness the separation between
    structural ledger validity and proposition truth. -/
structure SemanticLedgerEntry where
  structural : LedgerEntry
  claim : Bool
  deriving DecidableEq, Repr

def SemanticLedgerEntry.claimTrue (e : SemanticLedgerEntry) : Prop :=
  e.claim = true

private def structurallyValidFalseClaim : SemanticLedgerEntry :=
  { structural :=
      { gate := .proceed
        previousHash := genesisHash
        entryHash := 7 }
    claim := false }

/-- A structurally chained one-entry ledger can carry a false semantic claim. -/
theorem chained_does_not_entail_claim_truth :
    Ledger.chained [structurallyValidFalseClaim.structural] ∧
    ¬ structurallyValidFalseClaim.claimTrue := by
  constructor
  · simp [Ledger.chained, chainedFrom, structurallyValidFalseClaim, genesisHash]
  · simp [SemanticLedgerEntry.claimTrue, structurallyValidFalseClaim]

/-- Even lossless encoding/decoding of the structural record does not upgrade
    its semantic payload into truth. -/
theorem lossless_record_does_not_entail_claim_truth :
    LedgerEntry.decode (LedgerEntry.encode structurallyValidFalseClaim.structural) =
      some structurallyValidFalseClaim.structural ∧
    ¬ structurallyValidFalseClaim.claimTrue := by
  constructor
  · exact LedgerEntry.decode_encode structurallyValidFalseClaim.structural
  · simp [SemanticLedgerEntry.claimTrue, structurallyValidFalseClaim]

end Basilisk
