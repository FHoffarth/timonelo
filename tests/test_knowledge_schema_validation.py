import unittest
import os
import json
import jsonschema

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO_ROOT, "knowledge", "schema")
BELLISSIMA_DIR = os.path.join(REPO_ROOT, "knowledge", "ships", "msc-bellissima")


def strip_legacy_unmigrated_confidence(obj):
    """Helper for reading legacy unmigrated datasets without modifying files on disk."""
    if isinstance(obj, dict):
        return {k: strip_legacy_unmigrated_confidence(v) for k, v in obj.items() if k != "confidence"}
    elif isinstance(obj, list):
        return [strip_legacy_unmigrated_confidence(item) for item in obj]
    return obj


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
        # Handle unmigrated legacy dataset files on disk
        clean_doc = strip_legacy_unmigrated_confidence(doc)
        schema = self.load_json(schema_path)

        # Validate with jsonschema Draft 2020-12
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        errors = list(validator.iter_errors(clean_doc))
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

    def test_cabins_schema_validates_when_summary_optional_fields_are_absent(self):
        """TASK E: Verify cabin schema validates when balcony_percentage and standard_amenities are absent."""
        schema_path = os.path.join(SCHEMA_DIR, "cabin.schema.json")
        schema = self.load_json(schema_path)
        validator = jsonschema.validators.validator_for(schema)(schema)

        doc = {
            "vessel_id": "test-vessel",
            "provenance": {
                "source_artifact": "Test Artifact"
            },
            "summary": {
                "total_staterooms": 2214,
                "distinct_categories_count": 22
            },
            "cabin_categories": []
        }
        errors = list(validator.iter_errors(doc))
        self.assertEqual(errors, [], "Cabins doc without balcony_percentage and standard_amenities must validate cleanly")

    def test_cabins_schema_validates_when_summary_optional_fields_are_present_and_typed(self):
        """TASK D: Verify cabin schema validates when balcony_percentage and standard_amenities are present and typed."""
        schema_path = os.path.join(SCHEMA_DIR, "cabin.schema.json")
        schema = self.load_json(schema_path)
        validator = jsonschema.validators.validator_for(schema)(schema)

        doc = {
            "vessel_id": "test-vessel",
            "provenance": {
                "source_artifact": "Test Artifact"
            },
            "summary": {
                "total_staterooms": 2214,
                "distinct_categories_count": 22,
                "balcony_percentage": 75.0,
                "standard_amenities": [
                    "Doppelbett umstellbar zu zwei Einzelbetten (ausgenommen IS, YC3)"
                ]
            },
            "cabin_categories": []
        }
        errors = list(validator.iter_errors(doc))
        self.assertEqual(errors, [], "Cabins doc with valid typed optional fields must validate cleanly")

    def test_cabins_schema_rejects_invalid_balcony_percentage_or_amenities(self):
        """TASK D: Verify cabin schema rejects invalid balcony_percentage or standard_amenities."""
        schema_path = os.path.join(SCHEMA_DIR, "cabin.schema.json")
        schema = self.load_json(schema_path)
        validator = jsonschema.validators.validator_for(schema)(schema)

        # Invalid balcony percentage (> 100)
        doc_bad_pct = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "Test"},
            "summary": {
                "total_staterooms": 2214,
                "distinct_categories_count": 22,
                "balcony_percentage": 105.0
            },
            "cabin_categories": []
        }
        errors = list(validator.iter_errors(doc_bad_pct))
        self.assertTrue(len(errors) > 0, "balcony_percentage > 100 must be rejected")

        # Invalid standard_amenities (string instead of array of strings)
        doc_bad_amenities = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "Test"},
            "summary": {
                "total_staterooms": 2214,
                "distinct_categories_count": 22,
                "standard_amenities": "not an array"
            },
            "cabin_categories": []
        }
        errors = list(validator.iter_errors(doc_bad_amenities))
        self.assertTrue(len(errors) > 0, "non-array standard_amenities must be rejected")

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
                    clean_doc = strip_legacy_unmigrated_confidence(doc)
                    schema = self.load_json(schema_path)
                    validator_cls = jsonschema.validators.validator_for(schema)
                    validator = validator_cls(schema)
                    errors = list(validator.iter_errors(clean_doc))
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
        """Task D: canonical knowledge schemas explicitly prohibit confidence and confidence_score.

        This test uses the actual committed schema files without any mutation or injection.
        The schemas use JSON Schema Draft 2020-12 property-specific prohibition:
          "confidence": false, "confidence_score": false
        inside the properties dict of each canonical factual object scope.
        """
        # Part 1: audit all 16 schemas — confidence must not appear in any required array
        for fname in os.listdir(SCHEMA_DIR):
            if not fname.endswith(".json"):
                continue
            schema = self.load_json(os.path.join(SCHEMA_DIR, fname))

            def check_no_conf_required(obj, _fname=fname):
                if isinstance(obj, dict):
                    if "required" in obj:
                        self.assertNotIn(
                            "confidence", obj["required"],
                            f"confidence in required of {_fname}"
                        )
                        self.assertNotIn(
                            "confidence_score", obj["required"],
                            f"confidence_score in required of {_fname}"
                        )
                    for v in obj.values():
                        check_no_conf_required(v)
                elif isinstance(obj, list):
                    for item in obj:
                        check_no_conf_required(item)

            check_no_conf_required(schema)

        # Part 2: prove the ACTUAL committed deck.schema.json rejects confidence fields.
        # NO schema mutation. NO additionalProperties injection. Real schema only.
        schema_path = os.path.join(SCHEMA_DIR, "deck.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        real_validator = validator_cls(schema)

        # 2a. Clean doc with no confidence fields — must pass.
        clean_doc = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "test-source"},
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
        clean_errors = list(real_validator.iter_errors(clean_doc))
        self.assertEqual(
            clean_errors, [],
            f"Clean document must pass the actual schema but got: {clean_errors}"
        )

        # 2b. provenance.confidence — must be REJECTED by the actual schema.
        doc_prov_conf = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "test-source", "confidence": 1.0},
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
        prov_conf_errors = list(real_validator.iter_errors(doc_prov_conf))
        self.assertTrue(
            len(prov_conf_errors) > 0,
            "Actual deck.schema.json must reject provenance.confidence — "
            "schema property prohibition ('confidence': false) is not working"
        )

        # 2c. item-level confidence — must be REJECTED by the actual schema.
        doc_item_conf = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "test-source"},
            "decks": [{
                "id": "DECK-05",
                "name": "Deck 5",
                "deck_number": 5,
                "category": "STATEROOM_DECK",
                "description": "Deck 5 description",
                "passenger_accessible": True,
                "source": "test-source",
                "provenance": "page:1",
                "tags": ["test"],
                "confidence": 1.0
            }]
        }
        item_conf_errors = list(real_validator.iter_errors(doc_item_conf))
        self.assertTrue(
            len(item_conf_errors) > 0,
            "Actual deck.schema.json must reject deck item confidence — "
            "schema property prohibition ('confidence': false) is not working"
        )

        # 2d. item-level confidence_score — must be REJECTED by the actual schema.
        doc_item_cs = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "test-source"},
            "decks": [{
                "id": "DECK-05",
                "name": "Deck 5",
                "deck_number": 5,
                "category": "STATEROOM_DECK",
                "description": "Deck 5 description",
                "passenger_accessible": True,
                "source": "test-source",
                "provenance": "page:1",
                "tags": ["test"],
                "confidence_score": 0.9
            }]
        }
        item_cs_errors = list(real_validator.iter_errors(doc_item_cs))
        self.assertTrue(
            len(item_cs_errors) > 0,
            "Actual deck.schema.json must reject deck item confidence_score — "
            "schema property prohibition ('confidence_score': false) is not working"
        )

        # 2e. provenance.confidence_score — must also be REJECTED.
        doc_prov_cs = {
            "vessel_id": "test-vessel",
            "provenance": {"source_artifact": "test-source", "confidence_score": 0.9},
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
        prov_cs_errors = list(real_validator.iter_errors(doc_prov_cs))
        self.assertTrue(
            len(prov_cs_errors) > 0,
            "Actual deck.schema.json must reject provenance.confidence_score — "
            "schema property prohibition ('confidence_score': false) is not working"
        )

    def test_negative_ship_schema_optional_technical_fields(self):
        """Task D.3-7: ship knowledge may omit technical_specifications, IMO, GT, builder, dimensions, capacities."""
        schema_path = os.path.join(SCHEMA_DIR, "ship.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        # 1. technical_specifications completely absent
        minimal_doc = {
            "vessel_id": "msc-partially-evidenced",
            "vessel_name": "MSC Partially Evidenced",
            "provenance": {
                "source_artifact": "Official Deckplans PDF"
            }
        }
        self.assertEqual(list(validator.iter_errors(minimal_doc)), [], "Ship omitting technical_specifications must validate")

        # 2. technical_specifications present but omitting IMO, GT, builder, dimensions, capacities
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
        self.assertEqual(list(validator.iter_errors(partial_tech_doc)), [], "Ship omitting IMO/GT/builder must validate")

        # 3. dimensions present with only length, omitting beam and draft
        partial_dims_doc = {
            "vessel_id": "msc-partially-evidenced",
            "vessel_name": "MSC Partially Evidenced",
            "provenance": {
                "source_artifact": "Official Deckplans PDF"
            },
            "technical_specifications": {
                "dimensions": {
                    "length_meters": 315.83
                }
            }
        }
        self.assertEqual(list(validator.iter_errors(partial_dims_doc)), [], "Ship with partial dimensions must validate")

    def test_negative_invalid_technical_values_still_fail(self):
        """Task D.8: invalid present technical values still fail validation."""
        schema_path = os.path.join(SCHEMA_DIR, "ship.schema.json")
        schema = self.load_json(schema_path)
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)

        # Invalid IMO: too small
        invalid_imo = {
            "vessel_id": "test-ship",
            "vessel_name": "Test Ship",
            "provenance": {"source_artifact": "test"},
            "technical_specifications": {
                "imo_number": 99
            }
        }
        self.assertTrue(len(list(validator.iter_errors(invalid_imo))) > 0, "IMO < 1000000 must fail")

        # Invalid GT: negative
        invalid_gt = {
            "vessel_id": "test-ship",
            "vessel_name": "Test Ship",
            "provenance": {"source_artifact": "test"},
            "technical_specifications": {
                "tonnage_gt": -500
            }
        }
        self.assertTrue(len(list(validator.iter_errors(invalid_gt))) > 0, "Negative tonnage must fail")

    def test_schema_valid_does_not_imply_evidence_valid(self):
        """Task D.9: schema validity does not imply evidence/gatekeeper validity."""
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
