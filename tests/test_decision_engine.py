import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.decision_engine import DecisionEngine, DecisionVerdict
from src.timonelo.database.context_engine import (
    CabinFactProfile,
    PassengerContext,
    PassengerProfileType,
    TripContext,
    Season,
    SeaState,
    RouteHeading,
)


class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.cabin_14122 = CabinFactProfile(
            cabin_number="14122",
            deck_number=14,
            deck_name="Tiziano",
            category="Balcony Deluxe (BR2)",
            hull_side="STARBOARD",
            zone="AFT",
            interior_sqm=19.0,
            balcony_sqm=4.5,
            distance_to_nearest_lift_m=24.6,
            distance_to_nearest_stairs_m=18.0,
            distance_to_main_theatre_m=195.0,
            distance_to_buffet_m=25.0,
            noise_risk_fact="LOW_PANTRY_ADJACENT",
            view_category_fact="UNOBSTRUCTED",
            step_free_accessible=False,
            vertical_neighbor_above="Marketplace Buffet Seating Area (Carpeted)",
            vertical_neighbor_below="Residential Staterooms (Deck 13)",
        )
        self.passenger_motion = PassengerContext(
            profile_type=PassengerProfileType.MOTION_SENSITIVE,
            motion_sensitive=True,
            priority_theatre_and_shows=True,
        )
        self.trip_med = TripContext(
            ship_slug="msc-bellissima",
            route_slug="western-med-7n",
            route_name="7-Nächte Westliches Mittelmeer",
            season=Season.AUTUMN,
            heading=RouteHeading.WESTBOUND,
            expected_sea_state=SeaState.MODERATE,
        )

    def test_decision_reproducibility_and_determinism(self):
        """Verify that identical inputs yield identical Decision IDs and payloads across 10 iterations."""
        results = [
            DecisionEngine.evaluate_ship_decision("msc-bellissima", "msc-world-europa")
            for _ in range(10)
        ]
        first_id = results[0].decision_id
        for r in results:
            self.assertEqual(r.decision_id, first_id)
            self.assertEqual(r.verdict, results[0].verdict)
            self.assertEqual(r.warum, results[0].warum)
            self.assertTrue(r.is_deterministic)

    def test_cabin_decision_reproducibility(self):
        """Verify cabin decision is 100% deterministic."""
        card1 = DecisionEngine.evaluate_cabin_decision(self.cabin_14122, self.passenger_motion, self.trip_med)
        card2 = DecisionEngine.evaluate_cabin_decision(self.cabin_14122, self.passenger_motion, self.trip_med)
        self.assertEqual(card1.decision_id, card2.decision_id)
        self.assertEqual(card1.verdict, DecisionVerdict.NOT_RECOMMENDED)

    def test_decision_structure_contracts(self):
        """Verify the 5-point contract: Warum, 3 Gründe, 2 Unterschiede, 1 Risiko, Nächster Schritt."""
        card = DecisionEngine.evaluate_ship_decision("msc-bellissima", "msc-world-europa")
        self.assertTrue(len(card.warum) > 0)
        self.assertEqual(len(card.gruende_top_3), 3)
        self.assertEqual(len(card.unterschiede_2), 2)
        self.assertTrue(len(card.risiko_1) > 0)
        self.assertTrue(len(card.naechster_schritt) > 0)

    def test_evidence_and_confidence_completeness(self):
        """Verify decisions include valid source references and non-zero confidence."""
        card = DecisionEngine.evaluate_ship_decision("msc-bellissima", "msc-world-europa")
        self.assertGreater(len(card.evidence_sources), 0)
        self.assertGreater(card.confidence_score, 50.0)


if __name__ == "__main__":
    unittest.main()
