import unittest
import os
import json
import jsonschema

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO_ROOT, "knowledge", "schema")
PORTS_DIR = os.path.join(REPO_ROOT, "knowledge", "ports")

EXPECTED_PORTS = ["barcelona", "marseille", "genoa", "naples", "messina", "valletta"]
EXPECTED_FILES = [
    "port.json",
    "transport.json",
    "emergency.json",
    "medical.json",
    "weather.json",
    "sustainability.json",
]


class TestPortKnowledgeValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema_path = os.path.join(SCHEMA_DIR, "port.schema.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            cls.port_schema = json.load(f)
        cls.validator_cls = jsonschema.validators.validator_for(cls.port_schema)
        cls.validator = cls.validator_cls(cls.port_schema)

    def test_all_ports_and_files_exist(self):
        for port_id in EXPECTED_PORTS:
            port_dir = os.path.join(PORTS_DIR, port_id)
            self.assertTrue(os.path.isdir(port_dir), f"Directory for port '{port_id}' must exist")

            for filename in EXPECTED_FILES:
                filepath = os.path.join(port_dir, filename)
                self.assertTrue(os.path.exists(filepath), f"File '{port_id}/{filename}' must exist")

    def test_port_json_schema_validation(self):
        for port_id in EXPECTED_PORTS:
            filepath = os.path.join(PORTS_DIR, port_id, "port.json")
            with open(filepath, "r", encoding="utf-8") as f:
                port_data = json.load(f)

            errors = list(self.validator.iter_errors(port_data))
            if errors:
                err_msg = f"\nValidation errors for {port_id}/port.json:\n"
                for err in errors:
                    err_msg += f"  - Path {list(err.path)}: {err.message}\n"
                self.fail(err_msg)

    def test_entity_provenance_and_metadata_completeness(self):
        """Ensure every sub-entity in port files has id, name, source, provenance, confidence, tags."""
        for port_id in EXPECTED_PORTS:
            port_dir = os.path.join(PORTS_DIR, port_id)

            # Check emergency.json
            with open(os.path.join(port_dir, "emergency.json"), "r", encoding="utf-8") as f:
                em_data = json.load(f)
                for item in em_data.get("emergency_numbers", []):
                    self.assertIn("id", item)
                    self.assertIn("name", item)
                    self.assertIn("source", item)
                    self.assertIn("provenance", item)
                    self.assertNotIn("confidence", item)
                    self.assertIn("tags", item)

            # Check medical.json
            with open(os.path.join(port_dir, "medical.json"), "r", encoding="utf-8") as f:
                med_data = json.load(f)
                for item in med_data.get("medical_facilities", []):
                    self.assertIn("id", item)
                    self.assertIn("name", item)
                    self.assertIn("source", item)
                    self.assertIn("provenance", item)
                    self.assertNotIn("confidence", item)
                    self.assertIn("tags", item)


if __name__ == "__main__":
    unittest.main()
