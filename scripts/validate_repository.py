#!/usr/bin/env python3
"""Validate JSON Schemas and JSON/JSONL repository data."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError:
        print("Install requirements-dev.txt before validation.", file=sys.stderr)
        return 2
    schemas = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "schemas").glob("*.schema.json"))}
    registry = Registry()
    for schema in schemas.values():
        jsonschema.Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    entity_schemas = {n.removesuffix(".schema.json"): s for n, s in schemas.items() if n != "common.schema.json"}
    errors = []
    for path in sorted((ROOT / "data").rglob("*.json")):
        entity = path.stem.split(".")[0]
        if entity not in entity_schemas:
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        records = value if isinstance(value, list) else [value]
        validator = jsonschema.Draft202012Validator(entity_schemas[entity], registry=registry)
        for index, record in enumerate(records):
            errors.extend(f"{path}:{index}: {e.message}" for e in validator.iter_errors(record))
    for path in sorted((ROOT / "data").rglob("*.jsonl")):
        entity = path.stem.split(".")[0]
        if entity not in entity_schemas:
            continue
        validator = jsonschema.Draft202012Validator(entity_schemas[entity], registry=registry)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{number}: {exc}")
                continue
            errors.extend(f"{path}:{number}: {e.message}" for e in validator.iter_errors(record))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(schemas)} schemas and repository data files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
