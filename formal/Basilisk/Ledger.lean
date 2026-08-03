/-
Ledger.lean — a lossless encode/decode pair for a minimal Ledger entry,
plus the chain-linking discipline from `docs/protocol.md` §6 /
`src/map_lb/ledger.py`'s `HashLedger.verify`.

Scope note: the actual SHA-256 computation in `ledger.py` is not
modeled. `previousHash`/`entryHash` are abstract `Nat` identifiers here;
this file formalizes the *linking discipline* (each entry's
`previousHash` must equal the prior entry's `entryHash`) and a genuine
lossless encode/decode round-trip, not cryptographic hash security.
-/

import Basilisk.Script

namespace Basilisk

/-- A minimal Ledger entry: the fields relevant to chain integrity. -/
structure LedgerEntry where
  gate : ActionGate
  previousHash : Nat
  entryHash : Nat
  deriving DecidableEq, Repr

/-- A ledger is a list of entries, oldest first. -/
abbrev Ledger := List LedgerEntry

/-- The genesis hash, matching `ledger.py`'s `GENESIS_HASH`. -/
def genesisHash : Nat := 0

/-- Whether `entries`, appended after a ledger whose current head hash
    is `prevHead`, forms a validly chained sequence. -/
def chainedFrom (prevHead : Nat) : List LedgerEntry → Prop
  | [] => True
  | e :: rest => e.previousHash = prevHead ∧ chainedFrom e.entryHash rest

/-- A ledger is chained when it links back to the genesis hash. -/
def Ledger.chained (l : Ledger) : Prop := chainedFrom genesisHash l

/-- Encoding a `LedgerEntry` as a flat `List Nat`. -/
def LedgerEntry.encode (e : LedgerEntry) : List Nat :=
  [e.gate.toNat, e.previousHash, e.entryHash]

/-- Decoding the flat `List Nat` representation back into a
    `LedgerEntry`, when well-formed. -/
def LedgerEntry.decode : List Nat → Option LedgerEntry
  | [g, p, h] => (ActionGate.fromNat g).map (fun gate => ⟨gate, p, h⟩)
  | _ => none

/-- Losslessness: decoding an encoded entry always recovers it exactly. -/
theorem LedgerEntry.decode_encode (e : LedgerEntry) :
    LedgerEntry.decode (LedgerEntry.encode e) = some e := by
  simp [LedgerEntry.encode, LedgerEntry.decode, ActionGate.fromNat_toNat]

end Basilisk
