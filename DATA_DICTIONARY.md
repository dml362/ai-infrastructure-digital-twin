# Data Dictionary Standard

JSON Schemas in `schemas/` are the executable data dictionary. Every property must include a meaningful description of its scope, type, nullability, unit, relationship target, allowed interpretation, provenance role, constraints, and lifecycle semantics where applicable.

## Structural entity contract

Entity records are graph anchors, not evidence containers. They contain an immutable UUID, fixed `entity_type`, stable machine-readable `slug`, non-authoritative `display_name`, creation/modification timestamps, repository `record_status`, administrative notes, and only foreign keys needed to define graph topology. `display_name` supports interfaces and is never a legal or evidentiary name.

Legal/former names, headquarters and locations, capacities, power availability, project and construction dates/status, customer and lease terms, financial values, ownership percentages, operating characteristics, and every other sourced attribute are forbidden from entity records and represented exclusively as Facts. `additionalProperties: false` enforces this boundary across all entity schemas.

## Source Registry contract

Source IDs are permanent human-readable identifiers; entity and relationship IDs use the shared UUID definition. `source_url` is the original evidence location. `storage_location` and `external_file_id` identify an immutable external archive object. The Source JSONL record is repository metadata, not the evidence bytes.

External-object metadata records provider, original filename, media type, byte size, digest algorithm/value, archive time, archive access state, copyright, and restrictions. When `storage_provider` is `none`, every archive-specific field is null. Any external provider requires the complete archive metadata set and an algorithm-matched digest. Superseded Sources require reciprocal, resolvable, acyclic replacement links.

## Fact contract

A Fact documents one assertion. `entity_type` and `entity_id` form a typed foreign key. `field_name` supplies stable semantics; `value_type` selects exactly one permitted representation for `observed_value`; and `unit` supplies quantitative interpretation. Supported types are number, integer, text, Boolean, ISO date, ISO date-time, and structured JSON object. Null values are invalid.

Numbers and integers require units. Use `unitless` for counts and dimensionless ratios, `decimal_fraction` for ratios from 0 to 1, and `percent` for percentage points. Text, Boolean, date, date-time, and structured values use null units. A future field catalog will constrain field/type/unit combinations without changing this value envelope.

`observation_date` records when evidence first disclosed the value; `effective_date` records when it applied in the real world. `source_ids` provides immutable evidence provenance.

Production, review, and lifecycle are independent:

| Field | Allowed values | Mutability |
| --- | --- | --- |
| `value_classification` | observed, estimated, derived | Immutable |
| `verification_status` | pending_review, verified, disputed | Administrative update allowed |
| `lifecycle_status` | active, superseded, deprecated | Administrative update allowed |

Derived Facts require immutable `input_fact_ids` and `derivation_method`. Estimated Facts require immutable `estimation_method` and `estimation_assumptions`. Other classifications prohibit those production-specific fields.

Immutable fields are ID/schema/creation metadata, sources, subject, field, value type/value/unit, observation/effective dates, production classification, derivation metadata, and estimation metadata. Administrative updates may change verification, lifecycle, confidence, review notes, reciprocal supersession references, and `modified_at`. A corrected assertion creates a new Fact.

## Naming and evolution

Use singular entity names and plural arrays. Foreign keys end in `_id` or `_ids`. Dates end in `_date`; timestamps end in `_at`. Monetary Facts must use an explicit currency unit and document nominal/real and as-of semantics in the field definition or future field catalog.

New optional fields are normally backward-compatible. New required fields, changed meanings, narrowed enumerations, or altered units require a schema-version change and migration guidance. During pre-1.0 releases, breaking changes remain possible but must be documented. Historical Sources and Facts are never deleted.
