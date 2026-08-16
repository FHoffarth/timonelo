import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.context_engine import (
    ContextEngine,
    CabinFactProfile,
    PassengerContext,
    PassengerProfileType,
    TripContext,
    Season,
    SeaState,
    RouteHeading,
)


class TestContextEngine(unittest.TestCase):
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

    def test_motion_sensitive_context_divergence(self):
        """Verify motion sensitive traveler receives lower suitability for high aft deck."""
        passenger = PassengerContext(
            profile_type=PassengerProfileType.MOTION_SENSITIVE,
            motion_sensitive=True,
            priority_theatre_and_shows=True,
        )
        trip = TripContext(
            ship_slug="msc-bellissima",
            route_slug="western-med-7n",
            route_name="Western Med",
            season=Season.AUTUMN,
            heading=RouteHeading.WESTBOUND,
            expected_sea_state=SeaState.MODERATE,
        )
        advice = ContextEngine.evaluate_cabin_for_passenger(self.cabin_14122, passenger, trip)
        self.assertEqual(advice.suitability_verdict, "NOT_RECOMMENDED_FOR_YOUR_CONTEXT")
        self.assertLess(advice.suitability_score, 50.0)

    def test_photography_fjord_context_bonus(self):
        """Verify photographer receives high scenic score for northbound starboard balcony."""
        passenger = PassengerContext(
            profile_type=PassengerProfileType.PHOTOGRAPHER,
            priority_scenic_photography=True,
        )
        trip = TripContext(
            ship_slug="msc-bellissima",
            route_slug="norwegian-fjords-7n",
            route_name="7-Night Norwegian Fjords",
            season=Season.SUMMER,
            heading=RouteHeading.NORTHBOUND,
        )
        advice = ContextEngine.evaluate_cabin_for_passenger(self.cabin_14122, passenger, trip)
        self.assertIn("GREAT_FIT", advice.suitability_verdict)
        self.assertTrue(any("morning natural light" in b for b in advice.benefits_for_you))

    def test_mobility_step_free_rejection(self):
        """Verify step-free wheelchair context flags non-accessible bathroom thresholds."""
        passenger = PassengerContext(
            profile_type=PassengerProfileType.MOBILITY_REDUCED,
            requires_step_free=True,
        )
        trip = TripContext(
            ship_slug="msc-bellissima",
            route_slug="western-med-7n",
            route_name="Western Med",
            season=Season.SUMMER,
            heading=RouteHeading.CIRCULAR,
        )
        advice = ContextEngine.evaluate_cabin_for_passenger(self.cabin_14122, passenger, trip)
        self.assertLess(advice.suitability_score, 60.0)
        self.assertTrue(any("raised bathroom" in t for t in advice.trade_offs_for_you))

    def test_journey_phase_detection(self):
        """Verify automatic phase detection from calendar proximity."""
        # 12 days before departure -> PREPARATION
        phase_prep = ContextEngine.detect_journey_phase("2026-10-03", "2026-10-15", "2026-10-22")
        self.assertEqual(phase_prep.name, "PREPARATION")

        # 2 days before departure -> CHECK_IN
        phase_checkin = ContextEngine.detect_journey_phase("2026-10-13", "2026-10-15", "2026-10-22")
        self.assertEqual(phase_checkin.name, "CHECK_IN")

        # Day of departure -> EMBARKATION
        phase_embark = ContextEngine.detect_journey_phase("2026-10-15", "2026-10-15", "2026-10-22")
        self.assertEqual(phase_embark.name, "EMBARKATION")

    def test_priority_engine_strictly_capped_at_three(self):
        """Verify Priority Engine never overwhelms and caps top priorities at 3."""
        briefing = ContextEngine.generate_context_briefing(simulated_date_iso="2026-10-03")
        self.assertLessEqual(len(briefing.top_priorities), 3)
        self.assertGreater(len(briefing.top_priorities), 0)
        self.assertIn("I remain on the bridge", briefing.sign_off_phrase)
        self.assertTrue(any("BOT noticed" in n for n in briefing.proactive_bot_notices))


if __name__ == "__main__":
    unittest.main()
