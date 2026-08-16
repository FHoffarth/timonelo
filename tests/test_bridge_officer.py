import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.bridge_officer import (
    BridgeOfficerEngine,
    BriefingPhase,
)


class TestBridgeOfficer(unittest.TestCase):
    def test_daily_bridge_briefing_pre_cruise_12d(self):
        """Verify pre-cruise T-12d briefing contains proactive Hyatt and visa notes."""
        briefing = BridgeOfficerEngine.generate_briefing(
            phase=BriefingPhase.PRE_CRUISE_12D,
            traveler_name="Florian",
            ship_name="MSC Bellissima",
            cabin_num="14122",
        )
        self.assertEqual(briefing.greeting_line, "Guten Morgen, Florian.")
        self.assertIn("12 Tage", briefing.phase_context)
        self.assertGreater(len(briefing.proactive_notices), 0)
        self.assertIn("Hyatt", briefing.proactive_notices[0].content)
        self.assertEqual(briefing.sign_off, "Ich bleibe auf der Brücke. Melden Sie sich jederzeit.")

    def test_embarkation_day_briefing_and_wit(self):
        """Verify embarkation briefing prioritizes muster drill and contains subtle buffet wit."""
        briefing = BridgeOfficerEngine.generate_briefing(
            phase=BriefingPhase.EMBARKATION_BOARDING,
            traveler_name="Florian",
            ship_name="MSC Bellissima",
            cabin_num="14122",
        )
        self.assertIn("14122", briefing.phase_context)
        self.assertIn("Musterstation F", briefing.proactive_notices[0].content)
        self.assertIn("Expedition", briefing.maritime_insight)
        self.assertEqual(briefing.sign_off, "Ich bleibe auf der Brücke. Melden Sie sich jederzeit.")

    def test_yokohama_port_day_return_buffer(self):
        """Verify Yokohama port briefing emphasizes 45-minute return buffer before All Aboard."""
        briefing = BridgeOfficerEngine.generate_briefing(
            phase=BriefingPhase.PORT_YOKOHAMA,
            traveler_name="Florian",
        )
        self.assertIn("Yokohama", briefing.greeting_line)
        self.assertIn("45 Minuten", briefing.proactive_notices[0].content)
        self.assertEqual(len(briefing.daily_focus_points), 3)

    def test_zero_ai_jargon_in_briefings(self):
        """Verify no robotic or AI chatbot clichés exist in any briefing."""
        for phase in BriefingPhase:
            briefing = BridgeOfficerEngine.generate_briefing(phase=phase)
            full_text = f"{briefing.greeting_line} {briefing.phase_context} {briefing.maritime_insight} {briefing.sign_off} " + " ".join(briefing.daily_focus_points)
            for notice in briefing.proactive_notices:
                full_text += f" {notice.headline} {notice.content}"

            self.assertNotIn("As an AI", full_text)
            self.assertNotIn("Language model", full_text)
            self.assertNotIn("How can I help you today", full_text)
            self.assertNotIn("Error 404", full_text)
            self.assertTrue(briefing.is_deterministic)


if __name__ == "__main__":
    unittest.main()
