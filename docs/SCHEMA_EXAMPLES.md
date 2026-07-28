# Synthetic Schema Examples

These examples demonstrate contracts only. They do not represent a real company, asset, agreement, or source.

## Structural Company node

```json
{"id":"550e8400-e29b-41d4-a716-446655440000","schema_version":"0.2.0","entity_type":"company","slug":"synthetic-company","display_name":"Synthetic company node","created_at":"2026-07-28T12:00:00Z","modified_at":"2026-07-28T12:00:00Z","record_status":"active","administrative_notes":null}
```

`display_name` is only an interface label. An asserted legal name is a separate text Fact whose `field_name` is `legal_name`.

## Typed Fact states

- Observed legal name: `text`, observed/verified/active, null unit.
- Estimated capacity: `number`, estimated/pending_review/active, `MW`, plus estimation method and assumptions.
- Derived count: `integer`, derived/verified/superseded, `unitless`, plus input Fact IDs and derivation method. Supersession does not remove those inputs.
- Disputed construction date: `date`, observed/disputed/active, null unit and a valid ISO date.

```json
{"id":"123e4567-e89b-42d3-a456-426614174000","schema_version":"0.2.0","created_at":"2026-07-28T12:00:00Z","modified_at":"2026-07-28T12:00:00Z","source_ids":["SOURCE-SEC-2026-001"],"confidence_score":5,"value_classification":"observed","verification_status":"verified","lifecycle_status":"active","notes":null,"entity_type":"company","entity_id":"550e8400-e29b-41d4-a716-446655440000","field_name":"legal_name","value_type":"text","observed_value":"Synthetic Test Company","unit":null,"observation_date":"2026-07-28","effective_date":null,"superseded_by_fact_id":null,"supersedes_fact_ids":[],"input_fact_ids":[],"derivation_method":null,"estimation_method":null,"estimation_assumptions":null}
```

Unknown values are not encoded as null Facts. If evidence does not support an assertion, no Fact is created; an explicit estimate may be created only with its method, assumptions, provenance, and confidence.
