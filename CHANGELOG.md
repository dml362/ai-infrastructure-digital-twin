# Changelog

All notable changes are documented here. This project follows [Semantic Versioning](https://semver.org/) and the structure of [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.2.0] - Unreleased

### Added

- Canonical Source Registry supporting 18 evidence types and provider-neutral external archive metadata, including Google Drive object identifiers and integrity fields.
- Atomic Fact schema with typed entity links, observation/effective dates, confidence, provenance, estimation, derivation, and historical supersession.
- Controlled Fact status vocabulary and documented Source-to-Fact ingestion lifecycle.
- Repository-wide validation for duplicate identifiers, broken provenance and entity links, quantitative units, reciprocal supersession, and circular supersession or derivation graphs.
- Positive and negative evidence architecture tests.

### Changed

- Replaced the preliminary Source Document contract with the Version 0.2.0 Source Registry contract; no canonical data migration is required because the repository contains no records.
- Expanded the data dictionary and architecture documentation to separate evidence, Facts, derived information, analysis, and conclusions.

## [0.1.0] - 2026-07-28

### Added

- Initial multi-company repository architecture.
- JSON Schemas for companies, campuses, projects, leases, power assets, customers, financing, construction milestones, source documents, and market assumptions.
- Shared provenance, confidence, lifecycle, and audit metadata definitions.
- Data dictionary, assumptions policy, source-reference convention, and architecture documentation.
- Repository and fixture validation scripts with automated tests.

[Unreleased]: https://github.com/dml362/ai-infrastructure-digital-twin/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/dml362/ai-infrastructure-digital-twin/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/dml362/ai-infrastructure-digital-twin/releases/tag/v0.1.0
