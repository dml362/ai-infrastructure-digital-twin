# Source Reference System

Every canonical entity must include at least one `source_ids` entry resolving to a Source Document record.

## Format

Human-assigned source IDs use:

```text
SOURCE-{TYPE}-{PERIOD}-{SEQUENCE}
```

- `TYPE`: controlled uppercase source class such as `SEC`, `EARNINGS`, `COMPANY`, `UTILITY`, `REGULATORY`, `NEWS`, or a publisher code such as `BLOOMBERG`.
- `PERIOD`: publication year (`2026`) or year and reporting period (`2026-Q2`).
- `SEQUENCE`: zero-padded sequence when multiple sources share type and period; it may be omitted for a uniquely named reporting event.

Examples: `SOURCE-SEC-2026-001`, `SOURCE-EARNINGS-2026-Q2`, `SOURCE-BLOOMBERG-2026-015`.

The source ID identifies the document, not a claim within it. Use `locator` for page, section, exhibit, timestamp, table, or paragraph. When a single record relies on different passages, create structured fact-level attribution in the future facts layer rather than inventing duplicate source documents.

## Registration workflow

1. Register document metadata and a canonical URL or archive path.
2. Record publisher, publication date, retrieval timestamp, document type, and content hash when a local copy is permitted.
3. Assign the evidence confidence level; downstream records may use a lower score if the claim is ambiguous.
4. Cite its ID from every entity supported by the document.
5. Never silently replace archived content; register a revision as a new source and link it in notes.

URLs are locators, not durable proof. Preserve permitted documents under a content-addressed archive or external document store and record a SHA-256 hash.
