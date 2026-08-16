import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.journey_engine import (
    JourneyEngine,
    TimelineStage,
    JourneyConfig,
    JourneyCard,
    HotelStay,
)


class TestJourneyEngine(unittest.TestCase):
    def setUp(self):
        self.shanghai_cfg = JourneyEngine.get_reference_shanghai_tokyo_journey()
        self.med_cfg = JourneyEngine.get_reference_mediterranean_journey()

    def test_shanghai_timeline_stages_completeness(self):
        """Verify that a full journey produces exactly 8 chronological stages."""
        cards = JourneyEngine.generate_journey_timeline(self.shanghai_cfg)
        self.assertEqual(len(cards), 8)
        stages = [c.stage for c in cards]
        self.assertIn(TimelineStage.DAYS_90_BEFORE, stages)
        self.assertIn(TimelineStage.HOURS_48_BEFORE, stages)
        self.assertIn(TimelineStage.TERMINAL_ARRIVAL, stages)
        self.assertIn(TimelineStage.EMBARKATION_ONBOARD, stages)
        self.assertIn(TimelineStage.SEA_DAY_TRANSIT, stages)
        self.assertIn(TimelineStage.PORT_DAY_EXPLORATION, stages)
        self.assertIn(TimelineStage.DISEMBARKATION_DAY, stages)

    def test_negative_intelligence_in_every_card(self):
        """Verify every journey card contains an actionable Negative Intelligence warning."""
        cards = JourneyEngine.generate_journey_timeline(self.shanghai_cfg)
        for card in cards:
            self.assertGreater(len(card.negative_intelligence_to_avoid), 20)
            self.assertGreater(len(card.what_to_do_now), 15)
            self.assertGreater(len(card.upcoming_decision), 10)
            self.assertGreater(len(card.evidence_sources), 0)

    def test_missing_data_zero_hallucination(self):
        """Verify that when hotel is missing, it explicitly reports UNKNOWN."""
        cfg_no_hotel = JourneyConfig(
            journey_id="test-no-hotel",
            traveler_name="Cruiser",
            ship_slug="msc-bellissima",
            ship_name="MSC Bellissima",
            cabin_number="14122",
            departure_port_name="Shanghai",
            arrival_port_name="Tokyo",
            embarkation_date="2026-10-15",
            disembarkation_date="2026-10-22",
            pre_cruise_hotel=None,
        )
        cards = JourneyEngine.generate_journey_timeline(cfg_no_hotel)
        card_30d = [c for c in cards if c.stage == TimelineStage.DAYS_30_BEFORE][0]
        self.assertIn("UNKNOWN", card_30d.current_objective)

    def test_journey_determinism(self):
        """Verify multiple runs produce identical card IDs and payloads."""
        cards1 = JourneyEngine.generate_journey_timeline(self.med_cfg)
        cards2 = JourneyEngine.generate_journey_timeline(self.med_cfg)
        for c1, c2 in zip(cards1, cards2):
            self.assertEqual(c1.card_id, c2.card_id)
            self.assertEqual(c1.what_to_do_now, c2.what_to_do_now)
            self.assertTrue(c1.is_deterministic)


if __name__ == "__main__":
    unittest.main()
