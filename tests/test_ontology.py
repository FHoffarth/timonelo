"""
Unit tests for Plane 2 Spatial Ontology (ADR-0001).
"""

import unittest
from src.timonelo.ontology.bellissima import create_bellissima_ontology
from src.timonelo.ontology.models import HullSide, BalconyType, VenueCategory


class TestSpatialOntology(unittest.TestCase):
    def setUp(self):
        self.ontology = create_bellissima_ontology()

    def test_vessel_metadata(self):
        self.assertEqual(self.ontology.imo_number, "IMO9766205")
        self.assertEqual(self.ontology.name, "MSC Bellissima")
        self.assertEqual(self.ontology.ship_class, "Meraviglia Class")
        self.assertEqual(self.ontology.length_overall_meters, 315.83)
        self.assertEqual(self.ontology.beam_meters, 43.0)

    def test_deck_structure(self):
        self.assertIn(14, self.ontology.decks)
        self.assertIn(15, self.ontology.decks)
        self.assertIn(6, self.ontology.decks)
        
        deck14 = self.ontology.decks[14]
        self.assertEqual(deck14.name, "Girasole")
        self.assertEqual(deck14.elevation_meters, 42.0)

    def test_cabin_14122_fixtures(self):
        deck14 = self.ontology.decks[14]
        self.assertIn("14122", deck14.cabins)
        cabin = deck14.cabins["14122"]
        
        self.assertEqual(cabin.cabin_number, "14122")
        self.assertEqual(cabin.deck_number, 14)
        self.assertEqual(cabin.hull_side, HullSide.STARBOARD)
        self.assertEqual(cabin.balcony_type, BalconyType.UNOBSTRUCTED)
        self.assertEqual(cabin.connecting_cabin_number, "14120")
        self.assertTrue(cabin.bed_near_balcony)
        self.assertFalse(cabin.is_accessible_stateroom)
        self.assertEqual(cabin.sockets.eu_standard_count, 2)
        self.assertEqual(cabin.sockets.us_standard_count, 2)
        self.assertEqual(cabin.sockets.usb_a_count, 2)
        self.assertEqual(cabin.sockets.usb_c_count, 1)

    def test_accessible_cabin_14121(self):
        deck14 = self.ontology.decks[14]
        self.assertIn("14121", deck14.cabins)
        cabin = deck14.cabins["14121"]
        
        self.assertEqual(cabin.hull_side, HullSide.PORT)
        self.assertTrue(cabin.is_accessible_stateroom)
        self.assertEqual(cabin.door.clear_width_mm, 950)


if __name__ == "__main__":
    unittest.main()
