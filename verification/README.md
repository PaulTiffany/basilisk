# Verification / interpretability spine

This directory makes mathematical and architectural claims mechanically traceable across prose, Lean, executable witnesses, and dependency structure.

The design follows the verification discipline used in *Principia Symbolica*: a claim is not trusted because several files repeat it. A claim has an address, a status, dependency edges, and bindings to concrete artifacts. Those bindings are checked mechanically, accidental circular justification is rejected, and cross-substrate agreement is tested explicitly.

## Files

- `claims.json` — semantic claim registry / small machine-readable Atlas.
- `bindings.json` — provenance bindings from claims to exact artifact fragments, with SHA-256 receipts.
- `formal_inventory.json` — complete inventory of local Lean theorem/lemma declarations, separate from the smaller semantic Atlas.
- `check_provenance.py` — validates claim IDs, statuses, dependency references, required mechanical witnesses, artifact fragments, and receipts.
- `check_recursivity.py` — computes strongly connected components of the claim graph and rejects undeclared recursive justification.
- `check_formal_closure.py` — rejects unregistered Lean theorems, stale theorem receipts, proof modules not imported by the root kernel, and broken semantic-to-formal links.
- `numeric_witness.py` — NumPy witnesses for the pseudometric and Lipschitz/constitutional separation claims.
- `EXPECTED_NUMERIC.json` — expected deterministic numerical evidence.
- `check_numeric.py` — compares the live NumPy witness against the expected evidence.
- `controller_vectors.json` — shared observable corpus for Python/Lean controller correspondence.
- `check_controller_vectors.py` — runs the real Python reference controller against the shared corpus.
- `check_cross_witness.py` — derives expected Lean vector expressions from the JSON corpus and verifies the formal transcription.
- `meta_mutation.py` — deliberately corrupts temporary copies of provenance, recursivity, numerical evidence, formal closure, and cross-witness artifacts and requires the relevant checker to detect each mutation.

## Interpretability rule

A locally proved or mechanically witnessed claim should be readable as a chain:

```text
claim ID
  -> canonical statement + epistemic status
  -> declared dependencies
  -> prose/formal/executable bindings
  -> mechanical witness(es)
  -> agreement/closure checks
  -> adversarial mutation showing the checker can fail closed
```

No claim becomes stronger because it appears in more places. A `target_theorem` remains a target even when implemented experimentally; a `standard_theorem` is not relabeled as locally proved; a Lean theorem is bound to its exact theorem signature rather than to a nearby paragraph; an engineering correspondence claim is not silently upgraded into a universal equivalence theorem.

## Semantic Atlas vs formal inventory

The semantic Atlas stays intentionally small: it records claims a researcher would actually cite or discuss.

The formal inventory is exhaustive: every local `theorem` or `lemma` in the finite Lean kernel must be registered, including helper results. This avoids two opposite failures:

- orphan proofs that exist in source but are invisible to provenance machinery;
- an unusably bloated semantic Atlas in which every helper lemma is promoted into a headline claim.

`check_formal_closure.py` joins these two layers mechanically.

## Provenance receipts

Each binding contains an exact semantic fragment and its SHA-256 receipt. The checker requires:

1. the claim ID exists;
2. the bound file exists;
3. the exact fragment still occurs in that file;
4. the recorded SHA-256 matches the fragment;
5. locally proved or mechanically witnessed claims expose the declared witness kinds.

Changing a theorem statement, target-status sentence, or executable witness declaration without updating its provenance binding therefore makes the interpretability check fail.

Proof-body edits do not invalidate a theorem-statement receipt if the theorem signature is unchanged; Lean compilation remains the authority for proof validity.

## Recursivity

Claim dependencies are audited as a directed graph. Any strongly connected component with more than one claim (or a self-loop) is recursive.

Recursion is **not automatically forbidden**, but it must be explicitly declared in `claims.json` under `recursion_policy.allowed_components` with an external witness explaining what closes or stabilizes the loop. Undeclared circular justification fails the check.

The current mathematical spine is intentionally acyclic.

## Cross-witness agreement

Cross-witnessing is stronger than merely placing Lean, NumPy, and Python files beside one another.

For the controller bridge:

```text
controller_vectors.json
        |             \
        v              v
real Python        Lean vector proposition
controller              |
        |                v
        |          Lean `by decide`
        \             /
         agreement gate
```

`check_controller_vectors.py` checks the Python edge. `check_cross_witness.py` checks that the JSON cases are transcribed into the Lean proposition. `lake build` checks the Lean edge.

This machinery already exposed a real drift: the earlier Lean controller mirror omitted Python's `score >= 3` reporting branch and the `rollback_available` / `inspectable` fields that feed that score. The formal Script was repaired rather than weakening the correspondence claim.

## Meta-mutation

The verification system is itself subjected to mutation testing on isolated temporary copies. Current mutations include:

- corrupting a provenance receipt;
- introducing undeclared recursive justification;
- falsifying expected NumPy evidence;
- removing a Lean theorem from the formal inventory;
- removing a proof module from the root kernel;
- falsifying a shared controller expected gate;
- corrupting the Lean transcription of a shared controller vector.

A verifier that cannot detect its assigned corruption does not count as a working verifier.

## Running

```bash
make interpret
```

or individually:

```bash
python3 verification/check_provenance.py
python3 verification/check_recursivity.py
python3 verification/check_numeric.py
python3 verification/check_formal_closure.py
python3 verification/check_controller_vectors.py
python3 verification/check_cross_witness.py
python3 verification/meta_mutation.py
```

The NumPy witness requires the `verification` optional dependency. CI installs it before running `make package-check`; the formal CI job separately runs the Lean build.

## Non-claim

Passing these checks means the declared provenance graph is internally inspectable, its registered finite witnesses agree with their expected outputs, and the current deliberate corruptions are detected. It does **not** prove the full Basilisk philosophy, a universal Python↔Lean equivalence, the correctness of natural-language classification, or the empirical adequacy of the chosen metrics.
