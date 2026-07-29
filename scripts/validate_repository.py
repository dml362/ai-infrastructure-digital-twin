#!/usr/bin/env python3
"""Validate schemas, canonical JSONL records, provenance, and relationship graphs."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
PART_FILENAME = re.compile(r"^part-[0-9]{3,}\.jsonl$")
ENTITY_SCHEMAS = {
    "company": "company.schema.json",
    "campus": "campus.schema.json",
    "project": "project.schema.json",
    "lease": "lease.schema.json",
    "power_asset": "power_asset.schema.json",
    "customer": "customer.schema.json",
    "financing": "financing.schema.json",
    "construction_milestone": "construction_milestone.schema.json",
    "source": "source.schema.json",
    "fact": "fact.schema.json",
    "field": "field.schema.json",
    "market_assumption": "market_assumption.schema.json",
}
RELATIONSHIP_TARGETS = {
    "company_id": "company",
    "campus_id": "campus",
    "project_id": "project",
    "customer_id": "customer",
    "parent_customer_id": "customer",
    "dependency_milestone_ids": "construction_milestone",
}
IMMUTABLE_FACT_FIELDS = {
    "id", "schema_version", "created_at", "source_ids", "value_classification",
    "entity_type", "entity_id", "field_id", "value_type", "observed_value",
    "unit", "observation_date", "effective_date", "input_fact_ids",
    "derivation_method", "estimation_method", "estimation_assumptions",
}


def validate_fact_revision(previous: dict[str, Any], revised: dict[str, Any]) -> list[str]:
    """Reject in-place mutation of immutable Fact assertion and production fields."""
    errors = []
    for field in sorted(IMMUTABLE_FACT_FIELDS):
        if previous.get(field) != revised.get(field):
            errors.append(
                f"Fact '{previous.get('id')}' immutable field '{field}' changed; "
                "create a replacement Fact and use reciprocal supersession"
            )
    return errors


def load_schemas(root: Path) -> tuple[dict[str, Any], Any, Any]:
    """Load and validate every schema contract."""
    import jsonschema
    from referencing import Registry, Resource

    schemas = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / "schemas").glob("*.schema.json"))
    }
    expected = set(ENTITY_SCHEMAS.values()) | {"common.schema.json"}
    missing = expected - set(schemas)
    unexpected = set(schemas) - expected
    if missing:
        raise ValueError(f"Missing schema files: {', '.join(sorted(missing))}")
    if unexpected:
        raise ValueError(f"Unmapped schema files: {', '.join(sorted(unexpected))}")

    registry = Registry()
    for schema in schemas.values():
        jsonschema.Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(
            schema["$id"], Resource.from_contents(schema)
        )
    return schemas, registry, jsonschema


def map_data_file(root: Path, path: Path) -> tuple[str | None, str | None]:
    """Map data/canonical/<entity>/.../part-NNN.jsonl to a schema."""
    relative = path.relative_to(root / "data")
    parts = relative.parts
    display = relative.as_posix()
    if not parts or parts[0] != "canonical":
        return None, (
            f"{display}: unsupported data location; structured data files must be "
            "under data/canonical/<entity>/"
        )
    if len(parts) < 3:
        return None, (
            f"{display}: canonical data path must include a supported entity directory "
            "and a part file"
        )
    entity = parts[1]
    if entity not in ENTITY_SCHEMAS:
        supported = ", ".join(sorted(ENTITY_SCHEMAS))
        return None, (
            f"{display}: unknown canonical entity directory '{entity}'; "
            f"supported directories: {supported}"
        )
    if not PART_FILENAME.fullmatch(path.name):
        return None, (
            f"{display}: unsupported canonical filename '{path.name}'; "
            "expected part-NNN.jsonl"
        )
    return entity, None


def _detect_cycles(graph: dict[str, set[str]], label: str) -> list[str]:
    """Return deterministic errors for directed graph cycles."""
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            start = stack.index(node)
            cycle = stack[start:] + [node]
            errors.append(f"Circular {label}: {' -> '.join(cycle)}")
            return
        visiting.add(node)
        stack.append(node)
        for target in sorted(graph.get(node, set())):
            visit(target)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return errors


def _record_location(path: Path, line_number: int) -> str:
    return f"{path}:{line_number}"


def _validate_relationships(
    records: dict[str, list[tuple[dict[str, Any], Path, int]]]
) -> list[str]:
    errors: list[str] = []
    indexes: dict[str, dict[str, tuple[dict[str, Any], Path, int]]] = {}

    for entity, items in records.items():
        index: dict[str, tuple[dict[str, Any], Path, int]] = {}
        for record, path, line_number in items:
            record_id = record.get("id")
            if not isinstance(record_id, str):
                continue
            if record_id in index:
                first = index[record_id]
                errors.append(
                    f"{_record_location(path, line_number)}: duplicate {entity} ID "
                    f"'{record_id}'; first defined at {_record_location(first[1], first[2])}"
                )
            else:
                index[record_id] = (record, path, line_number)
        indexes[entity] = index

    source_index = indexes.get("source", {})
    for entity, items in records.items():
        for record, path, line_number in items:
            location = _record_location(path, line_number)
            for source_id in record.get("source_ids", []):
                if source_id not in source_index:
                    errors.append(
                        f"{location}: broken Source reference '{source_id}' in source_ids"
                    )
            if entity == "source" and record.get("id") not in record.get("source_ids", []):
                errors.append(f"{location}: Source source_ids must contain its own id")

            if entity not in {"fact", "source"}:
                for field_name, target_entity in RELATIONSHIP_TARGETS.items():
                    value = record.get(field_name)
                    target_ids: Iterable[str] = value if isinstance(value, list) else [value]
                    for target_id in target_ids:
                        if target_id is not None and target_id not in indexes.get(target_entity, {}):
                            errors.append(
                                f"{location}: broken {target_entity} reference "
                                f"'{target_id}' in {field_name}"
                            )

    fact_index = indexes.get("fact", {})
    fact_supersession: dict[str, set[str]] = defaultdict(set)
    derivation_graph: dict[str, set[str]] = defaultdict(set)
    for fact_id, (fact, path, line_number) in fact_index.items():
        location = _record_location(path, line_number)
        subject_type = fact.get("entity_type")
        subject_id = fact.get("entity_id")
        if subject_id not in indexes.get(subject_type, {}):
            errors.append(
                f"{location}: broken typed entity reference "
                f"'{subject_type}:{subject_id}'"
            )
        replacement_id = fact.get("superseded_by_fact_id")
        if replacement_id is not None:
            fact_supersession[fact_id].add(replacement_id)
            replacement = fact_index.get(replacement_id)
            if replacement is None:
                errors.append(f"{location}: broken superseding Fact reference '{replacement_id}'")
            else:
                replacement_fact = replacement[0]
                if fact_id not in replacement_fact.get("supersedes_fact_ids", []):
                    errors.append(
                        f"{location}: supersession is not reciprocal; Fact '{replacement_id}' "
                        f"must list '{fact_id}' in supersedes_fact_ids"
                    )
                subject = (fact.get("entity_type"), fact.get("entity_id"), fact.get("field_id"))
                replacement_subject = (
                    replacement_fact.get("entity_type"), replacement_fact.get("entity_id"),
                    replacement_fact.get("field_id"),
                )
                if subject != replacement_subject:
                    errors.append(
                        f"{location}: Fact '{replacement_id}' cannot supersede a different "
                        "entity or field"
                    )
        for prior_id in fact.get("supersedes_fact_ids", []):
            prior = fact_index.get(prior_id)
            if prior is None:
                errors.append(f"{location}: broken superseded Fact reference '{prior_id}'")
            elif prior[0].get("superseded_by_fact_id") != fact_id:
                errors.append(
                    f"{location}: supersession is not reciprocal; Fact '{prior_id}' "
                    f"must set superseded_by_fact_id to '{fact_id}'"
                )
        for input_id in fact.get("input_fact_ids", []):
            derivation_graph[fact_id].add(input_id)
            if input_id not in fact_index:
                errors.append(f"{location}: broken input Fact reference '{input_id}'")

    errors.extend(_detect_cycles(fact_supersession, "Fact supersession"))
    errors.extend(_detect_cycles(derivation_graph, "Fact derivation"))

    field_index = indexes.get("field", {})
    field_replacement: dict[str, set[str]] = defaultdict(set)
    canonical_names: dict[str, str] = {}
    for field_id, (field, path, line_number) in field_index.items():
        location = _record_location(path, line_number)
        canonical_name = field.get("canonical_name")
        if isinstance(canonical_name, str):
            if canonical_name in canonical_names:
                errors.append(
                    f"{location}: duplicate Field canonical_name '{canonical_name}'; "
                    f"first assigned to '{canonical_names[canonical_name]}'"
                )
            else:
                canonical_names[canonical_name] = field_id
        replacement_id = field.get("replacement_field_id")
        if replacement_id is not None:
            field_replacement[field_id].add(replacement_id)
            if replacement_id == field_id:
                errors.append(f"{location}: Field '{field_id}' cannot replace itself")
            elif replacement_id not in field_index:
                errors.append(f"{location}: broken replacement Field reference '{replacement_id}'")
        units = set(field.get("allowed_units", []))
        policy = field.get("unitless_policy")
        if policy == "required" and units != {"unitless"}:
            errors.append(f"{location}: unitless_policy required permits only the unitless unit")
        if policy == "allowed" and "unitless" not in units:
            errors.append(f"{location}: unitless_policy allowed requires unitless in allowed_units")
        if policy == "prohibited" and "unitless" in units:
            errors.append(f"{location}: unitless_policy prohibited cannot list unitless")
    errors.extend(_detect_cycles(field_replacement, "Field replacement"))

    active_facts: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for fact_id, (fact, path, line_number) in fact_index.items():
        location = _record_location(path, line_number)
        field_id = fact.get("field_id")
        registered = field_index.get(field_id)
        if registered is None:
            errors.append(f"{location}: unknown Field reference '{field_id}'")
            continue
        field = registered[0]
        if fact.get("entity_type") not in field.get("applicable_entity_types", []):
            errors.append(
                f"{location}: Field '{field_id}' does not apply to entity type "
                f"'{fact.get('entity_type')}'"
            )
        if fact.get("value_type") != field.get("value_type"):
            errors.append(
                f"{location}: Field '{field_id}' requires value_type "
                f"'{field.get('value_type')}', not '{fact.get('value_type')}'"
            )
        if fact.get("value_type") in {"number", "integer"}:
            if fact.get("unit") not in field.get("allowed_units", []):
                errors.append(
                    f"{location}: unit '{fact.get('unit')}' is not allowed for Field '{field_id}'"
                )
        elif fact.get("unit") is not None:
            errors.append(f"{location}: non-numeric Field '{field_id}' requires a null unit")
        classification = fact.get("value_classification")
        if classification not in field.get("permitted_value_classifications", []):
            errors.append(
                f"{location}: classification '{classification}' is not permitted for Field '{field_id}'"
            )
        if classification == "estimated" and not field.get("estimated_values_allowed"):
            errors.append(f"{location}: estimated values are prohibited for Field '{field_id}'")
        if classification == "derived" and not field.get("derived_values_allowed"):
            errors.append(f"{location}: derived values are prohibited for Field '{field_id}'")
        verification = fact.get("verification_status")
        if verification not in field.get("permitted_verification_states", []):
            errors.append(
                f"{location}: verification state '{verification}' is not permitted for Field '{field_id}'"
            )
        if field.get("deprecated") and fact.get("lifecycle_status") == "active":
            errors.append(f"{location}: deprecated Field '{field_id}' cannot govern an active Fact")
        if fact.get("lifecycle_status") == "active":
            key = (fact.get("entity_type"), fact.get("entity_id"), field_id)
            active_facts[key].append(fact_id)

    for key, fact_ids in sorted(active_facts.items()):
        field = field_index[key[2]][0]
        if not field.get("multiple_active_facts_allowed") and len(fact_ids) > 1:
            errors.append(
                f"Multiple active Facts prohibited for {key[0]}:{key[1]} Field '{key[2]}': "
                f"{', '.join(sorted(fact_ids))}"
            )

    source_supersession: dict[str, set[str]] = defaultdict(set)
    for source_id, (source, path, line_number) in source_index.items():
        location = _record_location(path, line_number)
        replacement_id = source.get("superseded_by_source_id")
        if replacement_id is not None:
            source_supersession[source_id].add(replacement_id)
            replacement = source_index.get(replacement_id)
            if replacement is None:
                errors.append(f"{location}: broken replacement Source reference '{replacement_id}'")
            elif source_id not in replacement[0].get("supersedes_source_ids", []):
                errors.append(
                    f"{location}: Source supersession is not reciprocal for '{replacement_id}'"
                )
        for prior_id in source.get("supersedes_source_ids", []):
            prior = source_index.get(prior_id)
            if prior is None:
                errors.append(f"{location}: broken superseded Source reference '{prior_id}'")
            elif prior[0].get("superseded_by_source_id") != source_id:
                errors.append(
                    f"{location}: Source supersession is not reciprocal for '{prior_id}'"
                )
    errors.extend(_detect_cycles(source_supersession, "Source supersession"))
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    """Return all schema, uniqueness, provenance, and relationship errors."""
    schemas, registry, jsonschema = load_schemas(root)
    format_checker = jsonschema.Draft202012Validator.FORMAT_CHECKER
    errors: list[str] = []
    records: dict[str, list[tuple[dict[str, Any], Path, int]]] = defaultdict(list)
    data_root = root / "data"
    if not data_root.exists():
        return errors

    for path in sorted(item for item in data_root.rglob("*") if item.is_file()):
        if path.name == ".gitkeep":
            continue
        entity, mapping_error = map_data_file(root, path)
        if mapping_error:
            errors.append(mapping_error)
            continue
        validator = jsonschema.Draft202012Validator(
            schemas[ENTITY_SCHEMAS[entity]],
            registry=registry,
            format_checker=format_checker,
        )
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(record, dict):
                errors.append(f"{path}:{line_number}: canonical record must be a JSON object")
                continue
            records[entity].append((record, path, line_number))
            for error in validator.iter_errors(record):
                location = ".".join(str(part) for part in error.absolute_path)
                suffix = f" at {location}" if location else ""
                errors.append(f"{path}:{line_number}: {error.message}{suffix}")

    errors.extend(_validate_relationships(records))
    return errors


def main() -> int:
    try:
        errors = validate_repository()
    except ImportError:
        print("Missing dependency: install requirements-dev.txt before validation.", file=sys.stderr)
        return 2
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Repository contract error: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Validated {len(ENTITY_SCHEMAS) + 1} schemas, canonical records, "
        "semantic governance, provenance, uniqueness, and relationships."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
