# Changelog

All notable changes are documented here. This project follows [Semantic Versioning](https://semver.org/) and the structure of [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added

- Evidence Acquisition and Knowledge Acceptance Architecture defining the constitutional repository boundary from external evidence through governed Facts.
- Conceptual Acquisition Record, Observed Assertion, Candidate Fact, and Acceptance Decision governance objects.
- Explicit admission lifecycle, independent validation layers, review and rejection governance, provenance continuity, and source-agnostic failure treatment.

### Changed

- README now identifies repository admission as a distinct architectural layer governed by the Architecture Constitution.

## [0.3.1] - 2026-07-30

### Added

- Architecture Constitution defining the repository's enduring layers, foundational principles, Fact and Field constitutions, validation philosophy, evolution rules, and release governance.

### Changed

- README now identifies the Architecture Constitution as the primary architectural authority.

## [0.3.0] - 2026-07-29

### Added

- First-class Field Registry with permanent `FIELD-NNNNNN` identifiers and governed canonical names.
- Synthetic definitions covering all Fact value types, units, shared applicability, relationships, calculations, history, and deprecation.
- Deterministic semantic validation for entity applicability, value type, units, classification, verification, cardinality, active-Fact multiplicity, and Field replacement graphs.
- Field governance, naming, category, lifecycle, and deprecation documentation.

### Changed

- Facts now reference immutable `field_id` values instead of free-form field-name strings.
- Validation now distinguishes structural, semantic, provenance, and lifecycle validity.
- Expanded tests for Field identity, naming, references, semantic constraints, cardinality, deprecation, replacement integrity, and rename stability.

## [0.2.0] - 2026-07-29

### Added

- Canonical Source Registry supporting 18 evidence types and provider-neutral external archive metadata, including Google Drive object identifiers and integrity fields.
- Atomic Fact schema with an explicit value-type discriminator, typed entity links, observation/effective dates, confidence, provenance, estimation, derivation, and historical supersession.
- Independent controlled vocabularies for Fact value classification, verification status, and lifecycle status.
- Repository-wide validation for duplicate identifiers, broken provenance and entity links, quantitative units, reciprocal supersession, and circular supersession or derivation graphs.
- Positive and negative evidence architecture tests.

### Changed

- Replaced the preliminary Source Document contract with the Version 0.2.0 Source Registry contract; no canonical data migration is required because the repository contains no records.
- Expanded the data dictionary and architecture documentation to separate evidence, Facts, derived information, analysis, and conclusions.
- Restricted entity schemas to structural identity, graph edges, non-authoritative display labels, and repository administration; sourced attributes exist exclusively as Facts.
- Replaced the former combined Fact status model and documented its conceptual mapping; no migration tool is needed because no production records exist.
- Tightened external archive and Source supersession consistency and added immutable Fact revision checks.

## [0.1.0] - 2026-07-28

### Added

- Initial multi-company repository architecture.
- JSON Schemas for companies, campuses, projects, leases, power assets, customers, financing, construction milestones, source documents, and market assumptions.
- Shared provenance, confidence, lifecycle, and audit metadata definitions.
- Data dictionary, assumptions policy, source-reference convention, and architecture documentation.
- Repository and fixture validation scripts with automated tests.

[Unreleased]: https://github.com/dml362/ai-infrastructure-digital-twin/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/dml362/ai-infrastructure-digital-twin/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/dml362/ai-infrastructure-digital-twin/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/dml362/ai-infrastructure-digital-twin/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/dml362/ai-infrastructure-digital-twin/releases/tag/v0.1.0
