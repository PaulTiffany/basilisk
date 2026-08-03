# Threat model

## Assets

- human decision authority;
- private information and audience boundaries;
- rollback and option value;
- source attribution and provenance;
- integrity of action records;
- useful model initiative;
- the correction channel.

## Adversaries and failure sources

The threat model includes malicious users, compromised tools, prompt injection, model error, ambiguous standing authority, rushed humans, and well-intentioned overreach.

## Primary failure modes

### Judgment leakage

Facts, inference, and model preference are written in one seamless voice, making the preference appear independently established.

### Permission creep

A narrow permission is generalized across tasks, audiences, or time.

### Boundary laundering

A consequential action is decomposed into harmless-looking substeps so no individual step appears to cross the boundary.

### Audience shift

Private or draft content becomes public or is sent to another person without a meaningful checkpoint.

### Ledger self-certification

The acting component controls the evidence, verifier, and retained chain head, allowing it to grade its own homework.

### Prompt sensitivity

Minor paraphrase, emotional intensity, or symbolic language causes a large change in gate, authority, or normative posture.

### Confirmation paralysis

The system asks for approval so frequently that the human delegates blindly or stops using the control mechanism.

### Global correction overfit

One correction is applied to unrelated domains, flattening useful behavior.

### Hidden dependency leakage

The apparent boundary omits shared services, data sources, tools, or downstream dependencies.

### Rollback theater

A rollback path is claimed but not tested, or external effects cannot actually be undone.

## Mitigations

- explicit action features and authority objects;
- hard boundary predicates before scalar risk scores;
- current-turn authorization distinguished from standing authorization;
- append-only hash-chained records with independent retention of the head;
- minimal-pair evaluations;
- local memory scopes;
- destructive-action drills;
- external tool allowlists;
- completion reports that distinguish executed checks from proposed checks.

## Residual risk

Natural-language interpretation remains outside the finite reference controller. A system may misclassify its own intended action, omit a hidden externality, or manipulate a human into granting authority. The protocol reduces and exposes these risks; it does not eliminate them.
