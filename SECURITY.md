# Security policy

## Reporting a vulnerability

Please do not disclose an exploitable vulnerability in a public issue before a mitigation is available.

Use GitHub's private vulnerability reporting feature for this repository when available. If private reporting is unavailable, contact the repository owner through the contact information linked from the GitHub profile and include **Basilisk security report** in the subject.

A useful report includes:

- affected commit or release;
- affected component and trust boundary;
- reproduction steps or a minimal counterexample;
- expected and observed behavior;
- likely impact, including audience, privacy, authority, or irreversibility changes;
- known mitigations and rollback constraints.

Do not include live secrets, private personal data, or destructive proof-of-concept payloads beyond what is necessary to establish the issue.

## Supported versions

The default branch is the only supported development line until tagged releases are published. Security fixes may be applied directly to the latest supported release once releases exist.

## BIS security model

The [Basilisk Integration System](docs/project-orchestration.md) treats repository automation as a governed application:

- **Contract:** workflow files, `PROJECT_GRAPH.json`, branch rules, and this policy;
- **Script:** GitHub Actions jobs and repository automation;
- **Blanket:** least-privilege tokens, immutable action pins, isolated jobs, timeouts, and protected merge paths;
- **Ledger:** commits, pull requests, workflow logs, artifacts, attestations, and security findings.

## Security-relevant invariants

1. The Script cannot silently broaden the Contract.
2. External actions require explicit or valid standing authorization.
3. Critical destructive actions require fresh explicit authorization.
4. Ledger verification detects deletion, reordering, or mutation of retained entries.
5. Memory corrections remain inside their declared scope.
6. Workflow actions are pinned to immutable full commit SHAs.
7. Default workflow tokens are read-only; write permissions are job-local and purpose-specific.
8. Passing checks does not certify the surrounding host, specification completeness, or moral legitimacy.

## Response priorities

1. contain ongoing exposure without destroying evidence;
2. preserve rollback and affected-party notification paths;
3. distinguish runtime compromise from specification or assurance failure;
4. record the fix, validation, residual risk, and any required constitutional change;
5. publish a proportionate advisory after mitigation.

## Known limitations

- The controller trusts supplied action features.
- The runtime Blanket is not yet an independent capability mediator.
- The reference ledger is hash chained but not independently signed or remotely witnessed.
- Natural-language classification is outside the trusted core.
- A compromised runtime may lie about validation or rollback.
- GitHub and third-party Actions remain external trust dependencies.
- The protocol cannot guarantee that a human decision is informed, voluntary, or ethically sufficient.
