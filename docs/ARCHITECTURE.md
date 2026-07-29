# Architecture

## Logical model

`Company` is the tenant-neutral root of the structural graph. Source Registry records identify immutable evidence. Field Registry records define governed semantics. Facts connect one Source-backed assertion and one immutable Field ID to one structural entity without embedding assertions in entity records.

The four validation layers are distinct: structural validity checks JSON contracts and canonical layout; semantic validity resolves Field rules; provenance validity resolves Sources; lifecycle validity enforces history, derivation, cardinality, and supersession.

Relationships are foreign-key IDs. Records must not embed another canonical entity, preventing duplicated customer, campus, or source attributes.

## Identifier convention

Canonical entity IDs are RFC 4122 UUID strings, for example `550e8400-e29b-41d4-a716-446655440000`. UUIDs are used consistently for entity primary keys and foreign-key relationships. Source Registry IDs are the intentional exception: their human-readable `SOURCE-{TYPE}-{PERIOD}-{SEQUENCE}` structure supports provenance workflows and is documented in `SOURCE_REFERENCE.md`.

IDs never encode mutable business meaning. Every entity also has a stable machine-readable `slug` and a non-authoritative `display_name` for navigation. The label is not a legal or sourced name. All changing, evidentiary, analytical, and source-derived attributes are Facts, including legal/former names, headquarters and location, capacity and power, project dates and construction status, customer relationships and lease terms, financial values, ownership percentages, and operating characteristics.

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
- All Fact `source_ids` resolve to registered Sources; structural entity records do not carry provenance because they contain no assertions.
- Every Fact `field_id` resolves to exactly one governed Field definition.
- Fact entity type, value type, units, classification, verification state, cardinality, and deprecation use comply with that Field.
- Fact subject links resolve to the entity collection declared by `entity_type`.
- Supersession links are reciprocal and acyclic; derived Facts resolve all input Fact IDs.
- Fact assertion and production fields are immutable; only documented administrative fields may change in place.
- Superseded records identify their replacement through future audit metadata.
- Canonical records contain no calculated totals that cannot be regenerated.
- Schema validation precedes cross-record integrity validation.

## Scale path

JSON Schema remains the stable structural contract while deterministic repository validation enforces cross-record semantics. Storage may evolve while preserving Entity, Source, Field, and Fact IDs. Index `field_id`, subject keys, state fields, effective dates, and Source IDs.
