# Claude Code working agreement

Read `AGENTS.md` first. Treat it as the operative control contract.

## Default mode

Retrieve, distinguish, derive, test, formalize, and label. Prefer a small validated change over a sweeping rewrite. Use existing project conventions when they are clear; state what convention you used in the completion report.

## Do not silently do these things

- invent or supply human values;
- convert user language into independent endorsement;
- publish, send, push, tag, release, deploy, or delete external data;
- broaden standing authorization from one task to another;
- expose private generative notes merely because they helped produce public work;
- treat the Quartet images as proofs;
- weaken `PROVENANCE.md` or remove cultural lineage;
- claim the protocol proves alignment.

## Useful initiative

You may fix low-stakes, reversible problems without repeated confirmation when the fix is inside the current task. A good report has this shape:

> Used the repository's established practice from `<location>`, changed `<files>`, validated with `<checks>`, and retained rollback through `<method>`.

## Meaningful checkpoint

Ask once at the semantic boundary, not at each substep. Examples: before an external write, before destructive migration, before public release, or when a requested implementation requires expanding the contract.

## Test commands

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/run_reference_evals.py
PYTHONPATH=src python3 examples/finite_controller.py
```
