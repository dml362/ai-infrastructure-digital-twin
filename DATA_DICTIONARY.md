# Data Dictionary Standard

The JSON Schemas in `schemas/` are the executable data dictionary. Every field must be documented where it is defined so that a reader can interpret a record without company-specific knowledge.

Each field definition must include:

| Attribute | Requirement |
| --- | --- |
| Name | Stable `snake_case` key; never reuse a retired name for a different meaning |
| Description | Plain-language meaning, scope, and interpretation |
| Type | JSON type, including whether `null` is allowed |
| Required | Whether absence makes the record invalid |
| Unit | Required for measurable quantities; encode in the field name when fixed, such as `_mw` or `_usd` |
| Format | ISO 8601 dates/timestamps, ISO 4217 currencies, and other machine-readable formats |
| Allowed values | Enumerations with lifecycle meaning documented |
| Relationships | Target entity type for every foreign-key ID |
| Provenance | Whether the value is sourced, estimated, or derived |
| Constraints | Bounds, patterns, uniqueness expectations, and conditional rules |

## Global fields

Every entity contains:

- `id`: globally unique, immutable RFC 4122 UUID for canonical entities. Source Registry records intentionally use the human-readable source-reference convention.
- `created_at`: UTC timestamp when the record was first created.
- `modified_at`: UTC timestamp of the most recent change; never earlier than `created_at`.
- `source_ids`: non-empty, deduplicated list of Source Registry `id` references.
- `confidence_score`: integer from 1 through 5 under the confidence policy.
- `status`: lifecycle state: `planned`, `active`, `inactive`, `completed`, `cancelled`, `superseded`, or `unknown`.
- `notes`: optional factual clarification; not a substitute for structured fields or provenance.

## Source Registry fields

Source fields distinguish three locations: `source_url` is the original authoritative location, `storage_location` plus `external_file_id` identify an immutable object in an external archive, and the JSONL Source record is the repository metadata catalog. External-object metadata documents provider, original filename, media type, byte size, digest algorithm and value, archive time, access status, copyright, and restrictions. Null storage fields mean no archived bytes exist; they must never be interpreted as permission to copy evidence into GitHub.

Source supersession uses `superseded_by_source_id` and `supersedes_source_ids`. These links identify evidence revisions and do not erase either registry record.

## Fact fields

A Fact documents one assertion only. `entity_type` and `entity_id` form a typed foreign key to its subject. `field_name` supplies stable field semantics; `observed_value` supplies the value; and `unit` supplies quantitative interpretation. `observation_date` records when evidence first disclosed the value, while `effective_date` records when the value applied in the real world.

`source_ids` provides evidence provenance. `superseded_by_fact_id` and `supersedes_fact_ids` preserve historical change. `input_fact_ids` and `derivation_method` make derived values reproducible. `estimation_method` distinguishes documented inference from direct observation. Status and confidence describe different dimensions: status is workflow/interpretation, while confidence is evidence strength.

## Naming and units

Use singular entity names and plural arrays. Foreign-key IDs end in `_id` or `_ids` and use the shared UUID contract. Dates end in `_date`; timestamps end in `_at`. Fixed-unit numeric fields include their unit (`capacity_mw`, `amount_usd`). When currencies may vary, store `amount` and an adjacent ISO 4217 `currency` field.

Percentages are decimal fractions (`0.25` means 25%). Energy is in MWh and power is in MW unless a field states otherwise. Monetary values must state whether they are nominal or real and identify the as-of date when material.

## Evolution rules

New optional fields are backward-compatible. New required fields, changed meanings, narrowed enumerations, or altered units require a schema-version change and migration notes. Deprecated fields remain documented until data migration is complete. Company-specific fields should first be tested for a general infrastructure meaning; use an `extensions` object only when no stable shared concept exists.

Source evidence and historical Facts are append-only. A corrected value creates a new Fact rather than mutating `observed_value`; the prior Fact remains accessible through explicit supersession links.
