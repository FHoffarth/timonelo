"""
Unit tests for Plane 4 Contextual Lenses (ADR-0001).
"""

import unittest
from src.timonelo.ontology.bellissima import create_bellissima_ontology
from src.timonelo.calculus.router import DeterministicSpatialRouter
from src.timonelo.calculus.sandwich import DeterministicSandwichResolver
from src.timonelo.lenses.accessibility import AccessibilityLens
from src.timonelo.lenses.family import FamilyLens
from src.timonelo.lenses.quiet import QuietCabinLens


class TestContextualLenses(unittest.TestCase):
    def setUp(self):
        self.ontology = create_bellissima_ontology()
        self.router = DeterministicSpatialRouter(self.ontology)
        self.sandwich_resolver = DeterministicSandwichResolver(self.ontology)

    def test_accessibility_lens(self):
        # 14121 is certified accessible
        eval_acc = AccessibilityLens.evaluate(self.ontology, self.router, "14121")
        self.assertIsNotNone(eval_acc)
        self.assertTrue(eval_acc.is_accessible_certified)
        self.assertEqual(eval_acc.door_clear_width_mm, 950)
        self.assertEqual(eval_acc.nearest_elevator_distance_meters, 12.5)

        # 14122 is standard stateroom
        eval_std = AccessibilityLens.evaluate(self.ontology, self.router, "14122")
        self.assertIsNotNone(eval_std)
        self.assertFalse(eval_std.is_accessible_certified)
        self.assertEqual(eval_std.door_clear_width_mm, 850)

    def test_family_lens(self):
        # 14122 connects to 14120
        eval_fam = FamilyLens.evaluate(self.ontology, self.router, "14122")
        self.assertIsNotNone(eval_fam)
        self.assertTrue(eval_fam.has_connecting_door)
        self.assertEqual(eval_fam.connecting_cabin_number, "14120")
        self.assertTrue(eval_fam.is_family_optimized)
        self.assertIsNotNone(eval_fam.kids_club_route)

    def test_quiet_cabin_lens(self):
        # 14122 sits under Marketplace Buffet (Active noise generator)
        eval_quiet = QuietCabinLens.evaluate(self.ontology, self.sandwich_resolver, self.router, "14122")
        self.assertIsNotNone(eval_quiet)
        self.assertFalse(eval_quiet.is_quiet_tier)
        self.assertTrue(any("Overhead venue" in f for f in eval_quiet.acoustic_flags))


if __name__ == "__main__":
    unittest.main()
