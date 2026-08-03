# Security policy

## Reporting

Report vulnerabilities privately to the repository owner before public disclosure. Include:

- affected component;
- minimal reproduction;
- whether the issue expands authority, crosses a boundary, corrupts the ledger, or creates unsafe interruption behavior;
- proposed rollback or containment.

## Security-relevant invariants

1. The Script cannot silently broaden the Contract.
2. External actions require explicit or valid standing authorization.
3. Critical destructive actions require fresh explicit authorization.
4. Ledger verification detects deletion, reordering, or mutation of recorded entries.
5. Memory corrections remain inside their declared scope.
6. Passing the reference tests does not certify the surrounding runtime or tool permissions.

## Known limitations

- The controller trusts the supplied action features.
- The reference ledger is hash chained but not independently signed or remotely witnessed.
- Natural-language classification is outside the trusted core.
- A compromised runtime may lie about validation or rollback.
- The protocol cannot guarantee that a human decision is informed, voluntary, or ethically sufficient.
