# AI Infrastructure Digital Twin

Version 0.2.0 adds the permanent evidence layer for a long-lived, multi-company digital representation of AI infrastructure. The repository is an engineering database: immutable external evidence is registered, atomic Facts cite that evidence, and derived information identifies its input Facts. Valuation models and company data remain outside this release.

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
| `data/` | Validated canonical records; intentionally empty in v0.2.0 |
| `schemas/` | JSON Schema contracts and reusable definitions |
| `sources/` | Source registry and future immutable source manifests |
| `models/` | Future reproducible transformations; not valuation models |
| `scripts/` | Validation and maintenance utilities |
| `tests/` | Automated tests and schema fixtures |
| `outputs/` | Generated, disposable artifacts; canonical data never lives here |
| `archive/` | Superseded material retained for audit history |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for entity relationships, [docs/EVIDENCE_ARCHITECTURE.md](docs/EVIDENCE_ARCHITECTURE.md) for the evidence-to-conclusion layers, [docs/FACT_LIFECYCLE.md](docs/FACT_LIFECYCLE.md) for controlled transitions, and [docs/SOURCE_REFERENCE.md](docs/SOURCE_REFERENCE.md) for provenance rules.

## Data philosophy

Canonical Facts are atomic objects outside typed entity records; entity tables do not embed asserted values. Relationships use IDs rather than copied records. Each Fact has observation and effective dates, lifecycle status, confidence, notes, and Source references. A Source establishes provenance, while confidence expresses evidentiary strength; neither substitutes for the other.

Raw source documents must not be modified after registration and binary evidence must not be committed to GitHub. Corrections create new Source and Fact records with reciprocal supersession links. Derived values reference input Fact IDs and document their reproducible formula or transformation.

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
