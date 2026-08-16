import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.explainable_matching import (
    ExplainableMatchingEngine,
    MatchStrength,
    PassengerPersona,
)


class TestExplainableMatching(unittest.TestCase):
    def test_explainable_recommendation_structure(self):
        """Verify that recommendations generate structured why, diff, and trade-off points."""
        rec = ExplainableMatchingEngine.generate_recommendation("msc-bellissima", "msc-world-europa")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.match_strength, MatchStrength.EXCEPTIONAL_MATCH)
        self.assertGreater(len(rec.why_recommended), 0)
        self.assertGreater(len(rec.things_that_are_different), 0)
        self.assertGreater(len(rec.reasons_not_to_choose), 0)
        self.assertTrue(rec.recommendation_id.startswith("rec:"))

    def test_persona_contextual_explanation(self):
        """Verify recommendations include targeted persona guidance."""
        rec = ExplainableMatchingEngine.generate_recommendation(
            "msc-bellissima", "msc-world-europa", persona=PassengerPersona.FAMILIES
        )
        self.assertIsNotNone(rec.persona_context)
        self.assertIn("Families", rec.persona_context)

    def test_head_to_head_comparison(self):
        """Verify head-to-head comparison generates operational and preference breakdowns."""
        comp = ExplainableMatchingEngine.compare_ships("msc-bellissima", "msc-world-europa")
        self.assertIsNotNone(comp)
        self.assertEqual(comp.ship_a_name, "MSC Bellissima")
        self.assertEqual(comp.ship_b_name, "MSC World Europa")
        self.assertGreater(len(comp.shared_experiences), 0)
        self.assertGreater(len(comp.operational_differences), 0)
        self.assertGreater(len(comp.who_will_prefer_ship_a), 0)


if __name__ == "__main__":
    unittest.main()
