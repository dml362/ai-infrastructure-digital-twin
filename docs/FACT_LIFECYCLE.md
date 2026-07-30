# Source and Fact Lifecycle

## Evidence admission

```text
Observation-backed: acquired evidence -> Acquisition Record -> Source -> Observed Assertion --------\
Estimation-backed: supporting evidence or Facts -> estimation method + assumptions -----------------> Candidate Fact
Derivation-backed: accepted input Facts -> reproducible derivation method ---------------------------/
                                                                                                     -> Validation
                                                                                                     -> Review
                                                                                                     -> one terminal decision
                                                                                                          | accepted
                                                                                                          v
                                                                                                     Repository Acceptance
                                                                                                     -> Governed Fact

Rejected terminal decision -------------------------------------------------------------------------> retained admission history
```

The [Evidence Acquisition and Knowledge Acceptance Architecture](architecture/KNOWLEDGE_ADMISSION_ARCHITECTURE.md) governs this boundary. Registration assigns a permanent Source ID, but neither registration, extraction, estimation, derivation, nor validation alone creates repository knowledge. Observation-backed, estimation-backed, and derivation-backed proposals all become Candidate Facts and use the same validation, review, and explicit acceptance boundary. Acceptance does not automatically set `verification_status` to `verified`. Rejected and revised candidates remain admission history rather than canonical Facts, and each immutable candidate version has exactly one terminal acceptance or rejection decision.

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
2. Create a new observation-backed, estimation-backed, or derivation-backed Candidate Fact citing the appropriate Source evidence and retaining all required production metadata.
3. Run the candidate through complete validation and review and record its unique terminal Acceptance Decision.
4. Only after acceptance, create the replacement Fact and apply its `supersedes_fact_ids`, the old Fact's `superseded_by_fact_id`, the old Fact's `lifecycle_status` change, and required administrative timestamps as one coherent repository change.
5. Preserve both Facts, both Sources, immutable provenance and production metadata, every candidate version, and every decision record.

A rejected replacement candidate does not alter the existing Fact. Revising or reconsidering a replacement creates a new candidate version linked to the prior candidate and its terminal decision; it never overwrites the prior version or adds a competing decision to it.

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
