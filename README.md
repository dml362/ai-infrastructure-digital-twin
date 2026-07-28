# AI Infrastructure Digital Twin

Version 0.1.0 establishes the data architecture for a long-lived, multi-company digital representation of AI infrastructure. The repository is an engineering database: it captures physical assets, commercial agreements, financing, construction, sources, and assumptions in auditable structured records. Valuation models and company data are intentionally outside this release.

## Design principles

- **Traceable:** every record cites one or more source-document IDs.
- **Normalized:** entities are stored once and connected with stable IDs.
- **Reproducible:** derived values identify their inputs and calculation method.
- **Time-aware:** facts retain effective dates and source publication dates.
- **Scalable:** newline-delimited JSON can be partitioned by entity, company, and year without changing schemas.
- **Conservative:** unknown values remain `null` or absent; they are never silently replaced with zero.

## Repository organization

| Path | Purpose |
| --- | --- |
| `docs/` | Architecture decisions, conventions, and operating guidance |
| `data/` | Validated canonical records; empty in v0.1.0 |
| `schemas/` | JSON Schema contracts and reusable definitions |
| `sources/` | Source registry and future immutable source manifests |
| `models/` | Future reproducible transformations; not valuation models |
| `scripts/` | Validation and maintenance utilities |
| `tests/` | Automated tests and schema fixtures |
| `outputs/` | Generated, disposable artifacts; canonical data never lives here |
| `archive/` | Superseded material retained for audit history |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for entity relationships and storage conventions and [docs/SOURCE_REFERENCE.md](docs/SOURCE_REFERENCE.md) for provenance rules.

## Data philosophy

Canonical facts belong in typed entity records, not prose or spreadsheets. Relationships use IDs rather than embedded copies. Each record has creation and modification timestamps, lifecycle status, confidence, notes, and source references. A source establishes provenance, while confidence expresses evidentiary strength; neither substitutes for the other.

Raw source documents should not be modified after registration. Corrections create a new record version or supersede a record with an explicit audit trail. Derived values must reference underlying record IDs and document their formula or transformation in code.

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
