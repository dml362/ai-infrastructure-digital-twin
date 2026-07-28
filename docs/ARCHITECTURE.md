# Architecture

## Logical model

`Company` is the tenant-neutral root. A company owns or operates campuses; campuses contain projects and power assets. Projects are delivery scopes that can have construction milestones. Customers enter leases tied to a company and optionally to a campus or project. Financing can fund a company, campus, or project. Market assumptions are scenario inputs scoped globally, geographically, or to a company. Source Registry records identify immutable evidence. Facts link evidence to individual fields on canonical entities without embedding assertions in those entity records.

Relationships are foreign-key IDs. Records must not embed another canonical entity, preventing duplicated customer, campus, or source attributes.

## Identifier convention

Canonical entity IDs are RFC 4122 UUID strings, for example `550e8400-e29b-41d4-a716-446655440000`. UUIDs are used consistently for entity primary keys and foreign-key relationships. Source Registry IDs are the intentional exception: their human-readable `SOURCE-{TYPE}-{PERIOD}-{SEQUENCE}` structure supports provenance workflows and is documented in `SOURCE_REFERENCE.md`.

IDs never encode mutable business meaning. Human-readable names and external identifiers are attributes, not primary keys.

## Physical storage

Small reference sets may begin as JSON arrays. At scale, canonical records should use newline-delimited JSON (`.jsonl`) partitioned by entity type and, when useful, company and year. One record per line supports streaming validation and avoids loading 100,000 facts into memory. Partitioning is an implementation detail and must not alter entity schemas.

Suggested future layout:

```text
data/canonical/{entity_type}/company_id={id}/year={yyyy}/part-001.jsonl
data/reference/
data/staging/
```

`entity_type` must be one of the supported schema directory names listed by `scripts/validate_repository.py`, including `source` and `fact`. Canonical filenames use `part-NNN.jsonl`, with at least three digits. The validator derives the schema from the entity directory, never from the filename, and rejects unknown directories, unsupported filenames, and structured data outside the canonical layout.

`staging` is non-canonical and must not contain committed structured data. Promotion to `canonical` requires schema validation, referential-integrity checks, and provenance checks.

## Integrity rules

- IDs are globally unique and immutable.
- All foreign keys resolve to the declared entity type.
- All `source_ids` resolve to registered source documents.
- Fact subject links resolve to the entity collection declared by `entity_type`.
- Supersession links are reciprocal and acyclic; derived Facts resolve all input Fact IDs.
- Modification timestamps cannot precede creation timestamps.
- Superseded records identify their replacement through future audit metadata.
- Canonical records contain no calculated totals that cannot be regenerated.
- Schema validation precedes cross-record integrity validation.

## Scale path

JSON Schema remains the stable contract while storage can evolve from versioned JSONL to a relational database or analytical warehouse. Loaders should preserve IDs, timestamps, source links, and schema versions. Index `id`, foreign keys, `status`, effective dates, and source IDs in database implementations.
