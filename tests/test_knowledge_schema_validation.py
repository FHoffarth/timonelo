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

        invalid_doc = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "test-source"},
            "decks": [{
                "id": "DECK-05",
                "name": "Deck 5",
                "deck_number": 5,
                "category": "INVALID_CATEGORY_ENUM",
                "description": "Invalid category test",
                "passenger_accessible": True,
                "source": "test-source",
                "provenance": "page:1",
                "tags": ["test"]
            }]
        }
        errors = list(validator.iter_errors(invalid_doc))
        self.assertTrue(len(errors) > 0, "Invalid enum value must fail validation")

    def test_negative_confidence_field_forbidden_by_schema(self):
        """Task E.2: canonical knowledge containing stored confidence fails validation."""
        schema_path = os.path.join(SCHEMA_DIR, "deck.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        doc_with_confidence = {
            "vessel_id": "test-vessel",
            "provenance": {
                "source_artifact": "test-source",
                "confidence": 1.0  # Forbidden in modernized schema!
            },
            "decks": [{
                "id": "DECK-05",
                "name": "Deck 5",
                "deck_number": 5,
                "category": "STATEROOM_DECK",
                "description": "Deck 5 description",
                "passenger_accessible": True,
                "source": "test-source",
                "provenance": "page:1",
                "tags": ["test"]
            }]
        }
        errors = list(validator.iter_errors(doc_with_confidence))
        self.assertTrue(len(errors) > 0, "Document with stored confidence must fail schema validation")

    def test_negative_ship_schema_may_omit_technical_fields(self):
        """Task E.3-7: ship knowledge may omit IMO, GT, builder, dimensions, capacities without dummy values."""
        schema_path = os.path.join(SCHEMA_DIR, "ship.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        # Partially evidenced vessel: has identity and provenance, but no technical specs
        minimal_doc = {
            "vessel_id": "msc-partially-evidenced",
            "vessel_name": "MSC Partially Evidenced",
            "provenance": {
                "source_artifact": "Official Deckplans PDF"
            }
        }
        errors = list(validator.iter_errors(minimal_doc))
        self.assertEqual(errors, [], "Partially evidenced ship with omitted technical_specifications must validate")

        # Has technical_specifications with only class, omitting IMO, GT, dimensions, builder, capacities
        partial_tech_doc = {
            "vessel_id": "msc-partially-evidenced",
            "vessel_name": "MSC Partially Evidenced",
            "provenance": {
                "source_artifact": "Official Deckplans PDF"
            },
            "technical_specifications": {
                "class": "Meraviglia-class"
            }
        }
        errors_partial = list(validator.iter_errors(partial_tech_doc))
        self.assertEqual(errors_partial, [], "Ship with omitted IMO, GT, builder must validate")

    def test_negative_invalid_technical_values_still_fail_validation(self):
        """Task E.8: when technical fields are present, invalid values/types still fail validation."""
        schema_path = os.path.join(SCHEMA_DIR, "ship.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        invalid_imo_doc = {
            "vessel_id": "test-ship",
            "vessel_name": "Test Ship",
            "provenance": {"source_artifact": "test"},
            "technical_specifications": {
                "imo_number": 99  # Invalid IMO: minimum is 1000000
            }
        }
        errors = list(validator.iter_errors(invalid_imo_doc))
        self.assertTrue(len(errors) > 0, "Invalid IMO value must fail schema validation")

    def test_schema_valid_does_not_imply_evidence_valid(self):
        """Task E.10: schema validity does not imply evidence/gatekeeper validity."""
        # A schema-valid document with unevidenced facts can be validated by schema,
        # but must be rejected by EvidenceGatekeeper when evaluated fail-closed.
        from timonelo.evidence.gatekeeper import EvidenceGatekeeper
        from timonelo.evidence.engine import Statement
        from timonelo.ontology.models import Method, Derivation, EvidenceCondition, HumanReviewState, PublishStatus

        gk = EvidenceGatekeeper()
        # Statement has schema-like fact, but is UNKNOWN
        gk.add_statement(Statement(
            statement_id="stmt-test",
            entity_id="test-ship",
            question_id="ship.imo",
            value=9760512,
            method=Method.INFERRED,
            derivation=Derivation.REFERENCE_MODEL,
            evidence_condition=EvidenceCondition.UNKNOWN,
            human_review_state=HumanReviewState.DRAFT,
            publish_status=PublishStatus.PUBLISH_BLOCKED,
        ))
        res = gk.evaluate_publish_gate()
        self.assertEqual(res.status, PublishStatus.PUBLISH_BLOCKED)
