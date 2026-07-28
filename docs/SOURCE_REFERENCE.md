# Source Reference System

Every canonical Fact must include at least one `source_ids` entry resolving to a Source Registry record. Structural entity records contain no asserted attributes and therefore carry no evidence references; their asserted attributes exist as Facts.

## Format

Human-assigned source IDs use:

```text
SOURCE-{TYPE}-{PERIOD}-{SEQUENCE}
```

- `TYPE`: controlled uppercase source class such as `SEC`, `EARNINGS`, `COMPANY`, `UTILITY`, `REGULATORY`, `NEWS`, or a publisher code such as `BLOOMBERG`.
- `PERIOD`: publication year (`2026`) or year and reporting period (`2026-Q2`).
- `SEQUENCE`: zero-padded sequence when multiple sources share type and period; it may be omitted for a uniquely named reporting event.

Examples: `SOURCE-SEC-2026-001`, `SOURCE-EARNINGS-2026-Q2`, `SOURCE-BLOOMBERG-2026-015`.

The Source ID identifies the evidence artifact, not a claim within it. Atomic claims are separate Fact records. A future fact-level evidence locator may identify the page, section, exhibit, timestamp, table, image region, or paragraph supporting an assertion without inventing duplicate Source records.

## Registration workflow

1. Register source metadata and the original authoritative `source_url`.
2. When permitted, archive immutable bytes externally and record provider, storage location, provider file ID, original filename, media type, size, archive timestamp, and cryptographic digest.
3. Assign the evidence confidence level; downstream Facts may use a lower score if the assertion is ambiguous.
4. Cite its ID from every Fact extracted from the document.
5. Never silently replace archived content; register a revision as a new Source and use reciprocal supersession fields.

When `storage_provider` is `none`, all archive fields—including archive access state—are null. Declaring any external provider requires a stable provider identifier, storage location, original filename, media type, byte size, algorithm-matched digest, archive timestamp, and archive access status. A superseded Source must identify its replacement; a non-superseded Source cannot carry an active replacement pointer. Self-links, broken links, non-reciprocal links, and cycles fail validation.

URLs are locators, not durable proof. Google Drive is the planned permanent archive, but the schema permits other external providers. GitHub stores only the metadata record and never the binary evidence. Direct archive integration is outside Version 0.2.0.
