# Producer / witness / authority separation

## Constitutional invariant

> **Production does not confer authority.** A producer may emit evidence about its own output, but production and self-checking are never sufficient authority for acceptance.

This note documents a **mechanically derived** exemplar. The human-supplied seed is `evals/producer_authority_seed.json`; `scripts/derive_producer_authority_exemplar.py` deterministically derives `evals/producer_authority.json`; the committed artifact is checked exactly by `tests/test_producer_authority_exemplar_derivation.py`.

The exemplar keeps three channels distinct:

1. **Producer** — proposes or constructs a candidate and may report a self-check.
2. **Witness** — independently checks a declared property of that candidate.
3. **Authority** — ratifies, modifies, vetoes, or defers the candidate for the relevant scope.

The resulting gate is intentionally conservative:

| Produced | Producer self-check | Independent witness | Authority disposition | Gate |
|---:|---:|---:|---|---|
| yes | yes | no | ratify | checkpoint |
| yes | yes | yes | defer | checkpoint |
| yes | yes | yes | veto | stop |
| yes | yes | yes | modify | checkpoint on successor |
| yes | no/yes | yes | ratify | proceed and report |

The producer self-check remains inspectable evidence, but changing only that bit cannot change the acceptance gate. This is the mechanical content of the separation claim; it is not a claim that producer-side verification is useless.

## Decision seams, not veto scores

A consequential branch point should preserve enough provenance to reconstruct the decision without turning disagreement into a performance metric. The exemplar records candidate identity, proposal channel, authority channel, disposition, contemporaneous reason, and successor identity when modification creates a new candidate.

There is deliberately **no veto count, override score, or human-agency KPI**. Such a metric would reward theatrical disagreement. The object of interest is the inspectable seam where production and acceptance could have diverged.

Ratification is first-class provenance too. If a model proposes an implementation choice and the human accepts it without independently deriving it, the record should say so. `Defer` is also an authority action: "not enough evidence yet" must remain representable without being flattened into failure or assent.

## Mechanical witnesses

The boundary has four mutually checking surfaces:

- `evals/producer_authority_seed.json` — human-supplied conceptual seed;
- `scripts/derive_producer_authority_exemplar.py` → `evals/producer_authority.json` — deterministic derivation and committed artifact;
- `src/map_lb/producer_authority.py` plus `tests/test_producer_authority.py` — executable finite gate and boundary cases;
- `formal/Basilisk/ProducerAuthority.lean` — Lean mirror and theorem surface.

The Python tests require self-certification alone to remain checkpointed; changing only producer self-check to leave the gate unchanged; witness without ratification to remain checkpointed; veto to stop a witnessed candidate; modification to create a successor checkpoint; and witness plus ratification to release the candidate.

The Lean theorem `producer_self_check_is_not_acceptance_authority` states the key non-authority property directly: with production state, independent witness, and the decision seam held fixed, toggling only the producer's self-check leaves the acceptance gate unchanged.

## Relationship to the Quartet

This is a small cross-cutting exemplar rather than a fifth Quartet component.

- **Contract** defines which acceptance conditions matter.
- **Script** performs the gate projection.
- **Blanket** keeps producer, witness, and authority channels from silently collapsing into one another.
- **Ledger** preserves the decision seam and later evidence.

The Ledger records an authority decision; it does not create that authority. Likewise a green producer self-check or a green independent witness can be evidence without becoming sovereign.

The separation is not a containment ontology. **A barrier is not a wall, and a model is not a box.** The producer can communicate through the boundary; evidence can traverse it; witnesses can answer it. The invariant is narrower: those traversals do not silently transport acceptance authority.

## Non-claims

This exemplar does not prove that every real deployment has a truly independent witness, that a human authority holder is always correct, or that every consequential decision can be reduced to four dispositions. It proves and tests only the declared finite separation law.

In particular, "independent" is a systems property that must be justified by the actual deployment boundary. Two nominal channels controlled by the same producer do not become independent merely because the data structure gives them different names. The certificate also explicitly refuses the claims that a model is a box or that the authority boundary is an impermeable wall.

## Regenerate and check

```bash
python3 scripts/derive_producer_authority_exemplar.py --write
python3 scripts/derive_producer_authority_exemplar.py --check
python3 -m unittest tests.test_producer_authority_exemplar_derivation -v
```
