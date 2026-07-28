# Evidence Architecture

Version 0.2.0 separates the Digital Twin into layers so that a downstream conclusion can always be traced back to immutable evidence.

## The five layers

### Evidence

Evidence is an external artifact: a filing, presentation, recording, photograph, research paper, or other source. The Source Registry stores metadata and integrity information about that artifact. Evidence bytes are immutable. If a publisher revises a document, register the revision as a new Source rather than replacing the old object.

### Fact

A Fact is one atomic assertion extracted from evidence about one field on one entity. Facts are not embedded in Company, Campus, or other entity records. A Fact records what value was observed, where it applies, when it was observed, when it became effective, its unit, its present confidence, and the Source IDs supporting it.

### Derived Information

Derived information is a deterministic calculation from one or more Facts. It is stored as a Fact with status `derived`, non-empty `input_fact_ids`, and a reproducible `derivation_method`. Derived information never cites an unexplained total and never replaces its input Facts.

### Analysis

Analysis interprets Facts and derived information for a defined purpose or scenario. Analysis may compare alternatives, apply explicit assumptions, or identify uncertainty. It belongs in future versioned analytical code or outputs, not in Source or Fact records.

### Conclusion

A conclusion is a decision or judgment based on analysis. It must not be presented as evidence or silently promoted to a Fact. Future conclusion records should identify the analysis version and inputs that support them.

## Related concepts

An **observation** is the act of finding a value in evidence. `observation_date` records when this occurred; it is distinct from the real-world `effective_date`.

An **estimate** is a Fact whose value is inferred because direct observation is unavailable. It uses status `estimated`, records `estimation_method`, and retains evidence and confidence like any other Fact.

An **observed value** is the literal structured value asserted by a Fact. The name does not mean the value is verified; status and confidence communicate review quality.

## Traceability chain

```text
External evidence bytes
        │ hash + external_file_id
        ▼
Source Registry record
        │ source_ids
        ▼
Atomic Fact
        │ input_fact_ids
        ▼
Derived information
        │ versioned inputs and methods
        ▼
Analysis → Conclusion
```

This chain answers: where a number originated, when it was first observed, what it applies to, whether it changed, what replaced it, and what confidence is assigned today.

## External archive boundary

GitHub is the system of record for schemas, Source Registry metadata, Facts, validation, documentation, tests, and analytical logic. Large or binary evidence must not be committed.

- `source_url` is the original authoritative location from which evidence was obtained.
- `storage_location` and `external_file_id` identify an immutable archived object held by `storage_provider`.
- The Source Registry JSONL record is repository metadata describing and verifying those locations; it is not the document itself.

Google Drive is the planned permanent archive and is an allowed provider. The contract remains provider-neutral so other controlled object stores can be introduced without changing the evidence model. Version 0.2.0 does not authenticate, upload, synchronize, or move Google Drive files.

## Immutability and correction

Source evidence is never edited in place. Facts are append-only historical assertions: `observed_value`, subject, field, and observation date are never overwritten to reflect a later disclosure. A correction creates a new Fact. The old Fact becomes `superseded`, its `superseded_by_fact_id` points to the new Fact, and the new Fact lists the old ID in `supersedes_fact_ids`.

Metadata such as confidence, review notes, status, and `modified_at` may change through controlled review. Those lifecycle updates must not erase the original assertion or provenance.
