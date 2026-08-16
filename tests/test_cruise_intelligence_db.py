import unittest
import os
import json
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler
from src.timonelo.database.graph import RelationType


class TestCruiseIntelligenceDatabase(unittest.TestCase):
    def setUp(self):
        self.compiler = KnowledgeDBCompiler(REPO_ROOT)
        self.db = self.compiler.compile()
        self.graph = self.compiler.knowledge_graph

    def test_database_structure(self):
        """Verify compiled database structure and statistics."""
        self.assertIn("statistics", self.db)
        self.assertIn("ships", self.db)
        self.assertIn("ports", self.db)
        self.assertIn("routes", self.db)
        self.assertIn("ship_classes", self.db)
        self.assertIn("venues", self.db)
        self.assertEqual(self.db["statistics"]["validation_errors_count"], 0)

    def test_ship_identity_integrity(self):
        """Verify indexed ships have required maritime identifiers."""
        ships = self.db["ships"]
        self.assertIn("msc-bellissima", ships)
        bellissima = ships["msc-bellissima"]
        imo_val = (bellissima.get("imo") or bellissima.get("imo_number", {}))["value"]
        self.assertEqual(imo_val, "9766205")
        self.assertEqual(bellissima["flag_state"]["value"], "Malta")

    def test_port_intelligence_integrity(self):
        """Verify ports have coordinates and official authority provenance."""
        ports = self.db["ports"]
        self.assertIn("genoa", ports)
        self.assertIn("civitavecchia", ports)
        self.assertIn("barcelona", ports)
        self.assertIn("miami", ports)
        
        genoa = ports["genoa"]
        self.assertEqual(genoa["un_locode"], "ITGOA")
        self.assertTrue(genoa["coordinates"]["latitude"] > 40.0)

    def test_knowledge_graph_connectivity(self):
        """Verify Knowledge Graph nodes, edges, and relationship traversal."""
        self.assertGreater(len(self.graph.nodes), 60)
        self.assertGreater(len(self.graph.edges), 90)

        # Verify Ship -> Class relationship
        bellissima_outgoing = self.graph.get_outgoing_edges("ship:msc-bellissima", RelationType.BELONGS_TO)
        self.assertEqual(len(bellissima_outgoing), 1)
        self.assertEqual(bellissima_outgoing[0].target_id, "class:meraviglia-class")

        # Verify Ship -> Calls At Ports
        calls_at = self.graph.get_outgoing_edges("ship:msc-bellissima", RelationType.CALLS_AT)
        called_ports = {e.target_id for e in calls_at}
        self.assertIn("port:genoa", called_ports)
        self.assertIn("port:barcelona", called_ports)

        # Verify Vertical Deck Stack (Deck 15 is ABOVE Deck 14)
        deck_15_above = self.graph.get_outgoing_edges("deck:msc-bellissima:15", RelationType.ABOVE)
        self.assertEqual(deck_15_above[0].target_id, "deck:msc-bellissima:14")

    def test_semantic_search_graph(self):
        """Verify semantic query resolution via graph inverted index."""
        bellissima_results = self.graph.semantic_search("bellissima")
        labels = [n.label for n in bellissima_results]
        self.assertTrue(any("Bellissima" in l for l in labels))

        port_results = self.graph.semantic_search("genoa")
        self.assertTrue(any("Genoa" in n.label for n in port_results))


if __name__ == "__main__":
    unittest.main()
