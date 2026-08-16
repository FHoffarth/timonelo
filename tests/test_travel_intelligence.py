import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.travel_intelligence import (
    TravelIntelligenceEngine,
    JourneyPhase,
    ActionUrgency,
    TravelActionCard,
)


class TestTravelIntelligence(unittest.TestCase):
    def test_journey_timeline_coverage(self):
        """Verify actions exist across embarkation, sea days, port days, and pre-cruise."""
        for phase in [JourneyPhase.EMBARKATION_DAY, JourneyPhase.SEA_DAY, JourneyPhase.PORT_DAY, JourneyPhase.PRE_CRUISE]:
            actions = TravelIntelligenceEngine.get_actions_for_phase(phase)
            self.assertGreater(len(actions), 0, f"Phase {phase} must have prescriptive action cards")

    def test_negative_intelligence_completeness(self):
        """Verify every action card contains explicit Negative Intelligence to avoid."""
        for action in TravelIntelligenceEngine.ACTIONS_CATALOGUE:
            self.assertGreater(len(action.negative_intelligence_to_avoid), 15)
            self.assertGreater(len(action.what_to_do_now), 15)
            self.assertEqual(len(action.reasons_top_3), 3)
            self.assertGreater(len(action.concrete_steps), 1)

    def test_evidence_and_confidence(self):
        """Verify evidence sources and high confidence scores."""
        for action in TravelIntelligenceEngine.ACTIONS_CATALOGUE:
            self.assertGreater(len(action.evidence_sources), 0)
            self.assertGreaterEqual(action.confidence_score, 90.0)
            self.assertTrue(action.is_deterministic)

    def test_specific_buffet_bypass_action(self):
        """Verify embarkation buffet bypass action content."""
        action = TravelIntelligenceEngine.get_action_by_id("act:emb:buffet-bypass")
        self.assertIsNotNone(action)
        self.assertIn("Posidonia", action.what_to_do_now)
        self.assertIn("15", action.negative_intelligence_to_avoid)


if __name__ == "__main__":
    unittest.main()
