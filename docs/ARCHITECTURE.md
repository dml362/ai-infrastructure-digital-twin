# Architecture

## Logical model

`Company` is the tenant-neutral root. A company owns or operates campuses; campuses contain projects and power assets. Projects are delivery scopes that can have construction milestones. Customers enter leases tied to a company and optionally to a campus or project. Financing can fund a company, campus, or project. Market assumptions are scenario inputs scoped globally, geographically, or to a company. All entities cite source documents.

Relationships are foreign-key IDs. Records must not embed another canonical entity, preventing duplicated customer, campus, or source attributes.

## Identifier convention

Entity IDs are uppercase prefixes plus a stable UUID, for example `COMPANY-550e8400-e29b-41d4-a716-446655440000`. Prefixes are `COMPANY`, `CAMPUS`, `PROJECT`, `LEASE`, `POWER`, `CUSTOMER`, `FINANCING`, `MILESTONE`, `SOURCE`, and `MARKET`.

IDs never encode mutable business meaning. Human-readable names and external identifiers are attributes, not primary keys.

## Physical storage

Small reference sets may begin as JSON arrays. At scale, canonical records should use newline-delimited JSON (`.jsonl`) partitioned by entity type and, when useful, company and year. One record per line supports streaming validation and avoids loading 100,000 facts into memory. Partitioning is an implementation detail and must not alter entity schemas.

Suggested future layout:

```text
data/canonical/{entity_type}/company_id={id}/year={yyyy}/part-*.jsonl
data/reference/
data/staging/
```

`staging` is non-canonical. Promotion to `canonical` requires schema validation, referential-integrity checks, and provenance checks.

## Integrity rules

- IDs are globally unique and immutable.
- All foreign keys resolve to the declared entity type.
- All `source_ids` resolve to registered source documents.
- Modification timestamps cannot precede creation timestamps.
- Superseded records identify their replacement through future audit metadata.
- Canonical records contain no calculated totals that cannot be regenerated.
- Schema validation precedes cross-record integrity validation.

## Scale path

JSON Schema remains the stable contract while storage can evolve from versioned JSONL to a relational database or analytical warehouse. Loaders should preserve IDs, timestamps, source links, and schema versions. Index `id`, foreign keys, `status`, effective dates, and source IDs in database implementations.
