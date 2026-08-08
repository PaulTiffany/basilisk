# Verification / interpretability spine

This directory makes mathematical and architectural claims mechanically traceable across prose, Lean, executable witnesses, and dependency structure.

The design is inherited from the verification discipline used in *Principia Symbolica*: a claim is not trusted because several files repeat it. A claim has an address, a status, dependency edges, and bindings to concrete artifacts. Those bindings are checked mechanically, and accidental circular justification is rejected.

## Files

- `claims.json` — claim registry / small machine-readable Atlas.
- `bindings.json` — provenance bindings from claims to exact artifact fragments, with SHA-256 receipts.
- `check_provenance.py` — validates claim IDs, statuses, dependency references, required mechanical witnesses, artifact fragments, and receipts.
- `check_recursivity.py` — computes strongly connected components of the claim graph and rejects undeclared recursive justification.
- `numeric_witness.py` — NumPy witnesses for the pseudometric and Lipschitz/constitutional separation claims.
- `EXPECTED_NUMERIC.json` — expected deterministic numerical evidence.
- `check_numeric.py` — compares the live NumPy witness against the expected evidence.

## Interpretability rule

A locally proved claim should be readable as a chain:

```text
claim ID
  -> canonical statement + status
  -> dependencies
  -> prose/formal/executable bindings
  -> machine witness
  -> generated check result
```

No claim becomes stronger because it appears in more places. A `target` remains a target even when implemented experimentally; a `standard_theorem` is not relabeled as locally proved; a Lean theorem is bound to its exact theorem signature rather than to a nearby paragraph.

## Provenance receipts

Each binding contains an exact semantic fragment and the SHA-256 of a normalized form of that fragment. The checker requires:

1. the claim ID exists;
2. the bound file exists;
3. the exact fragment still occurs in that file;
4. the recorded SHA-256 matches the fragment;
5. locally proved claims have an appropriate mechanical witness.

Changing a theorem statement, target-status sentence, or executable-schema declaration without updating its provenance binding therefore makes the interpretability check fail.

Proof-body edits do not invalidate a theorem-statement receipt if the theorem signature is unchanged; Lean compilation remains the authority for proof validity.

## Recursivity

Claim dependencies are audited as a directed graph. Any strongly connected component with more than one claim (or a self-loop) is recursive.

Recursion is **not automatically forbidden**, but it must be explicitly declared in `claims.json` under `recursion_policy.allowed_components` with an external witness explaining what closes or stabilizes the loop. Undeclared circular justification fails the check.

The initial mathematical spine is intentionally acyclic.

## Running

```bash
python3 verification/check_provenance.py
python3 verification/check_recursivity.py
python3 verification/check_numeric.py
```

`check_numeric.py` requires NumPy. CI installs the verification dependency before running `make package-check`.

## Non-claim

Passing these checks means the declared provenance graph is internally inspectable and its registered mechanical witnesses agree with their expected finite outputs. It does **not** prove the full Basilisk philosophy, the correctness of natural-language classification, or the empirical adequacy of the chosen metrics.
