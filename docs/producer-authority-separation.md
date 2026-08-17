# Producer / witness / authority separation

## Constitutional invariant

> **Production does not confer authority.** A producer may emit evidence about its own output, but production and self-checking are never sufficient authority for acceptance.

The mechanical exemplar keeps three channels distinct:

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

A consequential branch point should preserve enough provenance to reconstruct the decision without turning disagreement into a performance metric. The exemplar records:

- candidate identity;
- proposal channel;
- authority channel;
- disposition: `ratify`, `modify`, `veto`, or `defer`;
- contemporaneous reason;
- successor identity when modification creates a new candidate.

There is deliberately **no veto count, override score, or human-agency KPI**. Such a metric would reward theatrical disagreement. The object of interest is the inspectable seam where production and acceptance could have diverged.

Ratification is first-class provenance too. If a model proposes an implementation choice and the human accepts it without independently deriving it, the record should say so. `Defer` is also an authority action: "not enough evidence yet" must remain representable without being flattened into failure or assent.

## Mechanical witnesses

The same boundary is encoded twice:

- `src/map_lb/producer_authority.py` — executable finite gate;
- `formal/Basilisk/ProducerAuthority.lean` — Lean mirror and theorems.

The Python unit tests require:

- self-certification alone cannot release a candidate;
- changing only producer self-check cannot change the gate;
- witness without ratification remains checkpointed;
- veto stops even a witnessed candidate;
- modification creates a successor checkpoint rather than silent acceptance;
- witness plus ratification releases the candidate.

The Lean theorem `producer_self_check_is_not_acceptance_authority` states the key non-authority property directly: with production state, independent witness, and decision seam held fixed, toggling only the producer's self-check leaves the acceptance gate unchanged.

## Relationship to the Quartet

This is a small cross-cutting exemplar rather than a fifth Quartet component.

- **Contract** defines which acceptance conditions matter.
- **Script** performs the gate projection.
- **Blanket** keeps producer, witness, and authority channels from silently collapsing into one another.
- **Ledger** preserves the decision seam and later evidence.

The Ledger records an authority decision; it does not create that authority. Likewise a green producer self-check or a green independent witness can be evidence without becoming sovereign.

## Non-claims

This exemplar does not prove that every real deployment has a truly independent witness, that a human authority holder is always correct, or that every consequential decision can be reduced to four dispositions. It proves and tests only the declared finite separation law.

In particular, "independent" is a systems property that must be justified by the actual deployment boundary. Two nominal channels controlled by the same producer do not become independent merely because the data structure gives them different names.
