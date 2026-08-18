import unittest
import os
import json
import jsonschema

from backend.knowledge import KnowledgeRepository

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_DIR = os.path.join(REPO_ROOT, "knowledge", "schema")
INDEX_PATH = os.path.join(REPO_ROOT, "knowledge", "indexes", "relationships.json")


class TestRelationshipIndexes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = KnowledgeRepository()
        schema_path = os.path.join(SCHEMA_DIR, "relationship_graph.schema.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            cls.schema = json.load(f)
        cls.validator_cls = jsonschema.validators.validator_for(cls.schema)
        cls.validator = cls.validator_cls(cls.schema)

    def test_relationship_index_schema_validation(self):
        self.assertTrue(os.path.exists(INDEX_PATH), "relationships.json must exist")
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            index_data = json.load(f)

        errors = list(self.validator.iter_errors(index_data))
        if errors:
            msg = "\nValidation errors for relationships.json:\n"
            for err in errors:
                msg += f"  - Path {list(err.path)}: {err.message}\n"
            self.fail(msg)

    def test_cross_reference_ship_to_routes(self):
        routes = self.repo.getShipRoutes("msc-bellissima")
        self.assertEqual(routes, ["ROUTE_MSC_BELLISSIMA_WMED_7N"])

    def test_cross_reference_route_to_ports(self):
        ports = self.repo.getRoutePorts("ROUTE_MSC_BELLISSIMA_WMED_7N")
        self.assertEqual(ports, ["ES-BCN", "FR-MRS", "IT-GOA", "IT-NAP", "IT-MSN", "MT-MLA"])

    def test_cross_reference_port_to_terminals(self):
        # By UN/LOCODE
        bcn_terms = self.repo.getPortTerminals("ES-BCN")
        self.assertIn("TERM-BCN-ADOSAT-A", bcn_terms)
        self.assertIn("TERM-BCN-ADOSAT-H", bcn_terms)

        # By slug
        mrs_terms = self.repo.getPortTerminals("marseille")
        self.assertEqual(mrs_terms, ["TERM-MRS-MPCT", "TERM-MRS-J4-JOLIETTE"])

        goa_terms = self.repo.getPortTerminals("genoa")
        self.assertIn("TERM-GOA-PONTE-DEI-MILLE", goa_terms)

        nap_terms = self.repo.getPortTerminals("naples")
        self.assertIn("TERM-NAP-STAZIONE-MARITTIMA", nap_terms)

        msn_terms = self.repo.getPortTerminals("messina")
        self.assertEqual(msn_terms, ["TERM-MSN-CROCIERE"])

        mla_terms = self.repo.getPortTerminals("valletta")
        self.assertIn("TERM-MLA-VALLETTA-WATERFRONT", mla_terms)

    def test_end_to_end_graph_traversal(self):
        """Traverse Ship -> Routes -> Ports -> Terminals without data duplication."""
        ship_id = "msc-bellissima"
        routes = self.repo.getShipRoutes(ship_id)
        self.assertTrue(len(routes) > 0)

        all_terminal_ids = []
        for r_id in routes:
            ports = self.repo.getRoutePorts(r_id)
            self.assertEqual(len(ports), 6)
            for p_unlocode in ports:
                terms = self.repo.getPortTerminals(p_unlocode)
                self.assertTrue(len(terms) > 0)
                all_terminal_ids.extend(terms)

        # Verified total distinct terminals resolved along Bellissima's circuit
        self.assertGreaterEqual(len(set(all_terminal_ids)), 17)


if __name__ == "__main__":
    unittest.main()
