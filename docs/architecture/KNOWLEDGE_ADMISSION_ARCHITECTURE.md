# Evidence Acquisition and Knowledge Acceptance Architecture

## 1. Architectural question

External evidence becomes accepted repository knowledge through an explicit, reviewable admission boundary. Evidence is first brought under repository control without being treated as truth. Its assertions are then observed, mapped into candidate knowledge, validated against every applicable repository contract, reviewed, and either accepted as new governed Facts or rejected with the full attempt retained. Acceptance is a distinct architectural event; extraction, parsing, and structural validity never imply acceptance.

This architecture defines the contract for admission, not an ingestion implementation. It is subordinate to the [Architecture Constitution](ARCHITECTURE_CONSTITUTION.md).

## 2. Repository boundary

```text
External World
    -> Evidence Acquisition
    -> Candidate Knowledge
    -> Repository Acceptance
    -> Governed Repository Facts
```

The **External World** contains documents, recordings, images, statements, feeds, and manual observations that the repository does not control. Their existence alone creates no repository knowledge.

**Evidence Acquisition** begins when an external artifact or observation is assigned an acquisition identity and its origin, time, method, and integrity context are recorded under repository control. Governance begins at this point. The acquired material is evidence, not an accepted assertion, and must remain distinguishable from any interpretation of it.

**Candidate Knowledge** contains proposed interpretations of acquired evidence. Candidate records may be incomplete, invalid, disputed, rejected, revised, or reconsidered. They are never canonical Facts and must not be consumed as though acceptance had occurred.

**Repository Acceptance** is the controlled decision boundary. Every applicable structural, semantic, provenance, lifecycle, and admission requirement must succeed, and an accountable review decision must authorize admission.

**Governed Repository Facts** are created only after acceptance. From that event onward, the existing Fact, Field, Source, Entity, provenance, lifecycle, and append-only contracts apply without exception. The admission history remains linked to the accepted Fact.

Constitutional guarantees are mandatory for every record created under repository control, including unsuccessful acquisition and rejected candidate history. The guarantees become stricter, not weaker, as information advances toward canonical knowledge.

## 3. Knowledge admission lifecycle

| Stage | Responsibility | Inputs | Outputs | Ownership | Transition requirement |
| --- | --- | --- | --- | --- | --- |
| External Evidence | Preserve the distinction between the world and the repository | Artifact, communication, or manual observation outside repository control | Identified acquisition target | External custodian | A deliberate acquisition attempt is authorized |
| Acquired Evidence | Record what entered repository control without interpreting it as truth | External evidence and acquisition context | Acquisition Record and registered or proposed Source evidence | Evidence stewardship | Identity, origin, timestamp, method, integrity context, and access state are recorded |
| Observed Assertions | Preserve what an observer or extraction process found in the evidence | Acquired evidence and bounded extraction context | One or more Observed Assertions | Evidence interpretation | Each assertion points to exact evidence and extraction context; no semantic acceptance is implied |
| Candidate Facts | Express an observed, estimated, or derived assertion in the repository's proposed semantic form | Observed Assertion or documented estimation or derivation basis; proposed Entity, Field, typed value, unit, and provenance | Candidate Fact | Semantic stewardship | Production method and its required metadata are explicit, and the proposal is complete enough to validate |
| Validation | Evaluate independent admission dimensions deterministically | Candidate Fact and the repository state against which it is proposed | Validation outcome for every layer | Repository validation authority | Every required layer records pass or failure; no layer is inferred from another |
| Review | Apply accountable human governance after deterministic checks | Candidate, evidence, mappings, validation outcomes, and prior decisions | Review record and recommendation | Authorized reviewer | Reviewer identity, time, rationale, and considered evidence are retained |
| Acceptance or Rejection | Make an explicit admission decision | Complete review package | Immutable Acceptance Decision | Repository steward | Acceptance requires all gates to pass; rejection records reason codes and rationale |
| Accepted Facts | Create canonical knowledge using existing contracts | Accepted candidate and decision | New governed Fact linked to its admission history | Canonical repository | Fact identity is assigned once; provenance and semantic references resolve |
| Historical Repository | Preserve the complete chronology | Acquisition, interpretation, validation, review, decision, and Fact records | Auditable repository history | Repository governance | Changes occur through new records and explicit relationships, never silent overwrite |

Transitions are monotonic historical events. A later stage may refer back to an earlier stage, but it cannot rewrite what that earlier stage recorded.

### Production-neutral admission paths

The admission boundary governs all three Fact production methods. They differ only in the production context that must be preserved before they converge as Candidate Facts:

```text
Acquired evidence -> Observed Assertion -----------------------> Candidate Fact
Acquired evidence + documented method and assumptions --------> Candidate Fact
Accepted input Facts + reproducible derivation method ---------> Candidate Fact
                                                               -> Validation
                                                               -> Review
                                                               -> Acceptance Decision
                                                               -> Governed Fact
```

- An **observation-backed proposal** preserves the acquired evidence, exact observation context, and observation time.
- An **estimation-backed proposal** preserves supporting evidence, the estimation method, and all assumptions. It need not pretend that an estimate was directly observed.
- A **derivation-backed proposal** preserves its accepted input Fact IDs and reproducible derivation method, together with the provenance already retained by those inputs and any additional supporting Source references.

Every path uses the same structural, semantic, provenance, lifecycle, constitutional, review, and acceptance gates. Estimated and derived production metadata is part of the candidate and remains immutable in the accepted Fact. No calculation, inference, successful extraction, or pre-existing input Fact may bypass repository acceptance.

## 4. Candidate knowledge model

Version 0.4.0 recognizes four conceptual governed object types. It intentionally does not add their JSON Schemas or runtime behavior.

### Acquisition Record

An Acquisition Record identifies one attempt to bring evidence under repository control. Its permanent identity binds the external origin, acquisition timestamp, acquisition method, evidence identity or fingerprint, custody context, and outcome. A failed acquisition remains a valid historical record of the attempt.

### Observed Assertion

An Observed Assertion records what was found and where it was found before the repository assigns governed semantic meaning. It retains the acquisition reference, evidence locator, extraction context, observation time, observer identity or process identity, and the assertion as observed. It does not reference a conclusion and is not a Fact.

### Candidate Fact

A Candidate Fact is a proposed mapping of an observation, documented estimate, or reproducible derivation to an existing Entity and Field, with a proposed typed value, unit, classification, dates, Source provenance, and production metadata appropriate to its production method. Candidate identity is permanent within admission history, but candidate status is not canonical truth. Corrections create a new candidate version linked to the prior proposal; they do not mutate the original attempt.

### Acceptance Decision

An Acceptance Decision is an immutable record that accepts or rejects one specific immutable candidate version against one identifiable repository state. It preserves validation outcomes, reviewer history, decision time, rationale, and any accepted Fact ID. Each candidate version has exactly one terminal Acceptance Decision; acceptance and rejection cannot compete for the same version. Reconsideration creates a new candidate version linked to both the prior candidate and its terminal decision, then subjects that new version to a new validation, review, and decision path.

These admission objects are first-class governance records but not canonical domain knowledge. Only the accepted Fact is available to downstream repository consumers. Future releases must define their identifiers, schemas, controlled vocabularies, and canonical storage before implementing ingestion.

## 5. Acceptance and review governance

Repository acceptance requires all of the following:

- the acquired evidence and its Source provenance are identifiable and resolvable;
- the proposed record is structurally valid;
- the Entity and Field exist and the Field applies to that Entity type;
- the proposed value type, unit, classification, verification state, and production metadata comply with Field governance;
- lifecycle and cross-record relationships are coherent;
- duplicate immutable identifiers and conflicting active cardinality are rejected;
- every applicable validation outcome is recorded against an identifiable repository state;
- an authorized reviewer makes an explicit acceptance decision with rationale.

Parsing or extraction success establishes only that a process produced output. Structural validity establishes only that the output has an allowed shape. Neither is evidence of semantic correctness, adequate provenance, or approval.

Review may accept or reject a candidate, request a revised proposal, or identify insufficient evidence. Revision creates a new candidate linked to its predecessor. Rejection is permanent for the reviewed candidate version and remains auditable. Reconsideration never changes the old decision and never creates a second decision for the old candidate; it creates a new candidate version that cites the prior candidate and terminal decision before beginning a new review path.

Admission acceptance and Fact verification answer different questions. Acceptance authorizes a candidate to enter the canonical repository; `verification_status` records the repository's review judgment about the resulting assertion. Acceptance does not automatically set `verification_status` to `verified`. The accepted Fact retains the candidate's independently valid verification state, which may be `pending_review`, `verified`, or `disputed` when permitted by its Field and the existing Fact contract.

If accepted knowledge later proves wrong, its replacement begins as a new observation-backed, estimation-backed, or derivation-backed candidate and completes the entire admission lifecycle. Only after that replacement candidate has passed validation and review and received its unique acceptance decision may the repository apply the accepted replacement Fact, reciprocal supersession references, and the prior Fact's lifecycle change as one coherent repository change. The old Fact, its immutable provenance and production metadata, the replacement candidate, all decisions, and every prior candidate version remain preserved.

## 6. Provenance continuity

The provenance chain is continuous and directional:

```text
Observation-backed: acquired evidence -> Acquisition Record -> Source -> Observed Assertion --------\
Estimation-backed: supporting evidence or Facts -> estimation method + assumptions -----------------> Candidate Fact
Derivation-backed: accepted input Facts -> reproducible derivation method ---------------------------/
                                                                                                     -> validation outcomes
                                                                                                     -> review history
                                                                                                     -> one terminal decision
                                                                                                          | accepted
                                                                                                          v
                                                                                                     Repository Acceptance
                                                                                                     -> governed Fact

Rejected terminal decision -------------------------------------------------------------------------> retained admission history
```

Every transition adds context; none discards prior context. The chain preserves the original source location, acquisition timestamp and method, evidence identity or cryptographic integrity information where available, the exact extraction context, observer or process attribution, mappings considered, validation outcomes, reviewer actions, decision rationale, and the accepted Fact identity.

External evidence bytes may remain in provider-neutral external storage under the Source Registry contract. Their storage location is distinct from the original source URL and from repository metadata. Admission records refer to immutable evidence identity; moving an archive object must not change the meaning or identity of the historical acquisition.

## 7. Validation architecture

Validation layers remain independent so failures are precise and explainable:

| Layer | Architectural purpose |
| --- | --- |
| Acquisition validation | Establishes that evidence identity, origin, custody, acquisition time, method, and integrity context are sufficient to audit what entered repository control |
| Structural validation | Establishes that each proposed record conforms to its declared machine-readable contract |
| Semantic validation | Establishes that the Field exists and permits the Entity type, value type, unit, classification, verification state, production method, and cardinality |
| Provenance validation | Establishes that Source and evidence references resolve and that the chain from assertion to acquired evidence is complete |
| Lifecycle validation | Establishes that revisions, supersession, derivation, estimation, and historical links are coherent and acyclic |
| Constitutional validation | Establishes that the admission path preserves immutable identity, append-only history, evidence before interpretation, reproducibility, and repository-first authority |
| Acceptance validation | Establishes that all applicable outcomes and accountable review approval exist for the exact candidate and repository state being admitted, and that the candidate version has exactly one terminal decision |

A candidate may pass one layer and fail another. Every outcome is retained independently. Deterministic layers operate only on explicit inputs and an identifiable repository state; they do not depend on network availability, hidden state, processing order, or undocumented judgment. Human review is explicit governance data, not concealed validator behavior.

## 8. Failure philosophy

Failure prevents admission but does not erase history.

| Failure | Meaning | Required historical treatment |
| --- | --- | --- |
| Acquisition failure | Evidence could not be brought under repository control or verified as intended | Retain the attempt, method, time, target, and failure reason |
| Parsing failure | Evidence could not be represented by the attempted interpretation process | Retain the evidence reference, attempted process, context, and diagnostic outcome |
| Mapping failure | An assertion cannot be mapped unambiguously to an Entity, Field, type, or unit | Retain proposed mappings and explicit unresolved reasons |
| Semantic conflict | The proposal contradicts governed Field constraints or active cardinality | Retain the candidate and failed semantic outcomes; do not weaken the Field contract |
| Insufficient evidence | Provenance or evidentiary support cannot justify admission | Retain the candidate, available evidence, and insufficiency rationale |
| Validation failure | One or more deterministic gates fail | Retain each layer's outcome and prevent acceptance bypass |
| Reviewer rejection | An accountable reviewer declines admission despite a complete review package | Retain reviewer, time, rationale, evidence considered, and terminal decision |

Unknown Fields, unknown Entities, malformed Sources, invalid units, unsupported value types, and duplicate immutable identifiers are rejection conditions, not opportunities for silent coercion. No failed or rejected candidate is exposed as a repository Fact.

## 9. Constitutional preservation

- **Immutable identity:** every acquisition attempt, observation, candidate version, decision, Source, Field, Entity, and accepted Fact has a stable identity that is never reassigned.
- **Append-only history:** revision, reconsideration, rejection, acceptance, dispute, and supersession add records and relationships; they never overwrite prior events.
- **Evidence before interpretation:** an Acquisition Record and resolvable evidence identity precede Observed Assertions and Candidate Facts.
- **Provenance:** the complete path from external origin through acceptance remains navigable from the governed Fact.
- **Semantic governance:** candidates propose existing immutable Field IDs; admission cannot invent ungoverned field-name strings or bypass Field constraints.
- **Deterministic validation:** each applicable gate evaluates explicit records against an identifiable repository state and records its outcome independently.
- **Historical reproducibility:** evidence context, mappings, methods, assumptions, validation outcomes, reviews, and decisions remain available after acceptance or rejection.
- **Repository-first stewardship:** external tools may propose admission records, but only the version-controlled repository can establish canonical Fact acceptance.

## 10. Source-agnostic contract

The same boundary applies to SEC filings, earnings calls, regulatory filings, research papers, engineering specifications, X posts, Builder Brief, manually entered observations, and future unknown source types. Source-specific acquisition or interpretation may differ outside the repository, but it cannot alter the admission stages or reduce their requirements. A source's reputation may inform confidence and review; it cannot bypass provenance, semantic mapping, validation, or acceptance.

## 11. Future implementation boundary

Version 0.4.0 intentionally leaves the following to separately governed releases:

- machine-readable schemas and controlled vocabularies for admission records;
- canonical storage layout and repository-wide validation rules for those records;
- connector and synchronization frameworks;
- scraping, APIs, OCR, parsers, and LLM extraction;
- queues, scheduling, background workers, monitoring, and retry behavior;
- reviewer identity and authorization mechanisms;
- user interfaces or command-line tools for review and acceptance;
- external archive automation, including Google Drive integration;
- repository population, graph construction, search, analytics, dashboards, and valuation.

Future implementations plug into this architecture by producing governed admission records and submitting them through the same acceptance boundary. They may automate acquisition or interpretation, but they may not create canonical Facts directly or become an alternative system of record.
