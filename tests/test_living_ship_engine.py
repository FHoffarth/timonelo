import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.living_ship_engine import (
    DigitalTwinEngine,
    OperationalStatus,
)


class TestLivingShipEngine(unittest.TestCase):
    def test_canonical_live_states(self):
        """Verify MSC Bellissima in Yokohama and MS Andorinha in Douro are registered in Digital Twin."""
        states = DigitalTwinEngine.list_all_live_states()
        self.assertGreaterEqual(len(states), 2)
        ships = [s.ship_name for s in states]
        self.assertIn("MSC Bellissima", ships)
        self.assertIn("MS Andorinha", ships)

    def test_passenger_translation_layer(self):
        """Verify raw maritime telemetry is translated into passenger meaning and actionable guidance."""
        live = DigitalTwinEngine.get_live_voyage_state("bellissima-live-yokohama")
        self.assertEqual(live.current_status, OperationalStatus.PORT_STAY)
        self.assertTrue(live.gangway_open)
        self.assertIn("16:45", live.all_aboard_time)

        self.assertGreater(len(live.operational_changes), 0)
        gangway_impact = [c for c in live.operational_changes if "Gangway" in c.change_title][0]
        self.assertIn("japanischen Einreiseformalitäten", gangway_impact.passenger_translation)
        self.assertIn("Zeitfenster vor 10:00 Uhr", gangway_impact.recommended_action)

    def test_bot_live_observations_and_sign_off(self):
        """Verify calm, professional BOT live observations and bridge sign-off."""
        live = DigitalTwinEngine.get_live_voyage_state("bellissima-live-yokohama")
        self.assertGreaterEqual(len(live.bot_observations), 3)
        self.assertTrue(any("Yokohama" in obs for obs in live.bot_observations))
        self.assertIn("I have reviewed today's operational situation", live.bridge_sign_off)
        self.assertIn("I remain on the bridge", live.bridge_sign_off)

    def test_foundation_constitution_file(self):
        """Verify docs/CONSTITUTION.md exists and contains the foundational laws."""
        foundation_path = os.path.join(REPO_ROOT, "docs", "CONSTITUTION.md")
        self.assertTrue(os.path.exists(foundation_path))
        with open(foundation_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("We never invent.", content)
        self.assertIn("We translate complexity into calm.", content)
        self.assertIn("Hospitality comes before technology.", content)
        self.assertIn("We build calm.", content)
        self.assertIn("Welcome aboard. The bridge is yours whenever you need it.", content)
        self.assertIn("Production is the only truth.", content)


if __name__ == "__main__":
    unittest.main()
