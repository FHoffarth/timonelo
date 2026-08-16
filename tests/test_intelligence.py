"""
Unit tests for Plane 6: Cruise Intelligence Runtime (CRUISE_INTELLIGENCE.md & DECISION_FIRST.md).
Tests CruiseBriefingSynthesizer, NegativeIntelligence, Embarkation, Ports, Weather, Dining, and Visa evaluators.
"""

import unittest
from timonelo.ontology.bellissima import create_bellissima_ontology
from timonelo.factory.patch_engine import ShipPatchEngine
from timonelo.intelligence import (
    CruiseBriefingSynthesizer,
    CruiseBriefing,
    DecisionUrgency,
    PortDockingType,
    EmbarkationIntelligenceEvaluator,
    PortIntelligenceEvaluator,
    WeatherIntelligenceEvaluator,
    VisaIntelligenceEvaluator,
    TravelIntelligenceEvaluator,
    DiningIntelligenceEvaluator,
)


class TestCruiseIntelligenceRuntime(unittest.TestCase):
    def setUp(self):
        self.bellissima = create_bellissima_ontology()

    def test_cruise_briefing_synthesis_bellissima(self):
        briefing = CruiseBriefingSynthesizer.generate_briefing(self.bellissima, "14122")
        self.assertIsNotNone(briefing)
        self.assertIsInstance(briefing, CruiseBriefing)
        self.assertEqual(briefing.ship_name, "MSC Bellissima")
        self.assertEqual(briefing.cabin_intelligence.cabin_number, "14122")
        self.assertEqual(briefing.cabin_intelligence.deck_number, 14)
        self.assertEqual(briefing.cabin_intelligence.deck_name, "Girasole")

        # Verify Decision Summary (Three Things That Matter)
        self.assertGreaterEqual(len(briefing.decision_summary.core_decisions), 3)
        self.assertEqual(briefing.decision_summary.core_decisions[0].urgency, DecisionUrgency.CRITICAL_SAFETY)

        # Verify Negative Intelligence (Decisions Avoided)
        self.assertGreaterEqual(len(briefing.decision_summary.decisions_avoided), 3)
        regrets = [a.regret_prevented for a in briefing.decision_summary.decisions_avoided]
        self.assertTrue(any("emergency" in r.lower() or "wrong deck" in r.lower() for r in regrets))
        self.assertTrue(any("roaming" in r.lower() or "dinner" in r.lower() or "wrong gangway" in r.lower() for r in regrets))

    def test_embarkation_evaluator(self):
        deck14 = self.bellissima.decks[14]
        cabin = deck14.cabins["14122"]
        embark = EmbarkationIntelligenceEvaluator.evaluate(self.bellissima, cabin)
        self.assertIn("Muster Station", embark.assigned_muster_station)
        self.assertIn(embark.muster_station_deck, [6, 7])
        self.assertTrue(len(embark.step_free_muster_route) > 0)

    def test_port_evaluator(self):
        port = PortIntelligenceEvaluator.evaluate()
        self.assertEqual(port.port_name, "Genoa (Genova)")
        self.assertEqual(port.country, "Italy")
        self.assertEqual(port.docking_type, PortDockingType.PIER_BERTH)
        self.assertTrue(port.is_walkable_to_center)
        self.assertEqual(port.gangway_deck, 5)

    def test_weather_evaluator(self):
        weather = WeatherIntelligenceEvaluator.evaluate()
        self.assertTrue(weather.air_temperature_celsius > 0)
        self.assertTrue(weather.sea_swell_meters >= 0)
        self.assertIn("Motion", weather.motion_risk_level)

    def test_visa_evaluator(self):
        visa = VisaIntelligenceEvaluator.evaluate("Italy")
        self.assertEqual(visa.destination_country, "Italy")
        self.assertEqual(visa.passport_validity_required_months, 6)
        self.assertFalse(visa.visa_required_for_passengers)

    def test_travel_evaluator(self):
        travel = TravelIntelligenceEvaluator.evaluate("Italy")
        self.assertEqual(travel.local_currency_code, "EUR")
        self.assertIn("Airplane Mode", travel.offline_roaming_advice)

    def test_nonexistent_cabin_returns_none(self):
        briefing = CruiseBriefingSynthesizer.generate_briefing(self.bellissima, "99999")
        self.assertIsNone(briefing)

    def test_multi_vessel_briefing_inheritance(self):
        patch_meraviglia = {
            "target_imo": "IMO9647710",
            "target_name": "MSC Meraviglia",
            "operations": [
                {
                    "op": "RENAME_VENUE",
                    "deck": 6,
                    "venue_id": "VENUE_THEATER",
                    "new_name": "Broadway Theatre (Lower Level)",
                }
            ],
        }
        meraviglia = ShipPatchEngine.apply_patch(self.bellissima, patch_meraviglia)
        briefing = CruiseBriefingSynthesizer.generate_briefing(meraviglia, "12122")
        self.assertIsNotNone(briefing)
        self.assertEqual(briefing.ship_name, "MSC Meraviglia")
        self.assertEqual(briefing.ship_imo, "IMO9647710")


if __name__ == "__main__":
    unittest.main()
