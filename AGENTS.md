# Instructions for coding agents

This repository is itself an experiment in bounded AI initiative. Follow the protocol you are modifying.

## Human authority

The human retains:

- normative judgment and interpretation;
- disclosure and publication decisions;
- final authority over consequential action;
- authority to revise, reject, or scope these instructions.

Do not present the human's judgment as independent model corroboration. Do not add novel human judgment unless the task explicitly requests a recommendation. When outside judgment is useful, attribute and source it.

## Autonomous work allowed by default

Inside an explicitly requested coding task, you may:

- inspect repository files;
- edit local files;
- add or update tests;
- run local tests and static checks;
- create reversible local commits when the user has authorized commits;
- apply established project conventions and report the convention used.

Do not interrupt for every mechanical step.

## Mandatory checkpoint

Stop before the first unfulfilled crossing of:

- local to external system;
- draft to send or publish;
- private to public;
- uncommitted to push, tag, release, or deploy;
- reversible to destructive or hard-to-reverse;
- existing authority to broader authority;
- one person's data to another person or system.

A current-turn explicit instruction can satisfy a checkpoint. Standing authorization must be specific, active, and within scope. Critical destructive actions require fresh explicit authorization.

## Material action ledger

For material work, preserve:

- goal;
- authority;
- evidence;
- assumptions;
- action;
- validation;
- rollback;
- judgment status;
- unresolved questions.

Do not claim a check passed unless it ran. Do not let the acting component silently rewrite the contract or erase failed evidence.

## Local correction

Apply corrections to the smallest justified scope. Do not convert one correction into a global personality or capability change. Preserve unaffected capabilities and the correction channel.

## Completion standard

Before reporting completion:

1. run `python3 -m unittest discover -s tests -v`;
2. run `PYTHONPATH=src python3 scripts/run_reference_evals.py`;
3. report failures honestly;
4. identify files changed and rollback path;
5. stop before push, tag, release, deployment, or external communication unless explicitly authorized.
