# Memory design: scoped correction without flattening

## Purpose

Memory should improve continuity without turning every local correction into a global identity claim or permanent prohibition.

## Rule object

A memory rule contains:

```text
id
scope
text
kind
source
confidence
created_at
expires_at (optional)
supersedes (optional)
active
```

Recommended kinds:

- `preference`;
- `boundary`;
- `correction`;
- `project_fact`;
- `standing_authority`;
- `temporary_context`.

## Scope hierarchy

Use dotted scopes:

```text
judgment.unsolicited
judgment.requested
coding.local
coding.external.push
communication.email.send
symbolic_exploration.interpretation
safety.immediate
```

Lookup may include exact scope and parent rules, but a child correction does not rewrite siblings.

Example:

```text
Correction: Do not provide unsolicited human judgment.
Scope: judgment.unsolicited
```

This should not disable arithmetic, requested recommendations, factual contradiction, or code repair.

## Supersession

A new correction should deactivate only rules it explicitly supersedes inside the same scope. Historical records remain in the ledger.

## Promotion

A local pattern should not become a global rule merely because it recurs. Promotion requires explicit human approval or a separately defined review process.

## Forgetting and expiration

Temporary context should expire. Standing authority should be revocable and ideally time bounded. Cultural provenance and authorship records should not be treated like disposable convenience preferences.

## Testable properties

1. **Locality:** unrelated scopes produce unchanged outputs.
2. **Reversibility:** deactivating a rule restores prior behavior.
3. **Traceability:** each active rule identifies its source.
4. **No silent promotion:** scope broadening leaves an explicit record.
5. **Conflict visibility:** incompatible active rules are surfaced rather than arbitrarily merged.
