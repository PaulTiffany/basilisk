# Project orchestration

The repository is not a pile of adjacent artifacts. It is a dependency graph whose layers must remain cross-linked and testable.

The canonical machine-readable declaration is [`PROJECT_GRAPH.json`](../PROJECT_GRAPH.json). The governing commitments are in [`PHILOSOPHY.md`](../PHILOSOPHY.md).

## Layer order

```text
philosophy + provenance
        ↓
constitution
        ↓
mathematics
   ↙          ↘
formal       runtime
   ↘          ↙
 evaluation + evidence
        ↓
assurance
        ↓
orchestration
```

The arrows indicate obligations, not automatic truth. A downstream layer must identify what it imports from upstream and what it changes or leaves unimplemented.

## What CI must establish

The unified workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) checks four different claims:

1. **Project coherence** — declared artifacts exist, local Markdown links resolve, required cross-links are present, the layer graph is acyclic, and each tracked principle names evidence, checks, and open gaps.
2. **Runtime behavior** — Python unit tests and reference evaluations pass.
3. **Artifact validity** — JSON specifications and examples parse.
4. **Formal validity** — the repository-pinned Lean toolchain builds the formal core.

None of these checks substitutes for another. A successful Lean build does not prove the implementation conforms. Passing Python tests does not prove the philosophy has propagated. Valid links do not prove the linked claim true.

## Principle bindings

Each principle in `PROJECT_GRAPH.json` has:

- an exact phrase that must occur in `PHILOSOPHY.md`;
- a status: `declared`, `partial`, or `implemented`;
- evidence artifacts;
- checks that witness part of the claim;
- explicit gaps unless the principle is marked implemented.

This makes philosophy-to-artifact drift visible without pretending every ethical commitment is reducible to CI.

## Change protocol

A material change should answer:

1. Which layer changed?
2. Which upstream commitments does it interpret?
3. Which downstream artifacts may now be stale?
4. Which checks witness the change?
5. Which gaps remain?

When a new principle is added to `PHILOSOPHY.md`, either bind it in `PROJECT_GRAPH.json` or state why it is intentionally not yet orchestrated. When a proof, test, or runtime mechanism changes, update its principle binding and assurance status.

## Merge discipline

The intended merge gate is the unified `Basilisk project CI` workflow. Branch protection should require both jobs:

- `project / project graph, runtime, and artifact checks`
- `formal / lake build`

Branch protection is repository-host configuration rather than a file in this tree, so CI records it as an explicit remaining gap until configured.
