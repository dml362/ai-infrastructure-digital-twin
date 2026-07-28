import json
import shutil
import tempfile
import unittest
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from scripts.validate_repository import validate_repository

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "SOURCE-SEC-2026-001"
SOURCE_ID_2 = "SOURCE-SEC-2026-002"
COMPANY_ID = "550e8400-e29b-41d4-a716-446655440000"
FACT_ID = "123e4567-e89b-42d3-a456-426614174000"
FACT_ID_2 = "223e4567-e89b-42d3-a456-426614174000"


def source_record(source_id=SOURCE_ID, **overrides):
    record = {
        "id": source_id,
        "schema_version": "0.2.0",
        "created_at": "2026-07-28T12:00:00Z",
        "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [source_id],
        "confidence_score": 5,
        "status": "reviewed",
        "notes": None,
        "title": "Synthetic Test Filing",
        "organization": "Test Organization",
        "publication_date": "2026-07-28",
        "document_date": "2026-07-27",
        "authors": [],
        "publisher": "Test Publisher",
        "source_type": "sec_filing",
        "source_url": "https://example.com/test-filing",
        "storage_provider": "none",
        "storage_location": None,
        "external_file_id": None,
        "original_filename": None,
        "media_type": None,
        "file_size_bytes": None,
        "cryptographic_hash": None,
        "hash_algorithm": None,
        "archived_at": None,
        "access_status": "public",
        "copyright_status": "public_domain",
        "version": None,
        "language": "en",
        "access_restrictions": None,
        "reliability_notes": None,
        "superseded_by_source_id": None,
        "supersedes_source_ids": [],
    }
    record.update(overrides)
    return record


def company_record(**overrides):
    record = {
        "id": COMPANY_ID,
        "schema_version": "0.1.0",
        "created_at": "2026-07-28T12:00:00Z",
        "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [SOURCE_ID],
        "confidence_score": 5,
        "status": "active",
        "notes": None,
        "legal_name": "Synthetic Test Company",
        "website_url": "https://example.com",
    }
    record.update(overrides)
    return record


def fact_record(fact_id=FACT_ID, **overrides):
    record = {
        "id": fact_id,
        "schema_version": "0.2.0",
        "created_at": "2026-07-28T12:00:00Z",
        "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [SOURCE_ID],
        "confidence_score": 5,
        "status": "verified",
        "notes": None,
        "entity_type": "company",
        "entity_id": COMPANY_ID,
        "field_name": "legal_name",
        "observed_value": "Synthetic Test Company",
        "unit": None,
        "observation_date": "2026-07-28",
        "effective_date": None,
        "superseded_by_fact_id": None,
        "supersedes_fact_ids": [],
        "input_fact_ids": [],
        "derivation_method": None,
        "estimation_method": None,
    }
    record.update(overrides)
    return record


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

    def write_valid_foundation(self):
        self.write_jsonl("canonical/source/part-001.jsonl", source_record())
        self.write_jsonl("canonical/company/part-001.jsonl", company_record())


class EvidenceArchitectureTests(unittest.TestCase):
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

    def schema_errors(self, schema_name, record):
        validator = jsonschema.Draft202012Validator(
            self.schemas[schema_name],
            registry=self.registry,
            format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
        )
        return list(validator.iter_errors(record))

    def test_all_schema_contracts_are_documented(self):
        self.assertEqual(12, len(self.schemas))
        for name, schema in self.schemas.items():
            with self.subTest(schema=name):
                jsonschema.Draft202012Validator.check_schema(schema)
                if name == "common.schema.json":
                    continue
                self.assertFalse(schema["additionalProperties"])
                for field, definition in schema["properties"].items():
                    self.assertIn("description", definition, f"{name}.{field}")

    def test_valid_fact_creation(self):
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", fact_record())
            self.assertEqual([], validate_repository(fixture.root))

    def test_google_drive_source_metadata_is_valid(self):
        drive_source = source_record(
            storage_provider="google_drive",
            storage_location="Digital Twin/Source Archive/2026",
            external_file_id="1AbCdEfSyntheticId",
            original_filename="test-filing.pdf",
            media_type="application/pdf",
            file_size_bytes=1024,
            cryptographic_hash="a" * 64,
            hash_algorithm="sha256",
            archived_at="2026-07-28T13:00:00Z",
            access_status="restricted",
        )
        self.assertEqual([], self.schema_errors("source.schema.json", drive_source))

    def test_external_archive_requires_valid_digest(self):
        drive_source = source_record(
            storage_provider="google_drive",
            storage_location="Digital Twin/Source Archive/2026",
            external_file_id="1AbCdEfSyntheticId",
            original_filename="test-filing.pdf",
            media_type="application/pdf",
            file_size_bytes=1024,
            cryptographic_hash=None,
            hash_algorithm=None,
            archived_at="2026-07-28T13:00:00Z",
        )
        errors = self.schema_errors("source.schema.json", drive_source)
        self.assertTrue(errors)

    def test_invalid_source_reference_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/source/part-001.jsonl", source_record())
            fixture.write_jsonl(
                "canonical/company/part-001.jsonl",
                company_record(source_ids=[SOURCE_ID_2]),
            )
            errors = validate_repository(fixture.root)
            self.assertTrue(any("broken Source reference" in error for error in errors))

    def test_invalid_fact_status_fails(self):
        errors = self.schema_errors(
            "fact.schema.json", fact_record(status="accepted")
        )
        self.assertTrue(any(error.validator == "enum" for error in errors))

    def test_circular_fact_supersession_fails(self):
        first = fact_record(
            status="superseded",
            superseded_by_fact_id=FACT_ID_2,
            supersedes_fact_ids=[FACT_ID_2],
        )
        second = fact_record(
            FACT_ID_2,
            status="superseded",
            superseded_by_fact_id=FACT_ID,
            supersedes_fact_ids=[FACT_ID],
        )
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", first, second)
            errors = validate_repository(fixture.root)
            self.assertTrue(any("Circular Fact supersession" in error for error in errors))

    def test_fact_cannot_supersede_a_different_field(self):
        prior = fact_record(
            status="superseded", superseded_by_fact_id=FACT_ID_2
        )
        replacement = fact_record(
            FACT_ID_2,
            field_name="display_name",
            supersedes_fact_ids=[FACT_ID],
        )
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", prior, replacement)
            errors = validate_repository(fixture.root)
            self.assertTrue(any("different entity or field" in error for error in errors))

    def test_missing_provenance_fails(self):
        errors = self.schema_errors("fact.schema.json", fact_record(source_ids=[]))
        self.assertTrue(any(error.validator == "minItems" for error in errors))

    def test_duplicate_fact_ids_fail(self):
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl(
                "canonical/fact/part-001.jsonl", fact_record(), fact_record()
            )
            errors = validate_repository(fixture.root)
            self.assertTrue(any("duplicate fact ID" in error for error in errors))

    def test_duplicate_source_ids_fail(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl(
                "canonical/source/part-001.jsonl", source_record(), source_record()
            )
            errors = validate_repository(fixture.root)
            self.assertTrue(any("duplicate source ID" in error for error in errors))

    def test_broken_typed_entity_reference_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/source/part-001.jsonl", source_record())
            fixture.write_jsonl("canonical/fact/part-001.jsonl", fact_record())
            errors = validate_repository(fixture.root)
            self.assertTrue(any("broken typed entity reference" in error for error in errors))

    def test_missing_unit_for_numeric_fact_fails(self):
        errors = self.schema_errors(
            "fact.schema.json",
            fact_record(field_name="capacity_mw", observed_value=401, unit=None),
        )
        self.assertTrue(any("unit" in list(error.absolute_path) for error in errors))

    def test_valid_derived_fact_references_inputs(self):
        derived = fact_record(
            FACT_ID_2,
            status="derived",
            observed_value=2,
            unit="count",
            input_fact_ids=[FACT_ID],
            derivation_method="count(input_fact_ids)",
        )
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl(
                "canonical/fact/part-001.jsonl", fact_record(), derived
            )
            self.assertEqual([], validate_repository(fixture.root))

    def test_broken_input_fact_reference_fails(self):
        derived = fact_record(
            status="derived",
            observed_value=1,
            unit="count",
            input_fact_ids=[FACT_ID_2],
            derivation_method="count(input_fact_ids)",
        )
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", derived)
            errors = validate_repository(fixture.root)
            self.assertTrue(any("broken input Fact reference" in error for error in errors))

    def test_unknown_entity_directory_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/unknown/part-001.jsonl", fact_record())
            errors = validate_repository(fixture.root)
            self.assertTrue(any("unknown canonical entity directory" in error for error in errors))

    def test_unsupported_filename_fails(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/fact/facts.jsonl", fact_record())
            errors = validate_repository(fixture.root)
            self.assertTrue(any("unsupported canonical filename" in error for error in errors))

    def test_invalid_date_timestamp_uri_and_uuid_fail(self):
        source_errors = self.schema_errors(
            "source.schema.json",
            source_record(publication_date="yesterday", source_url="not a uri"),
        )
        fact_errors = self.schema_errors(
            "fact.schema.json",
            fact_record(id="not-a-uuid", created_at="not-a-timestamp"),
        )
        validators = {error.validator for error in source_errors + fact_errors}
        self.assertIn("format", validators)
        self.assertGreaterEqual(len(source_errors + fact_errors), 4)


if __name__ == "__main__":
    unittest.main()
