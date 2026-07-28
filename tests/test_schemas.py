import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METADATA = {"id", "created_at", "modified_at", "source_ids", "confidence_score", "status", "notes"}

class SchemaContractTests(unittest.TestCase):
    def test_entity_contracts(self):
        paths = [p for p in (ROOT / "schemas").glob("*.schema.json") if p.name != "common.schema.json"]
        self.assertEqual(10, len(paths))
        for path in paths:
            schema = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(schema=path.name):
                self.assertTrue(METADATA <= set(schema["properties"]))
                self.assertTrue(METADATA <= set(schema["required"]))
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual("0.1.0", schema["properties"]["schema_version"]["const"])

    def test_unique_schema_ids(self):
        ids = [json.loads(p.read_text(encoding="utf-8"))["$id"] for p in (ROOT / "schemas").glob("*.schema.json")]
        self.assertEqual(len(ids), len(set(ids)))

if __name__ == "__main__":
    unittest.main()
