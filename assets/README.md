# Human-facing symbols and media archive

The four Basilisk images are mnemonic and communicative artifacts:

1. Contract — permission before action;
2. Script — executable realization;
3. Blanket — bounded transmission and dependency closure;
4. Ledger — trace, account, and certificate.

They are not enforcement mechanisms and should not be treated as mathematical proofs. The protocol lives in explicit permissions, tool boundaries, execution rules, and inspectable records.

This directory also preserves the visual history of the project.

## Layout

```text
assets/
  archive/       original received files, preserved byte-for-byte
  gallery/       curated display copies and thumbnails
  media-manifest.json
```

## Canonical accession names

```text
BSK-IMG-001-original-basilisk-blanket.<ext>
BSK-IMG-002-markov-blanket-revision.<ext>
BSK-IMG-003-boundary-correspondence-revision.<ext>
BSK-IMG-004-basilisk-quartet.<ext>
BSK-IMG-005-frame-holder-constitution.<ext>
```

## Preservation rules

- Never overwrite an archived source image.
- Never claim a recreation is the original.
- Record every derivative with a `derived_from` relation.
- Record SHA-256, dimensions, media type, source filename, and transformation notes.
- Keep rejected revisions when they document conceptual development.

See [`MEDIA.md`](../MEDIA.md) for the human-facing gallery and archival narrative.