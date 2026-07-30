# AI Infrastructure Digital Twin

Version 0.4.0 defines how external evidence may cross the repository boundary and become governed knowledge. Acquisition, observation, candidate interpretation, validation, review, acceptance, and rejection remain explicit and auditable; no ingestion implementation or repository population is included.

## Design principles

- **Traceable:** every asserted Fact cites one or more Source Registry IDs.
- **Normalized:** entities are stored once and connected with stable IDs.
- **Reproducible:** derived values identify their inputs and calculation method.
- **Semantically governed:** every Fact resolves an immutable Field ID that governs meaning, type, units, applicability, and cardinality.
- **Time-aware:** facts retain effective dates and source publication dates.
- **Scalable:** newline-delimited JSON can be partitioned by entity, company, and year without changing schemas.
- **Conservative:** unknown values remain `null` or absent; they are never silently replaced with zero.

## Repository organization

| Path | Purpose |
| --- | --- |
| `docs/` | Architecture decisions, conventions, and operating guidance |
| `data/` | Validated canonical records; v0.3.0 contains only the synthetic Field Registry |
| `schemas/` | JSON Schema contracts and reusable definitions |
| `sources/` | Source registry and future immutable source manifests |
| `models/` | Future reproducible transformations; not valuation models |
| `scripts/` | Validation and maintenance utilities |
| `tests/` | Automated tests and schema fixtures |
| `outputs/` | Generated, disposable artifacts; canonical data never lives here |
| `archive/` | Superseded material retained for audit history |

The [Architecture Constitution](docs/architecture/ARCHITECTURE_CONSTITUTION.md) is the repository's primary architectural reference. The [Evidence Acquisition and Knowledge Acceptance Architecture](docs/architecture/KNOWLEDGE_ADMISSION_ARCHITECTURE.md) governs repository admission. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for relationships, [docs/FIELD_REGISTRY.md](docs/FIELD_REGISTRY.md) for semantic governance, [docs/EVIDENCE_ARCHITECTURE.md](docs/EVIDENCE_ARCHITECTURE.md) for evidence layers, [docs/FACT_LIFECYCLE.md](docs/FACT_LIFECYCLE.md) for transitions, and [docs/SOURCE_REFERENCE.md](docs/SOURCE_REFERENCE.md) for provenance.

## Data philosophy

Canonical Facts are atomic objects outside typed entity records; entity tables do not embed asserted values. Entity records contain only UUID identity, a machine key, a non-authoritative display label, structural graph edges, and repository-administration metadata. Legal names, locations, capacity, power, dates, operating state, customer relationships, lease terms, financial values, ownership, and all other sourced attributes exist exclusively as Facts.

Every Fact stores an immutable `field_id`, never a free-form field-name string. The Field Registry governs the canonical name, display label, applicable entity types, value type, units, production/review permissions, cardinality, and lifecycle policy. Renaming Field metadata never changes historical Facts.

Every Fact also separates `value_classification` (observed, estimated, derived), `verification_status` (pending review, verified, disputed), and `lifecycle_status` (active, superseded, deprecated). A Source establishes provenance, while a Field establishes meaning; neither substitutes for the other.

Raw source documents must not be modified after registration and binary evidence must not be committed to GitHub. Corrections create new Source and Fact records with reciprocal supersession links. Derived values reference input Fact IDs and document their reproducible formula or transformation.

`display_name` is only a navigation label. It must never be treated as a legal name or copied into analysis as an authoritative value. See [docs/SCHEMA_EXAMPLES.md](docs/SCHEMA_EXAMPLES.md) for synthetic structural and Fact examples.

## Versioning philosophy

The repository follows [Semantic Versioning](https://semver.org/):

- MAJOR: incompatible schema or data-contract changes.
- MINOR: backward-compatible entities, fields, or capabilities.
- PATCH: backward-compatible corrections and documentation improvements.

Schema files expose their own `schema_version`. Repository releases are tagged `vMAJOR.MINOR.PATCH`. During `0.x`, breaking changes may occur in minor releases but must be documented and accompanied by migration guidance.

## Contribution workflow

1. Create a focused branch from the default branch.
2. Add or update a source record before adding facts derived from it.
3. Update schemas and the data dictionary when fields change.
4. Run `python scripts/validate_repository.py` and `python -m unittest discover tests`.
5. Record user-visible changes under `Unreleased` in `CHANGELOG.md`.
6. Open a pull request describing provenance, schema impact, and validation results.

Never commit credentials, licensed documents without permission, generated outputs, or untraceable facts.
