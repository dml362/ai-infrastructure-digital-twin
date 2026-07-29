# Data Dictionary Standard

JSON Schemas in `schemas/` are the executable data dictionary. Every property must include a meaningful description of its scope, type, nullability, unit, relationship target, allowed interpretation, provenance role, constraints, and lifecycle semantics where applicable.

## Structural entity contract

Entity records are graph anchors, not evidence containers. They contain an immutable UUID, fixed `entity_type`, stable machine-readable `slug`, non-authoritative `display_name`, creation/modification timestamps, repository `record_status`, administrative notes, and only foreign keys needed to define graph topology. `display_name` supports interfaces and is never a legal or evidentiary name.

Legal/former names, headquarters and locations, capacities, power availability, project and construction dates/status, customer and lease terms, financial values, ownership percentages, operating characteristics, and every other sourced attribute are forbidden from entity records and represented exclusively as Facts. `additionalProperties: false` enforces this boundary across all entity schemas.

## Source Registry contract

Source IDs are permanent human-readable identifiers; entity and relationship IDs use the shared UUID definition. `source_url` is the original evidence location. `storage_location` and `external_file_id` identify an immutable external archive object. The Source JSONL record is repository metadata, not the evidence bytes.

External-object metadata records provider, original filename, media type, byte size, digest algorithm/value, archive time, archive access state, copyright, and restrictions. When `storage_provider` is `none`, every archive-specific field is null. Any external provider requires the complete archive metadata set and an algorithm-matched digest. Superseded Sources require reciprocal, resolvable, acyclic replacement links.

## Field Registry contract

Fields are first-class governed objects. `id` is an immutable `FIELD-NNNNNN` key referenced by Facts. `canonical_name` is governed lowercase dotted metadata; `display_label` is optional presentation metadata. Names may evolve, but IDs and historical Fact references do not.

Each definition documents applicable entity types, exact value type, allowed units and unitless behavior, classification and verification permissions, cardinality, temporal semantics, estimate/derivation permissions, confidence guidance, semantic categories, and deprecation replacement. Field definitions contain no company observations.

## Fact contract

A Fact documents one assertion. `entity_type` and `entity_id` identify its subject. `field_id` supplies governed semantics; free-form `field_name` is invalid. `value_type`, value, unit, classification, and verification must comply with the referenced Field. Null values are invalid.

Numbers and integers require a unit allowed by their Field. Use `unitless` only when the Field permits it, `decimal_fraction` for ratios from 0 to 1, and `percent` for percentage points. Non-numeric Fields require null units.

`observation_date` records when evidence first disclosed the value; `effective_date` records when it applied in the real world. `source_ids` provides immutable evidence provenance.

Production, review, and lifecycle are independent:

| Field | Allowed values | Mutability |
| --- | --- | --- |
| `value_classification` | observed, estimated, derived | Immutable |
| `verification_status` | pending_review, verified, disputed | Administrative update allowed |
| `lifecycle_status` | active, superseded, deprecated | Administrative update allowed |

Derived Facts require immutable `input_fact_ids` and `derivation_method`. Estimated Facts require immutable `estimation_method` and `estimation_assumptions`. Other classifications prohibit those production-specific fields.

Immutable fields are ID/schema/creation metadata, sources, subject, Field ID, value type/value/unit, observation/effective dates, production classification, derivation metadata, and estimation metadata. Administrative updates may change verification, lifecycle, confidence, review notes, reciprocal supersession references, and `modified_at`. A corrected assertion creates a new Fact.

## Governed-object principle

Every governed object has a permanent immutable identifier, a governed canonical name, and optional presentation metadata. Entity `slug`/`display_name`, Source `title`, and Field `canonical_name`/`display_label` implement equivalent vocabulary. Facts inherit their governed semantic name through immutable `field_id`; copying mutable Field names into Facts is prohibited. Future exceptions require explicit documentation.

## Naming and evolution

Use singular entity names and plural arrays. Foreign keys end in `_id` or `_ids`. Dates end in `_date`; timestamps end in `_at`. Monetary Facts use an explicit currency unit and document nominal/real and as-of semantics in the Field definition.

New optional fields are normally backward-compatible. New required fields, changed meanings, narrowed enumerations, or altered units require a schema-version change and migration guidance. During pre-1.0 releases, breaking changes remain possible but must be documented. Historical Sources and Facts are never deleted.
