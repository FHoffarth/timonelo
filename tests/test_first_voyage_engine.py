import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.first_voyage_engine import (
    FirstVoyageEngine,
    JourneyStage,
    ProductAuditEngine,
)


class TestFirstVoyageEngine(unittest.TestCase):
    def test_journey_readiness_score_with_unknown_flight(self):
        """Verify Journey Readiness Health Score is exactly 82% when flight is missing, with clear deduction."""
        readiness = FirstVoyageEngine.calculate_journey_readiness(
            flight_confirmed=False,
            hotel_confirmed=True,
            passport_verified=True,
            china_visa_exempt_verified=True,
            web_checkin_done=False,
        )
        self.assertEqual(readiness.total_score, 82)
        self.assertTrue(readiness.is_ready_for_departure)
        self.assertEqual(len(readiness.deductions), 1)
        self.assertEqual(readiness.deductions[0].points_deducted, 18)
        self.assertIn("Hinflug", readiness.deductions[0].item_name)
        self.assertIn("82%", readiness.bot_verdict)

    def test_journey_readiness_score_full_verification(self):
        """Verify Journey Readiness reaches 100% when flight and web check-in are confirmed."""
        readiness = FirstVoyageEngine.calculate_journey_readiness(
            flight_confirmed=True,
            hotel_confirmed=True,
            passport_verified=True,
            china_visa_exempt_verified=True,
            web_checkin_done=True,
        )
        self.assertEqual(readiness.total_score, 100)
        self.assertEqual(len(readiness.deductions), 0)

    def test_stage_timeline_detail_retrieval(self):
        """Verify chronological stage details for Preparation, Embarkation and Home."""
        prep = FirstVoyageEngine.get_stage_detail(JourneyStage.PREPARATION)
        self.assertIn("T-12", prep.title)
        self.assertGreater(len(prep.completed_milestones), 0)
        self.assertIn("gleichtägiger Ankunft", prep.anti_regret_warning)

        embark = FirstVoyageEngine.get_stage_detail(JourneyStage.EMBARKATION)
        self.assertIn("Wusongkou", embark.title)
        self.assertIn("Posidonia", embark.outstanding_actions[0])

        home = FirstVoyageEngine.get_stage_detail(JourneyStage.HOME)
        self.assertIn("Heimkehr", home.title)
        self.assertIn("Willkommen zu Hause", home.bot_morning_briefing)

    def test_anti_regret_register(self):
        """Verify anti-regret rules cover flight timing, luggage medication, and Yokohama buffer."""
        regrets = FirstVoyageEngine.get_anti_regret_register()
        self.assertGreaterEqual(len(regrets), 4)
        stages = [r.stage_name for r in regrets]
        self.assertIn("Flugplanung", stages)
        self.assertIn("Gepäck", stages)
        self.assertIn("Landgang Yokohama", stages)

    def test_product_audit_engine(self):
        """Verify Product Quality Audit scores UX clarity and proactive delivery."""
        audit = ProductAuditEngine.evaluate_experience()
        self.assertGreaterEqual(audit.total_ux_score, 98.0)
        self.assertEqual(audit.unnecessary_clicks_count, 0)
        self.assertEqual(audit.unnecessary_questions_asked, 0)
        self.assertFalse(audit.duplicate_info_detected)


if __name__ == "__main__":
    unittest.main()
