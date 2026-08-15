"""
Unit tests for Plane 3 Spatial Calculus Engine (ADR-0001).
"""

import unittest
from src.timonelo.ontology.bellissima import create_bellissima_ontology
from src.timonelo.calculus.router import DeterministicSpatialRouter
from src.timonelo.calculus.sandwich import DeterministicSandwichResolver
from src.timonelo.calculus.sightlines import DeterministicSightlineCalculator


class TestSpatialCalculus(unittest.TestCase):
    def setUp(self):
        self.ontology = create_bellissima_ontology()
        self.router = DeterministicSpatialRouter(self.ontology)
        self.sandwich_resolver = DeterministicSandwichResolver(self.ontology)
        self.sightline_calc = DeterministicSightlineCalculator(self.ontology)

    def test_horizontal_routing_same_deck(self):
        # Route from Door 14122 to Aft Elevator lobby on Deck 14
        route = self.router.find_shortest_path("D14_AFT_CORR_STBD_1", "D14_AFT_LIFT")
        self.assertIsNotNone(route)
        self.assertEqual(route.total_distance_meters, 12.5)
        self.assertTrue(route.is_fully_step_free)
        self.assertEqual(route.estimated_step_count, 17)

    def test_multi_deck_vertical_routing(self):
        # Route from Cabin 14122 (Deck 14) to Marketplace Buffet on Deck 15
        route = self.router.find_shortest_path("D14_AFT_CORR_STBD_1", "D15_BUFFET_ENTRANCE")
        self.assertIsNotNone(route)
        # 12.5m (corr to lift) + 3.5m (vert lift Deck 14->15) + 10.0m (lift to buffet) = 26.0m
        self.assertEqual(route.total_distance_meters, 26.0)
        self.assertTrue(route.is_fully_step_free)
        self.assertGreater(len(route.steps), 1)

    def test_vertical_sandwich_resolution(self):
        report = self.sandwich_resolver.resolve_cabin_sandwich("14122")
        self.assertIsNotNone(report)
        self.assertEqual(report.cabin_deck_number, 14)
        
        # Overhead is Deck 15 (Marketplace Buffet area)
        self.assertIsNotNone(report.overhead_layer)
        self.assertEqual(report.overhead_layer.deck_number, 15)
        self.assertIn("Marketplace Buffet", report.overhead_layer.intersecting_venues)
        self.assertTrue(report.overhead_layer.is_active_noise_generator)

    def test_sightline_calculation(self):
        report = self.sightline_calc.calculate_sightline("14122")
        self.assertEqual(report.horizon_view_angle_degrees, 180.0)
        self.assertFalse(report.has_lifeboat_obstruction)


if __name__ == "__main__":
    unittest.main()
