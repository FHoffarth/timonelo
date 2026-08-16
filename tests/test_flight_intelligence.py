import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.flight_intelligence import (
    FlightIntelligenceEngine,
    FlightSegment,
    AirlineAlliance,
    ConnectionRiskLevel,
)


class TestFlightIntelligence(unittest.TestCase):
    def test_airport_registry_pvg_and_hnd(self):
        """Verify Shanghai Pudong and Tokyo Haneda airport hubs are registered with immigration and transit facts."""
        self.assertIn("PVG", FlightIntelligenceEngine.AIRPORT_REGISTRY)
        pvg = FlightIntelligenceEngine.AIRPORT_REGISTRY["PVG"]
        self.assertEqual(pvg.city, "Shanghai")
        self.assertEqual(pvg.minimum_connection_time_intl_min, 90)

        self.assertIn("HND", FlightIntelligenceEngine.AIRPORT_REGISTRY)
        hnd = FlightIntelligenceEngine.AIRPORT_REGISTRY["HND"]
        self.assertEqual(hnd.city, "Tokio")
        self.assertIn("Keikyu", hnd.public_transport_connection)

    def test_itinerary_evaluation_previous_day_arrival(self):
        """Verify flight evaluation recommends previous day arrival and Senator lounge access."""
        segments = [
            FlightSegment("LH728", "FRA", "PVG", "17:15", "11:40", "Lufthansa", AirlineAlliance.STAR_ALLIANCE)
        ]
        eval_res = FlightIntelligenceEngine.evaluate_itinerary(segments, "2026-10-15", "Miles & More Senator")
        self.assertEqual(eval_res.arrival_date_vs_embarkation, "PREVIOUS_DAY")
        self.assertIn("Senator Lounge", eval_res.lounge_eligibility_summary)
        self.assertIn("Handgepäck", eval_res.negative_intelligence)


if __name__ == "__main__":
    unittest.main()
