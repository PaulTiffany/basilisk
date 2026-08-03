# Build report

**Built:** 2026-08-02

## Included

- Basilisk Quartet mathematical note and existing finite sanity model;
- MAP-LB control protocol and mathematical model;
- human-authority, external-judgment, memory, threat, assurance, and implementation docs;
- vendor-neutral pretest prompt and compact memory;
- JSON schemas and reusable templates;
- dependency-free Python reference controller;
- hash-chained ledger and scoped memory implementation;
- minimal-pair and boundary evaluation corpora;
- Claude Code and Codex-compatible agent instructions;
- human-facing Quartet diagrams;
- provenance and licensing materials.

## Validation performed on the packaged tree

- `python3 -m unittest discover -s tests -v`
- `PYTHONPATH=src python3 scripts/run_reference_evals.py`
- `python3 scripts/validate_json.py`
- `PYTHONPATH=src python3 -m map_lb verify-ledger examples/sample-ledger.jsonl`
- `PYTHONPATH=src python3 examples/finite_controller.py`
- `python3 examples/finite_quartet.py`

The exact results are recorded during packaging and summarized in the root `VALIDATION.txt`.

## Deliberate exclusions

- raw private conversation transcript;
- Git metadata;
- external deployment credentials;
- claims that this protocol proves general alignment.
