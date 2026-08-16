import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.safety_intelligence import (
    SafetyIntelligenceEngine,
    CurrentLocationType,
    ShipSide,
)


class TestSafetyIntelligence(unittest.TestCase):
    def test_muster_station_assignment_cabin_14122(self):
        """Verify cabin 14122 (Aft Deck 14) is assigned to Muster Station F on Deck 6."""
        station = SafetyIntelligenceEngine.get_assigned_muster_station_for_cabin("msc-bellissima", "14122")
        self.assertEqual(station.station_code, "F")
        self.assertEqual(station.deck, 6)
        self.assertEqual(station.side, ShipSide.STARBOARD)
        self.assertIn("Carousel Lounge", station.venue_name)
        self.assertIn(12, station.primary_lifeboat_numbers)

    def test_context_navigation_from_cabin(self):
        """Verify routing calculation from cabin 14122 to Muster Station F."""
        plan = SafetyIntelligenceEngine.calculate_navigation_plan(
            ship_slug="msc-bellissima",
            ship_name="MSC Bellissima",
            cabin_num="14122",
            from_location=CurrentLocationType.CABIN,
        )
        self.assertEqual(plan.assigned_muster_station.station_code, "F")
        self.assertEqual(plan.estimated_walking_time_min, 2)
        self.assertEqual(plan.distance_meters, 124)
        self.assertEqual(plan.deck_changes, 8)
        self.assertEqual(len(plan.primary_route_steps), 3)
        self.assertTrue(plan.is_deterministic)

    def test_context_navigation_from_theatre(self):
        """Verify level walking route from London Theatre Deck 6 to Station F."""
        plan = SafetyIntelligenceEngine.calculate_navigation_plan(
            ship_slug="msc-bellissima",
            ship_name="MSC Bellissima",
            cabin_num="14122",
            from_location=CurrentLocationType.THEATRE,
        )
        self.assertEqual(plan.deck_changes, 0)
        self.assertEqual(plan.estimated_walking_time_min, 1)
        self.assertEqual(plan.distance_meters, 96)

    def test_safety_negative_intelligence_completeness(self):
        """Verify negative intelligence rules cover buffet bypass and drill completion."""
        plan = SafetyIntelligenceEngine.calculate_navigation_plan(
            ship_slug="msc-bellissima",
            cabin_num="14122",
            from_location=CurrentLocationType.CABIN,
        )
        self.assertGreater(len(plan.negative_intelligence_rules), 3)
        rules_text = " ".join(plan.negative_intelligence_rules)
        self.assertIn("Muster Drill", rules_text)
        self.assertIn("Buffet Deck 15", rules_text)


if __name__ == "__main__":
    unittest.main()
