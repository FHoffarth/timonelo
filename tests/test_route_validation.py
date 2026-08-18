import unittest
import os
import json
import jsonschema

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO_ROOT, "knowledge", "schema")
ROUTES_DIR = os.path.join(REPO_ROOT, "knowledge", "routes")


class TestRouteKnowledgeValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema_path = os.path.join(SCHEMA_DIR, "route.schema.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            cls.route_schema = json.load(f)
        cls.validator_cls = jsonschema.validators.validator_for(cls.route_schema)
        cls.validator = cls.validator_cls(cls.route_schema)

    def test_western_med_route_exists_and_validates(self):
        route_path = os.path.join(ROUTES_DIR, "western-mediterranean-7n", "route.json")
        self.assertTrue(os.path.exists(route_path), "western-mediterranean-7n/route.json must exist")

        with open(route_path, "r", encoding="utf-8") as f:
            route_data = json.load(f)

        errors = list(self.validator.iter_errors(route_data))
        if errors:
            msg = "\nValidation errors for western-mediterranean-7n/route.json:\n"
            for err in errors:
                msg += f"  - Path {list(err.path)}: {err.message}\n"
            self.fail(msg)

    def test_relational_canonical_port_ids(self):
        route_path = os.path.join(ROUTES_DIR, "western-mediterranean-7n", "route.json")
        with open(route_path, "r", encoding="utf-8") as f:
            route_data = json.load(f)

        expected_unlocodes = {"ES-BCN", "FR-MRS", "IT-GOA", "IT-NAP", "IT-MSN", "MT-MLA"}
        found_origins = {leg["origin_canonical_id"] for leg in route_data["legs"]}
        found_dests = {leg["destination_canonical_id"] for leg in route_data["legs"]}

        self.assertEqual(found_origins, expected_unlocodes)
        self.assertEqual(found_dests, expected_unlocodes)

        # Check total legs and interporting homeport configuration
        self.assertEqual(len(route_data["legs"]), 8)
        self.assertEqual(route_data["legs"][6]["sea_day"], True)
        self.assertEqual(route_data["legs"][6]["distance_if_known_nm"], 600)


if __name__ == "__main__":
    unittest.main()
