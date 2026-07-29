# Source and Fact Lifecycle

## Evidence ingestion

```text
Source arrives -> Registered -> Reviewed -> Facts extracted -> Validated
               -> Fact created -> Linked to entity -> Available downstream
```

Registration assigns a permanent Source ID. Fact creation also selects a governed Field ID; semantic validation must pass before the Fact is available downstream.

## Fact state transitions

Production classification never transitions: `observed`, `estimated`, or `derived` describes how the immutable assertion was made. Review may move between `pending_review`, `verified`, and `disputed`. Lifecycle normally moves from `active` to `superseded` or `deprecated`; records are never deleted.

Examples:

- observed + verified + active
- estimated + pending_review + active
- derived + verified + superseded
- observed + disputed + active
- estimated + verified + deprecated

Dispute affects review judgment only. It does not erase the value, evidence, derivation, or estimation metadata. Deprecation preserves the same production history. Supersession requires `superseded_by_fact_id`; the replacement reciprocally lists the old ID in `supersedes_fact_ids`, and both records remain queryable.

## Correction workflow

When later evidence changes an assertion:

1. Register the later evidence as a new Source.
2. Create a new Fact citing that Source.
3. Change only the old Fact's administrative lifecycle to `superseded`, set its replacement link, and update `modified_at`.
4. Add the old ID to the new Fact's `supersedes_fact_ids`.
5. Preserve both Facts, their immutable production metadata, and both Sources.

## Legacy conceptual mapping

No production data exists and no migration utility is required. The former combined status concepts map as follows:

| Former status | New dimensions |
| --- | --- |
| `observed` | observed / pending_review or verified / active |
| `verified` | observed / verified / active |
| `estimated` | estimated / pending_review or verified / active |
| `derived` | derived / pending_review or verified / active |
| `disputed` | preserve original classification / disputed / active |
| `superseded` | preserve original classification and verification / superseded |
| `deprecated` | preserve original classification and verification / deprecated |
| `pending_review` | preserve original classification / pending_review / active |

A legacy lifecycle or review label cannot determine how a value was produced. If original classification is unknown, a reviewer must inspect the evidence; it must not be guessed.

## Validation guarantees and limitation

Validation rejects unknown state values, contradictory production metadata, missing numeric units, broken provenance, duplicate IDs, broken typed entity links, non-reciprocal supersession, and circular Fact, Source, or derivation chains. The revision-integrity helper rejects changes to immutable fields when supplied prior and revised records. Standard repository validation sees only the current checkout and therefore cannot independently compare all historical Git versions.

Field lifecycle is independent from Fact lifecycle. Deprecating a Field prevents new active Facts but does not invalidate historical deprecated or superseded Facts. A deprecated Field points to a replacement Field; Facts are never rewritten to the replacement ID.
