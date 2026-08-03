# Implementation guide

## 1. Preflight

Construct an `ActionIntent` before tool use. Record:

- requested goal;
- intended action class;
- current-turn authorization;
- applicable standing authority;
- boundary features;
- reversibility and rollback;
- scope and uncertainty;
- judgment mode.

Do not infer consequential authority from convenience.

## 2. Assess

Pass the intent and optional standing authority to the controller.

```python
from map_lb import ActionIntent, assess_action

assessment = assess_action(intent, standing_authority)
```

The result contains a gate, reasons, risk score, and whether reporting is required.

## 3. Execute only inside the gate

- `proceed`: execute locally;
- `proceed_and_report`: execute, validate, and retain rollback;
- `checkpoint`: ask once for the missing authority or decision;
- `stop`: do not execute; identify the violated invariant.

A checkpoint response should be specific:

> This changes the audience from private draft to external recipient. Authorize sending this exact draft to this recipient?

Avoid generic “Are you sure?” prompts.

## 4. Record

Append a ledger entry after a material action or checkpoint decision. Preserve the prior hash. Store the chain head independently for meaningful assurance.

## 5. Complete

Report:

- what practice or source was used;
- what changed;
- what checks ran;
- rollback path;
- judgment status;
- unresolved questions.

## 6. Integration patterns

### Coding agent

Allow local edits, tests, formatting, and reversible refactors. Checkpoint before push, tag, release, deployment, destructive migration, or external issue/comment creation.

### Research assistant

Allow retrieval, source comparison, derivation, and draft generation. Label hypotheses and sourced judgments. Checkpoint before contacting people, publishing, or exposing private notes.

### Administrative agent

Allow local sorting and drafting. Checkpoint before sending, purchasing, signing, canceling, or changing another person's access.

### Multi-agent runtime

Each agent should have a separate Script identity and least-authority Contract. A shared Ledger does not justify shared authority. Tool routers and memory stores belong inside the Blanket analysis.
