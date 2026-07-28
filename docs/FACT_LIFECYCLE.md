# Source and Fact Lifecycle

## Source ingestion workflow

```text
Source arrives
    ↓
Registered in Source Registry
    ↓
Evidence identity, rights, hash, and access reviewed
    ↓
Atomic Facts extracted
    ↓
Schema, provenance, uniqueness, and relationship validation
    ↓
Facts created and linked to canonical entities
    ↓
Available to downstream transformations and analysis
```

Registration assigns a permanent Source ID and captures the original URL separately from any external archive. Review confirms source type, reliability, copyright, access, and—when bytes are archived—the provider object ID, size, media type, timestamp, and cryptographic digest.

## Fact statuses

| Status | Meaning | Typical next states |
| --- | --- | --- |
| `pending_review` | Extracted assertion awaiting evidence and field review | observed, verified, estimated, disputed |
| `observed` | Directly transcribed from evidence but not independently verified | verified, disputed, superseded, deprecated |
| `verified` | Reviewed and supported under the confidence policy | disputed, superseded, deprecated |
| `estimated` | Inferred using a documented estimation method | verified, disputed, superseded, deprecated |
| `derived` | Reproducibly calculated from `input_fact_ids` | disputed, superseded, deprecated |
| `disputed` | Conflicting evidence or interpretation is unresolved | verified, superseded, deprecated |
| `deprecated` | Retained historically but no longer recommended for use | none, except a documented correction |
| `superseded` | Replaced by a newer Fact linked in both directions | none |

Status transitions are review events, not deletion instructions. Unknown statuses fail schema validation. `superseded` requires `superseded_by_fact_id`, and relationship validation requires the new Fact to reciprocally list the old Fact.

## Historical change example

When a later SEC filing changes a disclosed value:

1. Register the later filing as a new Source.
2. Create a new Fact citing that Source.
3. Set the prior Fact to `superseded` and point `superseded_by_fact_id` to the new Fact.
4. Add the prior Fact ID to the new Fact's `supersedes_fact_ids`.
5. Preserve both Facts and both Sources.

The current value is selected through lifecycle status and effective dates. The historical value never disappears.

## Validation guarantees

Repository validation rejects duplicate Fact or Source IDs, missing or broken provenance, invalid statuses, missing quantitative units, broken entity links, broken calculation inputs, non-reciprocal supersession, and circular Fact or Source supersession chains.
