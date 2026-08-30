"""
Unit tests for Plane 6: Cruise Intelligence Runtime (CRUISE_INTELLIGENCE.md & DECISION_FIRST.md).
Tests CruiseBriefingSynthesizer, NegativeIntelligence, Embarkation, Ports, Weather, Dining, and Visa evaluators.
"""

import unittest
from timonelo.ontology.bellissima import create_bellissima_ontology
from timonelo.factory.patch_engine import HypothesisPublicationBlocked, ShipPatchEngine
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
        # Negative-intelligence items exist only for sections that are
        # sourced; with none sourced, the correct count is zero.
        self.assertIsInstance(briefing.decision_summary.decisions_avoided, list)
        regrets = [a.regret_prevented for a in briefing.decision_summary.decisions_avoided]
        # Muster-related negative intelligence is only present when sourced
        # embarkation data exists; it is absent by design otherwise.
        self.assertTrue(any("roaming" in r.lower() or "dinner" in r.lower() or "wrong gangway" in r.lower() for r in regrets))

    def test_embarkation_returns_none_without_sourced_data(self):
        """Muster assignment must never be fabricated from generated geometry.

        This test previously asserted the opposite: it required a muster
        station to exist for a cabin with no sourced muster record, which
        enforced the defect. The station was computed from the cabin polygon's
        x-coordinate and the parity of the cabin number.
        """
        deck14 = self.bellissima.decks[14]
        cabin = deck14.cabins["14122"]
        embark = EmbarkationIntelligenceEvaluator.evaluate(self.bellissima, cabin)
        self.assertIsNone(embark)

    def test_embarkation_refuses_partial_sourced_data(self):
        """Partial embarkation data must raise rather than render half a claim."""
        deck14 = self.bellissima.decks[14]
        cabin = deck14.cabins["14122"]
        with self.assertRaises(ValueError):
            EmbarkationIntelligenceEvaluator.evaluate(
                self.bellissima, cabin, terminal_override={"terminal_name": "X"}
            )

    def test_port_returns_none_without_sourced_data(self):
        """Volatile-domain data must not be fabricated.

        This test previously asserted specific hardcoded values, which is what
        kept the fabrication in place.
        """
        self.assertIsNone(PortIntelligenceEvaluator.evaluate())


    def test_weather_returns_none_without_sourced_data(self):
        """Volatile-domain data must not be fabricated.

        This test previously asserted specific hardcoded values, which is what
        kept the fabrication in place.
        """
        self.assertIsNone(WeatherIntelligenceEvaluator.evaluate())


    def test_visa_returns_none_without_sourced_data(self):
        """Volatile-domain data must not be fabricated.

        This test previously asserted specific hardcoded values, which is what
        kept the fabrication in place.
        """
        self.assertIsNone(VisaIntelligenceEvaluator.evaluate('Italy'))


    def test_travel_returns_none_without_sourced_data(self):
        """Volatile-domain data must not be fabricated.

        This test previously asserted specific hardcoded values, which is what
        kept the fabrication in place.
        """
        self.assertIsNone(TravelIntelligenceEvaluator.evaluate('Italy'))


    def test_nonexistent_cabin_returns_none(self):
        briefing = CruiseBriefingSynthesizer.generate_briefing(self.bellissima, "99999")
        self.assertIsNone(briefing)

    def test_sister_ship_hypothesis_cannot_generate_passenger_briefing(self):
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
        with self.assertRaises(HypothesisPublicationBlocked):
            CruiseBriefingSynthesizer.generate_briefing(meraviglia, "12122")


if __name__ == "__main__":
    unittest.main()
