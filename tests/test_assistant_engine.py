import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.assistant_engine import (
    AssistantEngine,
    QuickActionQuery,
    SuggestionCategory,
)


class TestAssistantEngine(unittest.TestCase):
    def test_daily_mission_yokohama(self):
        """Verify Yokohama daily mission contains objective, recommendations, and negative intelligence."""
        msn = AssistantEngine.get_daily_mission("morning_yokohama")
        self.assertIsNotNone(msn)
        self.assertIn("Yokohama", msn.phase_name)
        self.assertGreater(len(msn.recommended_actions), 0)
        self.assertGreater(len(msn.negative_intelligence_avoid), 0)
        self.assertTrue(any("16:45" in act for act in msn.recommended_actions))
        self.assertTrue(any("Taxis" in av for av in msn.negative_intelligence_avoid))

    def test_free_time_two_hours_evaluation(self):
        """Verify 2-hour free time evaluation suggests valid options and flags restricted Top Sail Lounge."""
        bundle = AssistantEngine.evaluate_free_time(hours_available=2.0)
        self.assertEqual(len(bundle.recommended_options), 3)
        self.assertEqual(bundle.top_recommendation_id, "opt:champagne-bar")

        # Verify restricted venue check
        yacht_club_opt = [o for o in bundle.recommended_options if "Yacht Club" in o.title][0]
        self.assertTrue(yacht_club_opt.is_restricted)
        self.assertIsNotNone(yacht_club_opt.restriction_note)

    def test_quick_action_muster_and_lunch(self):
        """Verify quick action guidance for Muster Station and Lunch."""
        muster_bundle = AssistantEngine.answer_quick_action(QuickActionQuery.MUSTER_STATION, cabin_number="14122")
        self.assertIn("Station F", muster_bundle.bot_opening_line)
        self.assertEqual(muster_bundle.recommended_options[0].category, SuggestionCategory.SAFETY_DRILL)

        lunch_bundle = AssistantEngine.answer_quick_action(QuickActionQuery.LUNCH_WHERE)
        self.assertIn("Posidonia", lunch_bundle.recommended_options[0].title)
        self.assertEqual(lunch_bundle.recommended_options[0].category, SuggestionCategory.DINING)

    def test_concierge_phrasing_and_confidence(self):
        """Verify gentlemanly tone and high confidence without robotic clichés."""
        bundle = AssistantEngine.evaluate_free_time(hours_available=2.0)
        self.assertGreaterEqual(bundle.confidence_score, 99.0)
        self.assertIn("Ich bleibe auf der Brücke", bundle.bot_conclusion_line)
        self.assertNotIn("As an AI", bundle.bot_opening_line)


if __name__ == "__main__":
    unittest.main()
