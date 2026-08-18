import unittest
import os
import json
import jsonschema

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO_ROOT, "knowledge", "schema")
BELLISSIMA_DIR = os.path.join(REPO_ROOT, "knowledge", "ships", "msc-bellissima")


class TestKnowledgeSchemaValidation(unittest.TestCase):
    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_document(self, doc_filename, schema_filename):
        doc_path = os.path.join(BELLISSIMA_DIR, doc_filename)
        schema_path = os.path.join(SCHEMA_DIR, schema_filename)

        self.assertTrue(os.path.exists(doc_path), f"Document {doc_filename} must exist")
        self.assertTrue(os.path.exists(schema_path), f"Schema {schema_filename} must exist")

        doc = self.load_json(doc_path)
        schema = self.load_json(schema_path)

        # Validate with jsonschema Draft 2020-12
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        errors = list(validator.iter_errors(doc))
        if errors:
            msg = f"\nValidation errors in {doc_filename} against {schema_filename}:\n"
            for err in errors:
                msg += f"  - Path {list(err.path)}: {err.message}\n"
            self.fail(msg)

    def test_technical_schema(self):
        self.validate_document("technical.json", "ship.schema.json")

    def test_decks_schema(self):
        self.validate_document("decks.json", "deck.schema.json")

    def test_public_areas_schema(self):
        self.validate_document("public_areas.json", "venue.schema.json")

    def test_restaurants_schema(self):
        self.validate_document("restaurants.json", "restaurant.schema.json")

    def test_bars_schema(self):
        self.validate_document("bars.json", "bar.schema.json")

    def test_lounges_schema(self):
        self.validate_document("lounges.json", "lounge.schema.json")

    def test_pools_schema(self):
        self.validate_document("pools.json", "pool.schema.json")

    def test_spa_schema(self):
        self.validate_document("spa.json", "spa.schema.json")

    def test_sports_schema(self):
        self.validate_document("sports.json", "sport.schema.json")

    def test_entertainment_schema(self):
        self.validate_document("entertainment.json", "entertainment.schema.json")

    def test_muster_schema(self):
        self.validate_document("muster.json", "muster.schema.json")

    def test_cabins_schema(self):
        self.validate_document("cabins.json", "cabin.schema.json")


if __name__ == "__main__":
    unittest.main()
