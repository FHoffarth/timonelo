"""
Unit tests for MS Andorinha Universal River Vessel Ontology (Douro River Class).
Verifies Plane 1-6 determinism, spatial integrity, Dijkstra multi-deck circulation, and Plane 6 briefing.
"""

import unittest
from timonelo.ontology.andorinha import create_andorinha_ontology
from timonelo.factory.validator import SpatialIntegrityValidator
from timonelo.calculus.router import DeterministicSpatialRouter
from timonelo.calculus.sandwich import DeterministicSandwichResolver
from timonelo.calculus.sightlines import DeterministicSightlineCalculator
from timonelo.lenses.accessibility import AccessibilityLens
from timonelo.lenses.quiet import QuietCabinLens
from timonelo.intelligence import CruiseBriefingSynthesizer, CruiseBriefing


class TestAndorinhaUniversalRiverVessel(unittest.TestCase):
    def setUp(self):
        self.andorinha = create_andorinha_ontology()

    def test_vessel_metadata(self):
        self.assertEqual(self.andorinha.name, "MS Andorinha")
        self.assertEqual(self.andorinha.imo_number, "ENI02338573")
        self.assertEqual(self.andorinha.ship_class, "Douro River Class")
        self.assertEqual(self.andorinha.length_overall_meters, 80.0)
        self.assertEqual(self.andorinha.beam_meters, 11.4)
        self.assertEqual(self.andorinha.total_decks, 4)

    def test_quality_gates_pass_100_percent(self):
        report = SpatialIntegrityValidator.audit_vessel(self.andorinha)
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.issues), 0)
        self.assertIn("GATE_1_PROVENANCE_SATISFIED", report.quality_gates_passed)
        self.assertIn("GATE_2_TOPOLOGY_ZERO_ORPHANS", report.quality_gates_passed)
        self.assertIn("GATE_3_SANDWICH_INTEGRITY", report.quality_gates_passed)
        self.assertIn("GATE_4_CIRCULATION_CONNECTED", report.quality_gates_passed)

    def test_stateroom_counts_and_distribution(self):
        total_cabins = sum(len(d.cabins) for d in self.andorinha.decks.values())
        self.assertEqual(total_cabins, 42)
        # Deck 1 (Emerald): 4 cabins
        self.assertEqual(len(self.andorinha.decks[1].cabins), 4)
        # Deck 2 (Ruby): 22 cabins
        self.assertEqual(len(self.andorinha.decks[2].cabins), 22)
        # Deck 3 (Diamond): 16 cabins
        self.assertEqual(len(self.andorinha.decks[3].cabins), 16)
        # Deck 4 (Sun Deck): 0 cabins
        self.assertEqual(len(self.andorinha.decks[4].cabins), 0)

    def test_diamond_suite_spatial_calculus(self):
        # Test Diamond Suite 301 (Deck 3 Port Forward Master Suite)
        suite = self.andorinha.decks[3].cabins["301"]
        self.assertEqual(suite.category_code, "DSU")
        self.assertEqual(suite.square_meters, 28.0)
        self.assertTrue(suite.is_accessible_stateroom)
        self.assertEqual(suite.door.clear_width_mm, 950)

        # Multi-deck Dijkstra Routing to Compass Rose Restaurant (Deck 2)
        router = DeterministicSpatialRouter(self.andorinha)
        route = router.find_shortest_path("D03_CORRIDOR_FWD", "D02_RESTAURANT_COMPASS")
        self.assertIsNotNone(route)
        self.assertTrue(route.total_distance_meters > 0)
        self.assertTrue(route.is_fully_step_free)

    def test_vertical_sandwich_resolution(self):
        sandwich_resolver = DeterministicSandwichResolver(self.andorinha)
        # Ruby Deck cabin 205
        report = sandwich_resolver.resolve_cabin_sandwich("205")
        self.assertIsNotNone(report)
        self.assertIsNotNone(report.overhead_layer)
        self.assertEqual(report.overhead_layer.deck_name, "Diamond Deck")

    def test_plane_6_cruise_briefing_andorinha(self):
        """Ship-derived sections render; volatile sections read UNKNOWN.

        This test previously supplied a port_override dict and asserted the
        values came back. Override dicts bypassed the evidence chain entirely:
        a value handed in at call time carried no artifact, no locator and no
        review. Sourced port data must now enter through the Truth Engine.
        """
        briefing = CruiseBriefingSynthesizer.generate_briefing(
            ontology=self.andorinha,
            cabin_number="301",
        )
        self.assertIsNotNone(briefing)
        self.assertIsInstance(briefing, CruiseBriefing)
        self.assertEqual(briefing.ship_name, "MS Andorinha")
        self.assertEqual(briefing.cabin_intelligence.cabin_number, "301")
        self.assertEqual(briefing.cabin_intelligence.deck_name, "Diamond Deck")
        self.assertIsNone(briefing.port_intelligence)
        self.assertIsNone(briefing.weather_intelligence)


if __name__ == "__main__":
    unittest.main()
