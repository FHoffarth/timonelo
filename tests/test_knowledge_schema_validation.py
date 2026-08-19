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

    def test_tier1_all_knowledge_ships_validate(self):
        """Tier 1: Dynamic traversal validating all ships in knowledge/ships/ against canonical schemas."""
        ships_dir = os.path.join(REPO_ROOT, "knowledge", "ships")
        if not os.path.exists(ships_dir):
            return
        mapping = {
            "technical.json": "ship.schema.json",
            "decks.json": "deck.schema.json",
            "public_areas.json": "venue.schema.json",
            "restaurants.json": "restaurant.schema.json",
            "bars.json": "bar.schema.json",
            "lounges.json": "lounge.schema.json",
            "pools.json": "pool.schema.json",
            "spa.json": "spa.schema.json",
            "sports.json": "sport.schema.json",
            "entertainment.json": "entertainment.schema.json",
            "muster.json": "muster.schema.json",
            "cabins.json": "cabin.schema.json",
        }
        for ship_slug in os.listdir(ships_dir):
            s_path = os.path.join(ships_dir, ship_slug)
            if not os.path.isdir(s_path):
                continue
            for doc_name, schema_name in mapping.items():
                file_path = os.path.join(s_path, doc_name)
                if os.path.exists(file_path):
                    schema_path = os.path.join(SCHEMA_DIR, schema_name)
                    doc = self.load_json(file_path)
                    schema = self.load_json(schema_path)
                    validator_cls = jsonschema.validators.validator_for(schema)
                    validator = validator_cls(schema)
                    errors = list(validator.iter_errors(doc))
                    self.assertEqual(errors, [], f"Schema validation errors in {file_path}")

    def test_tier2_staging_data_structural_validation(self):
        """Tier 2: Staging data structure validation for data/ directory."""
        data_dir = os.path.join(REPO_ROOT, "data")
        db_path = os.path.join(data_dir, "cruise_intelligence_db.json")
        graph_path = os.path.join(data_dir, "cruise_knowledge_graph.json")

        self.assertTrue(os.path.exists(db_path), "Master database must exist")
        self.assertTrue(os.path.exists(graph_path), "Master graph must exist")

        db = self.load_json(db_path)
        self.assertIn("ships", db)
        self.assertIn("ports", db)
        self.assertIsInstance(db["ships"], dict)
        self.assertIsInstance(db["ports"], dict)

        graph = self.load_json(graph_path)
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)

    def test_tier3_legacy_frontend_fixtures_structural_validation(self):
        """Tier 3: Legacy fixture structural validation for frontend/src/data/."""
        frontend_data_dir = os.path.join(REPO_ROOT, "frontend", "src", "data")
        if not os.path.exists(frontend_data_dir):
            return

        for fname in os.listdir(frontend_data_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(frontend_data_dir, fname)
            doc = self.load_json(fpath)
            self.assertIsInstance(doc, (dict, list), f"{fname} must be valid JSON object/array")

            # Validate specific required structure per fixture
            if "semantic_vessel" in fname:
                self.assertIn("vessel_id", doc)
                self.assertIn("decks", doc)
                for d in doc["decks"]:
                    self.assertIn("deck_level", d)
                    self.assertIn("objects", d)
            elif "living_decks" in fname:
                self.assertIn("decks", doc)
                self.assertIn("ship_name", doc)
            elif "twin" in fname:
                self.assertIn("decks", doc)
                self.assertIn("ship", doc)

    def test_invalid_canonical_enum_fails_schema_validation(self):
        """Tier 1 negative test: invalid enum value must fail schema validation."""
        schema_path = os.path.join(SCHEMA_DIR, "deck.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        invalid_doc = [{
            "deck_number": 5,
            "name": "Invalid Deck",
            "is_passenger_accessible": True,
            "has_cabins": False,
            "has_public_venues": True,
            "vertical_transport_hubs": 2,
            "muster_station_count": 1,
            "lifeboat_embarkation_deck": False,
            "zones": ["MIDSHIP"],
            "elevation_m": 12.5,
            "evidence_links": [{
                "source_id": "SRC-1",
                "locator": "p1",
                "method": "INVALID_METHOD_ENUM_VALUE"
            }]
        }]
        errors = list(validator.iter_errors(invalid_doc))
        self.assertTrue(len(errors) > 0, "Invalid enum value must fail validation")
