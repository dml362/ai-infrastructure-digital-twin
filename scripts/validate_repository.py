#!/usr/bin/env python3
"""Validate JSON Schemas and canonical JSONL repository data."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

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
    "source_document": "source_document.schema.json",
    "market_assumption": "market_assumption.schema.json",
}


def load_schemas(root: Path) -> tuple[dict[str, Any], Any, Any]:
    """Load and validate schema contracts, returning schemas and validator helpers."""
    import jsonschema
    from referencing import Registry, Resource

    schema_dir = root / "schemas"
    schemas = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(schema_dir.glob("*.schema.json"))
    }
    expected = set(ENTITY_SCHEMAS.values()) | {"common.schema.json"}
    missing = expected - set(schemas)
    if missing:
        raise ValueError(f"Missing schema files: {', '.join(sorted(missing))}")

    registry = Registry()
    for schema in schemas.values():
        jsonschema.Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(
            schema["$id"], Resource.from_contents(schema)
        )
    return schemas, registry, jsonschema


def map_data_file(root: Path, path: Path) -> tuple[str | None, str | None]:
    """Map a data path to an entity schema name or return a clear validation error."""
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
    return ENTITY_SCHEMAS[entity], None


def validate_repository(root: Path = ROOT) -> list[str]:
    """Return all schema and canonical-data validation errors."""
    schemas, registry, jsonschema = load_schemas(root)
    format_checker = jsonschema.Draft202012Validator.FORMAT_CHECKER
    errors: list[str] = []
    data_root = root / "data"

    if not data_root.exists():
        return errors

    for path in sorted(item for item in data_root.rglob("*") if item.is_file()):
        if path.name == ".gitkeep":
            continue

        schema_name, mapping_error = map_data_file(root, path)
        if mapping_error:
            errors.append(mapping_error)
            continue

        validator = jsonschema.Draft202012Validator(
            schemas[schema_name],
            registry=registry,
            format_checker=format_checker,
        )
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
                continue
            for error in validator.iter_errors(record):
                location = ".".join(str(part) for part in error.absolute_path)
                suffix = f" at {location}" if location else ""
                errors.append(f"{path}:{line_number}: {error.message}{suffix}")
    return errors


def main() -> int:
    try:
        errors = validate_repository()
    except ImportError:
        print(
            "Missing dependency: install requirements-dev.txt before validation.",
            file=sys.stderr,
        )
        return 2
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Repository contract error: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        f"Validated {len(ENTITY_SCHEMAS) + 1} schemas and all repository data files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
