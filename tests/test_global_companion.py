import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.global_companion import (
    GlobalCompanionEngine,
    RegretScoreEngine,
    CompanionPhase,
    RegretLevel,
    TravelMemory,
)


class TestGlobalCompanion(unittest.TestCase):
    def setUp(self):
        self.memory = GlobalCompanionEngine.get_reference_memory_flo()

    def test_travel_memory_integrity(self):
        """Verify Travel Memory structure and values for Flo."""
        self.assertEqual(self.memory.preferred_name, "Flo")
        self.assertEqual(self.memory.msc_loyalty_tier, "Diamond")
        self.assertTrue(self.memory.is_solo_traveler)
        self.assertTrue(self.memory.photography_enthusiast)
        self.assertIn("Balkonkabinen", self.memory.likes[0])
        self.assertIn("Buffet-Gänge", self.memory.dislikes[0])

    def test_all_8_companion_phases_generated(self):
        """Verify that all 8 distinct chronological phases are generated with memory adaptations."""
        phases = GlobalCompanionEngine.generate_8_phase_journey(self.memory)
        self.assertEqual(len(phases), 8)
        expected_phases = [
            CompanionPhase.PHASE_1_HOME,
            CompanionPhase.PHASE_2_FLIGHT,
            CompanionPhase.PHASE_3_HOTEL,
            CompanionPhase.PHASE_4_CITY,
            CompanionPhase.PHASE_5_TERMINAL,
            CompanionPhase.PHASE_6_SHIP,
            CompanionPhase.PHASE_7_PORT_DAYS,
            CompanionPhase.PHASE_8_RETURN,
        ]
        for idx, expected in enumerate(expected_phases):
            self.assertEqual(phases[idx].phase, expected)
            self.assertEqual(phases[idx].phase_number, idx + 1)
            self.assertGreater(len(phases[idx].what_to_do_now), 0)
            self.assertGreater(len(phases[idx].negative_intelligence_to_avoid), 10)
            self.assertGreater(len(phases[idx].travel_memory_adaptations), 0)

    def test_regret_score_same_day_vs_previous_day(self):
        """Verify high regret risk for same-day flight arrival vs low regret for previous day."""
        high_risk = RegretScoreEngine.evaluate_flight_arrival_timing(
            arrival_date_same_day=True,
            arrival_time_str="09:50",
            departure_time_str="17:00",
            city_name="Shanghai",
        )
        self.assertEqual(high_risk.level, RegretLevel.HIGH)
        self.assertGreaterEqual(high_risk.regret_score_pct, 80)
        self.assertGreater(len(high_risk.why_you_will_regret_this), 3)

        low_risk = RegretScoreEngine.evaluate_flight_arrival_timing(
            arrival_date_same_day=False,
            arrival_time_str="Vortag",
            departure_time_str="17:00",
            city_name="Shanghai",
        )
        self.assertEqual(low_risk.level, RegretLevel.LOW)
        self.assertLessEqual(low_risk.regret_score_pct, 20)


if __name__ == "__main__":
    unittest.main()
