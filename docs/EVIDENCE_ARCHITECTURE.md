# Evidence Architecture

Version 0.2.0 separates Evidence, Facts, Derived Information, Analysis, and Conclusions so every downstream statement can be traced to immutable evidence.

## Layers and concepts

- **Evidence** is an external artifact. The Source Registry stores its identity, provenance, rights, archive locator, and integrity metadata. Evidence bytes are never edited.
- **Field** is a governed semantic definition with a permanent ID. It defines what a Fact means and which types, units, subjects, classifications, review states, and cardinality are valid.
- **Fact** is one typed assertion governed by one Field and applied to one structural entity. It cites Evidence and is not embedded in the entity record.
- **Observation** is the act of extracting an assertion. `observation_date` records when it was first found; `effective_date` records when it applied in the world.
- **Estimate** is a Fact produced by documented inference. It retains `estimation_method` and `estimation_assumptions` in every review and lifecycle state.
- **Derived Value** is a deterministic Fact calculated from `input_fact_ids` using a reproducible `derivation_method`. Inputs and method remain immutable even after dispute, deprecation, or supersession.
- **Analysis** interprets Facts for a defined scenario in future versioned analytical code.
- **Conclusion** is a judgment based on Analysis and must never be represented as Evidence or silently promoted to a Fact.

## Independent Fact dimensions

The former combined `status` field has been replaced because production method, review judgment, and lifecycle are orthogonal:

| Field | Values | Meaning |
| --- | --- | --- |
| `value_classification` | `observed`, `estimated`, `derived` | Immutable description of how the value was produced |
| `verification_status` | `pending_review`, `verified`, `disputed` | Current review judgment; may change administratively |
| `lifecycle_status` | `active`, `superseded`, `deprecated` | Current administrative availability; history is never deleted |

Valid combinations include observed/verified/active, estimated/pending_review/active, derived/verified/superseded, observed/disputed/active, and estimated/verified/deprecated. A disputed derived or estimated Fact keeps all original calculation or estimation metadata.

## Typed values and units

Every Fact declares exactly one `value_type`, but its Field determines which type is semantically permitted. Dates and timestamps use Draft 2020-12 format validation. Structured values are JSON objects. Null assertions are prohibited. Free-form field names are prohibited; Facts store only immutable Field IDs.

Numeric values always declare a unit permitted by their Field. Use `unitless` only when governed, `decimal_fraction` for ratios from 0 to 1, and `percent` for percentage points. Non-numeric Fields require null units.

## Traceability and storage boundaries

```text
External evidence -> Acquisition Record -> Source Registry -> Observed Assertion ----\
Supporting evidence -> Acquisition Record -> estimation method and assumptions ------> Candidate Fact
Accepted input Facts + Source provenance -> reproducible derivation method -----------/
                                                                                     -> Acceptance Decision
                                                                                     -> Atomic Fact <- Field Registry
                                                                                     -> Analysis -> Conclusion
```

The intermediate admission records preserve the difference between observed and accepted knowledge. Observation-backed, estimation-backed, and derivation-backed proposals all become Candidate Facts and pass through the same validation, review, and explicit acceptance boundary. Admission acceptance does not itself set a Fact's `verification_status` to `verified`. Their conceptual contracts are defined in the [Evidence Acquisition and Knowledge Acceptance Architecture](architecture/KNOWLEDGE_ADMISSION_ARCHITECTURE.md). They do not weaken or replace the Source, Field, Entity, or Fact contracts, and Version 0.4.0 does not implement an ingestion system.

`source_url` is the original evidence location. `storage_location` and `external_file_id` identify an immutable object held by an external `storage_provider`. The repository JSONL record is only metadata describing those locations and integrity checks. When `storage_provider` is `none`, every archive-specific field is null. When a provider is declared, object identity, filename, media type, size, digest, algorithm, archive time, and archive access status are mandatory and internally consistent.

Google Drive is allowed but not required. Version 0.2.0 contains no authentication, upload, synchronization, file movement, or binary evidence.

## Immutability

After creation, a Fact's ID, schema version, creation timestamp, sources, subject, field, value type, asserted value, unit, observation/effective dates, classification, derivation inputs/method, and estimation method/assumptions are immutable. Permitted administrative updates are `verification_status`, `lifecycle_status`, `confidence_score`, review `notes`, reciprocal supersession references, and `modified_at`.

Changing an assertion first creates a new candidate that completes the same production-neutral admission lifecycle as every other proposal. Only after acceptance may the repository create the replacement Fact and apply reciprocal supersession links and the prior Fact's lifecycle change as one coherent change. The validator exposes a revision-integrity check for future ingestion workflows, but the canonical repository validator cannot compare a record with an earlier Git revision automatically; enforcement across Git history remains a documented policy limitation.
