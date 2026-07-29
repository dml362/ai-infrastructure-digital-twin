# Field Registry

The Field Registry is the semantic contract for every Fact. Structural schema validation answers whether a Fact is well formed; the Field definition answers what it represents and whether that assertion is permitted.

## Identity and naming

Every Field has three deliberately separate names:

- `id` is the immutable `FIELD-NNNNNN` identifier stored by Facts. It is never renamed, reused, or reassigned.
- `canonical_name` is governed machine metadata used for discovery and human-readable queries. It may change through review without rewriting historical Facts.
- `display_label` is optional presentation metadata and carries no identity or validation authority.

Canonical names use lowercase dotted paths: `{namespace}.{concept}[.{subconcept}...]`. Namespace is an entity type or `shared`; segments begin with a letter and contain lowercase letters, digits, or underscores. Examples include `company.legal_name`, `campus.power.contracted_capacity`, and `project.construction.start_date`.

## Semantic contract

A Field governs applicable entity types, exact value type, allowed units, unitless behavior, permitted production classifications and verification states, cardinality, temporal interpretation, null policy, estimate/derivation permissions, active-Fact multiplicity, confidence guidance, semantic categories, and deprecation.

Categories mean:

| Category | Meaning |
| --- | --- |
| `identity` | Identifies or names the subject without defining its graph key |
| `operational` | Describes operating capacity, condition, or behavior |
| `relationship` | Represents a sourced association between governed entities or concepts |
| `calculated` | Intended for reproducible derived values |
| `historical` | Preserves a past state or event |
| `temporal` | Meaning depends on observation, effective date, period, or event time |
| `append_only` | New events are appended rather than replacing earlier events |
| `single_active` | At most one active Fact per entity and Field |
| `multiple_active` | Multiple active Facts per entity and Field are allowed |

## Validation flow

1. Validate the Field and Fact JSON structures.
2. Resolve the Fact's `field_id` to exactly one registry definition.
3. Enforce entity type, value type, unit, classification, verification, and deprecation policies.
4. Enforce active-Fact cardinality across the repository.
5. Validate provenance, typed entity references, derivation inputs, and lifecycle/supersession graphs.

A Fact is usable only when structural, semantic, provenance, and lifecycle validation all pass.

## Lifecycle and deprecation

Field IDs are permanent. Active Fields have no replacement. A deprecated Field must identify a valid replacement and cannot govern a new active Fact. Historical Facts using the deprecated ID remain valid when their lifecycle is deprecated or superseded. Replacement links are resolvable and acyclic.

Renaming `canonical_name` or `display_label` is a governed metadata revision. Historical Facts remain unchanged because they store only the immutable Field ID.

## Synthetic registry

`data/canonical/field/part-001.jsonl` contains synthetic definitions used to validate every supported value type, numeric and unitless policies, multiple entity types, relationships, calculation, history, and deprecation. These are semantic contracts only—not company or infrastructure data.

## Permanent governed-object rule

Every governed repository object has a permanent immutable identifier, a governed canonical name, and optional presentation metadata. Entity `slug` and `display_name`, Source `title`, and Field `canonical_name` and `display_label` are equivalent vocabulary implementations. A Fact's governed semantic name is inherited through its immutable `field_id`; duplicating the mutable Field name inside the Fact is intentionally prohibited. Future exceptions require an explicit architectural explanation.
