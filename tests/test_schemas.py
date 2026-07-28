import json
import shutil
import tempfile
import unittest
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from scripts.validate_repository import validate_repository

ROOT = Path(__file__).resolve().parents[1]
METADATA = {"id", "created_at", "modified_at", "source_ids", "confidence_score", "status", "notes"}
UUID_1 = "550e8400-e29b-41d4-a716-446655440000"
UUID_2 = "123e4567-e89b-42d3-a456-426614174000"
SOURCE_ID = "SOURCE-SEC-2026-001"


def company_record(**overrides):
    record = {
        "id": UUID_1, "schema_version": "0.1.0",
        "created_at": "2026-07-28T12:00:00Z",
        "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [SOURCE_ID], "confidence_score": 5,
        "status": "active", "notes": None,
        "legal_name": "Fixture Company", "website_url": "https://example.com",
    }
    record.update(overrides)
    return record


def customer_record():
    return {
        "id": UUID_2, "schema_version": "0.1.0",
        "created_at": "2026-07-28T12:00:00Z",
        "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [SOURCE_ID], "confidence_score": 4,
        "status": "active", "notes": None, "name": "Fixture Customer",
    }


class RepositoryFixture:
    def __enter__(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        (self.root / "data").mkdir()
        return self

    def __exit__(self, *args):
        self.temp.cleanup()

    def write_jsonl(self, relative_path, *records):
        path = self.root / "data" / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )
        return path


class SchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in (ROOT / "schemas").glob("*.schema.json")
        }
        cls.registry = Registry()
        for schema in cls.schemas.values():
            cls.registry = cls.registry.with_resource(
                schema["$id"], Resource.from_contents(schema)
            )

    def company_errors(self, **overrides):
        validator = jsonschema.Draft202012Validator(
            self.schemas["company.schema.json"],
            registry=self.registry,
            format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
        )
        return list(validator.iter_errors(company_record(**overrides)))

    def test_entity_contracts(self):
        entity_schemas = {
            name: schema for name, schema in self.schemas.items()
            if name != "common.schema.json"
        }
        self.assertEqual(10, len(entity_schemas))
        for name, schema in entity_schemas.items():
            with self.subTest(schema=name):
                self.assertTrue(METADATA <= set(schema["properties"]))
                self.assertTrue(METADATA <= set(schema["required"]))
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual("0.1.0", schema["properties"]["schema_version"]["const"])
                for field, definition in schema["properties"].items():
                    self.assertIn(
                        "description", definition,
                        f"{name}.{field} must document its contract",
                    )

    def test_unique_schema_ids(self):
        ids = [schema["$id"] for schema in self.schemas.values()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_valid_canonical_part_file(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/company/part-001.jsonl", company_record())
            self.assertEqual([], validate_repository(fixture.root))

    def test_multiple_supported_entity_directories(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/company/year=2026/part-001.jsonl", company_record())
            fixture.write_jsonl("canonical/customer/year=2026/part-002.jsonl", customer_record())
            self.assertEqual([], validate_repository(fixture.root))

    def test_unknown_entity_directory_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/unknown/part-001.jsonl", company_record())
            errors = validate_repository(fixture.root)
            self.assertTrue(any("unknown canonical entity directory" in error for error in errors))

    def test_unsupported_canonical_filename_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/company/company.jsonl", company_record())
            errors = validate_repository(fixture.root)
            self.assertTrue(any("unsupported canonical filename" in error for error in errors))

    def test_previously_silently_ignored_file_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("ignored.json", company_record())
            errors = validate_repository(fixture.root)
            self.assertTrue(any("unsupported data location" in error for error in errors))

    def test_invalid_date_fails(self):
        project = {
            "id": UUID_1, "schema_version": "0.1.0",
            "created_at": "2026-07-28T12:00:00Z",
            "modified_at": "2026-07-28T12:00:00Z",
            "source_ids": [SOURCE_ID], "confidence_score": 4,
            "status": "active", "notes": None,
            "company_id": UUID_1, "campus_id": UUID_2,
            "name": "Fixture Project", "project_type": "data_center",
            "start_date": "yesterday",
        }
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/project/part-001.jsonl", project)
            errors = validate_repository(fixture.root)
            self.assertTrue(errors, "the invalid date must be rejected")
            self.assertTrue(any("start_date" in error for error in errors))

    def test_invalid_timestamp_fails(self):
        self.assertTrue(any(
            error.validator == "format"
            for error in self.company_errors(created_at="not-a-timestamp")
        ))

    def test_malformed_uri_fails(self):
        self.assertTrue(any(
            error.validator == "format"
            for error in self.company_errors(website_url="not a uri")
        ))

    def test_malformed_uuid_fails(self):
        self.assertTrue(any(
            error.validator == "format"
            for error in self.company_errors(id="------------------------------------")
        ))


if __name__ == "__main__":
    unittest.main()
