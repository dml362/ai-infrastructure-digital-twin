import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from scripts.validate_repository import validate_fact_revision, validate_repository

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "SOURCE-SEC-2026-001"
SOURCE_ID_2 = "SOURCE-SEC-2026-002"
COMPANY_ID = "550e8400-e29b-41d4-a716-446655440000"
FACT_ID = "123e4567-e89b-42d3-a456-426614174000"
FACT_ID_2 = "223e4567-e89b-42d3-a456-426614174000"


def source_record(source_id=SOURCE_ID, **overrides):
    record = {
        "id": source_id, "schema_version": "0.2.0",
        "created_at": "2026-07-28T12:00:00Z", "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [source_id], "confidence_score": 5, "status": "reviewed", "notes": None,
        "title": "Synthetic Test Filing", "organization": "Test Organization",
        "publication_date": "2026-07-28", "document_date": "2026-07-27", "authors": [],
        "publisher": "Test Publisher", "source_type": "sec_filing",
        "source_url": "https://example.com/test-filing", "storage_provider": "none",
        "storage_location": None, "external_file_id": None, "original_filename": None,
        "media_type": None, "file_size_bytes": None, "cryptographic_hash": None,
        "hash_algorithm": None, "archived_at": None, "archive_access_status": None,
        "copyright_status": "public_domain", "version": None, "language": "en",
        "access_restrictions": None, "reliability_notes": None,
        "superseded_by_source_id": None, "supersedes_source_ids": [],
    }
    record.update(overrides)
    return record


def company_record(**overrides):
    record = {
        "id": COMPANY_ID, "schema_version": "0.2.0", "entity_type": "company",
        "slug": "synthetic-company", "display_name": "Synthetic company node",
        "created_at": "2026-07-28T12:00:00Z", "modified_at": "2026-07-28T12:00:00Z",
        "record_status": "active", "administrative_notes": None,
    }
    record.update(overrides)
    return record


def fact_record(fact_id=FACT_ID, **overrides):
    record = {
        "id": fact_id, "schema_version": "0.2.0",
        "created_at": "2026-07-28T12:00:00Z", "modified_at": "2026-07-28T12:00:00Z",
        "source_ids": [SOURCE_ID], "confidence_score": 5,
        "value_classification": "observed", "verification_status": "verified",
        "lifecycle_status": "active", "notes": None, "entity_type": "company",
        "entity_id": COMPANY_ID, "field_name": "legal_name", "value_type": "text",
        "observed_value": "Synthetic Test Company", "unit": None,
        "observation_date": "2026-07-28", "effective_date": None,
        "superseded_by_fact_id": None, "supersedes_fact_ids": [], "input_fact_ids": [],
        "derivation_method": None, "estimation_method": None, "estimation_assumptions": None,
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
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    def write_valid_foundation(self):
        self.write_jsonl("canonical/source/part-001.jsonl", source_record())
        self.write_jsonl("canonical/company/part-001.jsonl", company_record())


class EvidenceArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "schemas").glob("*.schema.json")}
        cls.registry = Registry()
        for schema in cls.schemas.values():
            cls.registry = cls.registry.with_resource(schema["$id"], Resource.from_contents(schema))

    def schema_errors(self, schema_name, record):
        validator = jsonschema.Draft202012Validator(self.schemas[schema_name], registry=self.registry, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER)
        return list(validator.iter_errors(record))

    def assert_invalid_fact(self, **overrides):
        self.assertTrue(self.schema_errors("fact.schema.json", fact_record(**overrides)))

    def test_all_schema_contracts_parse_and_properties_are_documented(self):
        self.assertEqual(12, len(self.schemas))
        for name, schema in self.schemas.items():
            jsonschema.Draft202012Validator.check_schema(schema)
            if name != "common.schema.json":
                self.assertFalse(schema["additionalProperties"])
                for field, definition in schema["properties"].items():
                    self.assertIn("description", definition, f"{name}.{field}")

    def test_valid_observed_fact_and_structural_entity(self):
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", fact_record())
            self.assertEqual([], validate_repository(fixture.root))

    def test_asserted_attribute_is_rejected_by_entity_and_valid_as_fact(self):
        self.assertTrue(self.schema_errors("company.schema.json", company_record(legal_name="Not allowed")))
        self.assertEqual([], self.schema_errors("fact.schema.json", fact_record(field_name="legal_name")))
        lease = {"id": COMPANY_ID, "schema_version": "0.2.0", "entity_type": "lease", "slug": "synthetic-lease", "display_name": "Synthetic lease node", "created_at": "2026-07-28T12:00:00Z", "modified_at": "2026-07-28T12:00:00Z", "record_status": "active", "administrative_notes": None, "customer_id": FACT_ID}
        self.assertTrue(self.schema_errors("lease.schema.json", lease))
        relationship_fact = fact_record(field_name="customer_id", observed_value=FACT_ID)
        self.assertEqual([], self.schema_errors("fact.schema.json", relationship_fact))

    def test_valid_fact_state_combinations(self):
        combinations = [
            ("observed", "verified", "active"), ("estimated", "pending_review", "active"),
            ("observed", "disputed", "active"), ("estimated", "verified", "deprecated"),
        ]
        for classification, verification, lifecycle in combinations:
            extras = {}
            if classification == "estimated":
                extras = {"estimation_method": "Comparable evidence", "estimation_assumptions": ["Comparable scope"]}
            record = fact_record(value_classification=classification, verification_status=verification, lifecycle_status=lifecycle, **extras)
            self.assertEqual([], self.schema_errors("fact.schema.json", record))

    def test_derived_fact_remains_reproducible_when_superseded(self):
        prior = fact_record(value_type="number", observed_value=2.0, unit="unitless")
        derived = fact_record(FACT_ID_2, value_classification="derived", verification_status="verified", lifecycle_status="superseded", value_type="number", observed_value=4.0, unit="unitless", input_fact_ids=[FACT_ID], derivation_method="input * 2", superseded_by_fact_id="323e4567-e89b-42d3-a456-426614174000")
        self.assertEqual([], self.schema_errors("fact.schema.json", derived))

    def test_estimate_preserves_method_when_disputed_or_deprecated(self):
        for verification, lifecycle in [("disputed", "active"), ("verified", "deprecated")]:
            estimate = fact_record(value_classification="estimated", verification_status=verification, lifecycle_status=lifecycle, estimation_method="Peer median", estimation_assumptions=["Comparable scope"])
            self.assertEqual([], self.schema_errors("fact.schema.json", estimate))

    def test_invalid_classification_method_combinations_fail(self):
        self.assert_invalid_fact(derivation_method="x", input_fact_ids=[FACT_ID_2])
        self.assert_invalid_fact(estimation_method="x", estimation_assumptions=["a"])
        self.assert_invalid_fact(value_classification="derived")
        self.assert_invalid_fact(value_classification="estimated")

    def test_typed_values_accept_exact_representations(self):
        valid = [("number", 401.5, "MW"), ("integer", 401, "count"), ("text", "text", None), ("boolean", True, None), ("date", "2026-07-28", None), ("date_time", "2026-07-28T12:00:00Z", None), ("structured", {"lower": 1, "upper": 2}, None)]
        for value_type, value, unit in valid:
            self.assertEqual([], self.schema_errors("fact.schema.json", fact_record(value_type=value_type, observed_value=value, unit=unit)))

    def test_typed_values_reject_mismatches_and_null(self):
        invalid = [("number", "401", "MW"), ("date", "yesterday", None), ("date_time", "tomorrow noon", None), ("boolean", "true", None), ("structured", [1, 2], None), ("text", None, None)]
        for value_type, value, unit in invalid:
            self.assert_invalid_fact(value_type=value_type, observed_value=value, unit=unit)

    def test_numeric_units_are_explicit(self):
        self.assertEqual([], self.schema_errors("fact.schema.json", fact_record(value_type="number", observed_value=0.25, unit="decimal_fraction")))
        self.assertEqual([], self.schema_errors("fact.schema.json", fact_record(value_type="integer", observed_value=3, unit="unitless")))
        self.assert_invalid_fact(value_type="number", observed_value=401, unit=None)

    def test_google_drive_source_metadata_is_valid(self):
        drive = source_record(storage_provider="google_drive", storage_location="Digital Twin/Archive", external_file_id="1AbCdEfSyntheticId", original_filename="test.pdf", media_type="application/pdf", file_size_bytes=1024, cryptographic_hash="a" * 64, hash_algorithm="sha256", archived_at="2026-07-28T13:00:00Z", archive_access_status="restricted")
        self.assertEqual([], self.schema_errors("source.schema.json", drive))

    def test_archive_state_contradictions_fail(self):
        self.assertTrue(self.schema_errors("source.schema.json", source_record(external_file_id="unexpected")))
        incomplete = source_record(storage_provider="google_drive", storage_location="archive", external_file_id="id", original_filename="x.pdf", media_type="application/pdf", file_size_bytes=1, cryptographic_hash=None, hash_algorithm=None, archived_at=None, archive_access_status="private")
        self.assertTrue(self.schema_errors("source.schema.json", incomplete))
        bad_digest = source_record(storage_provider="google_drive", storage_location="archive", external_file_id="id", original_filename="x.pdf", media_type="application/pdf", file_size_bytes=1, cryptographic_hash="a" * 64, hash_algorithm="sha512", archived_at="2026-07-28T13:00:00Z", archive_access_status="private")
        self.assertTrue(self.schema_errors("source.schema.json", bad_digest))

    def test_source_supersession_schema_and_relationships(self):
        self.assertTrue(self.schema_errors("source.schema.json", source_record(status="superseded")))
        old = source_record(status="superseded", superseded_by_source_id=SOURCE_ID_2)
        new = source_record(SOURCE_ID_2, supersedes_source_ids=[SOURCE_ID])
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/source/part-001.jsonl", old, new)
            self.assertEqual([], validate_repository(fixture.root))

    def test_source_self_broken_and_circular_supersession_fail(self):
        cases = [
            [source_record(status="superseded", superseded_by_source_id=SOURCE_ID, supersedes_source_ids=[SOURCE_ID])],
            [source_record(status="superseded", superseded_by_source_id=SOURCE_ID_2, supersedes_source_ids=[SOURCE_ID_2]), source_record(SOURCE_ID_2, status="superseded", superseded_by_source_id=SOURCE_ID, supersedes_source_ids=[SOURCE_ID])],
            [source_record(status="superseded", superseded_by_source_id=SOURCE_ID_2)],
        ]
        for records in cases:
            with RepositoryFixture() as fixture:
                fixture.write_jsonl("canonical/source/part-001.jsonl", *records)
                self.assertTrue(validate_repository(fixture.root))

    def test_fact_immutable_fields_cannot_change_in_place(self):
        prior = fact_record()
        administrative = copy.deepcopy(prior)
        administrative.update(verification_status="disputed", notes="Under review", modified_at="2026-07-29T12:00:00Z")
        self.assertEqual([], validate_fact_revision(prior, administrative))
        revised = copy.deepcopy(prior)
        revised["observed_value"] = "Changed value"
        self.assertTrue(validate_fact_revision(prior, revised))

    def test_provenance_uniqueness_and_typed_references(self):
        self.assertTrue(self.schema_errors("fact.schema.json", fact_record(source_ids=[])))
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", fact_record(source_ids=[SOURCE_ID_2]))
            self.assertTrue(any("broken Source reference" in e for e in validate_repository(fixture.root)))
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation()
            fixture.write_jsonl("canonical/fact/part-001.jsonl", fact_record(), fact_record())
            self.assertTrue(any("duplicate fact ID" in e for e in validate_repository(fixture.root)))
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/source/part-001.jsonl", source_record(), source_record())
            self.assertTrue(any("duplicate source ID" in e for e in validate_repository(fixture.root)))
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/source/part-001.jsonl", source_record())
            fixture.write_jsonl("canonical/fact/part-001.jsonl", fact_record())
            self.assertTrue(any("broken typed entity reference" in e for e in validate_repository(fixture.root)))

    def test_fact_supersession_and_derivation_relationship_failures(self):
        first = fact_record(lifecycle_status="superseded", superseded_by_fact_id=FACT_ID_2, supersedes_fact_ids=[FACT_ID_2])
        second = fact_record(FACT_ID_2, lifecycle_status="superseded", superseded_by_fact_id=FACT_ID, supersedes_fact_ids=[FACT_ID])
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation(); fixture.write_jsonl("canonical/fact/part-001.jsonl", first, second)
            self.assertTrue(any("Circular Fact supersession" in e for e in validate_repository(fixture.root)))
        derived = fact_record(value_classification="derived", value_type="integer", observed_value=1, unit="count", input_fact_ids=[FACT_ID_2], derivation_method="count(inputs)")
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation(); fixture.write_jsonl("canonical/fact/part-001.jsonl", derived)
            self.assertTrue(any("broken input Fact reference" in e for e in validate_repository(fixture.root)))
        prior = fact_record(lifecycle_status="superseded", superseded_by_fact_id=FACT_ID_2)
        replacement = fact_record(FACT_ID_2, field_name="former_name", supersedes_fact_ids=[FACT_ID])
        with RepositoryFixture() as fixture:
            fixture.write_valid_foundation(); fixture.write_jsonl("canonical/fact/part-001.jsonl", prior, replacement)
            self.assertTrue(any("different entity or field" in e for e in validate_repository(fixture.root)))

    def test_unknown_statuses_and_invalid_formats_fail(self):
        self.assert_invalid_fact(value_classification="calculated")
        self.assert_invalid_fact(verification_status="accepted")
        self.assert_invalid_fact(lifecycle_status="deleted")
        errors = self.schema_errors("source.schema.json", source_record(publication_date="yesterday", source_url="not a uri")) + self.schema_errors("fact.schema.json", fact_record(id="not-a-uuid", created_at="bad"))
        self.assertIn("format", {e.validator for e in errors})

    def test_unknown_directories_and_unsupported_files_fail(self):
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/unknown/part-001.jsonl", fact_record())
            self.assertTrue(any("unknown canonical entity directory" in e for e in validate_repository(fixture.root)))
        with RepositoryFixture() as fixture:
            fixture.write_jsonl("canonical/fact/facts.jsonl", fact_record())
            self.assertTrue(any("unsupported canonical filename" in e for e in validate_repository(fixture.root)))


if __name__ == "__main__":
    unittest.main()
