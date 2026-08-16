import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.port_city_intelligence import (
    PortCityIntelligenceEngine,
    TapWaterSafety,
)


class TestPortCityIntelligence(unittest.TestCase):
    def test_canonical_destinations_registry(self):
        """Verify key world cruise destinations are loaded with structured profiles."""
        destinations = PortCityIntelligenceEngine.list_all_destinations()
        self.assertGreaterEqual(len(destinations), 6)
        slugs = [d.city_slug for d in destinations]
        self.assertIn("yokohama", slugs)
        self.assertIn("shanghai", slugs)
        self.assertIn("genoa", slugs)
        self.assertIn("naples", slugs)
        self.assertIn("barcelona", slugs)
        self.assertIn("singapore", slugs)

    def test_yokohama_shore_time_and_gangway(self):
        """Verify Yokohama Osanbashi shore time buffer and gangway transfer."""
        yok = PortCityIntelligenceEngine.get_destination_profile("yokohama")
        self.assertIsNotNone(yok)
        self.assertEqual(yok.terminal_name, "Yokohama Osanbashi International Passenger Terminal")
        self.assertEqual(yok.tap_water, TapWaterSafety.POTABLE_SAFE)
        self.assertEqual(yok.shore_time.scheduled_all_aboard, "17:30 Uhr")
        self.assertEqual(yok.shore_time.recommended_latest_return, "16:45 Uhr")
        self.assertEqual(yok.shore_time.safe_buffer_minutes, 45)
        self.assertGreaterEqual(len(yok.gangway_steps), 3)
        self.assertEqual(yok.bot_closing_phrase, "Enjoy your time ashore. I will be here when you return.")

    def test_negative_intelligence_traps_coverage(self):
        """Verify Negative Intelligence covers destination-specific pitfalls."""
        bcn = PortCityIntelligenceEngine.get_destination_profile("barcelona")
        self.assertTrue(any("Taschendiebe" in t for t in bcn.negative_intelligence_traps))
        self.assertTrue(any("Pont d'Europa" in t for t in bcn.negative_intelligence_traps))

        sin = PortCityIntelligenceEngine.get_destination_profile("singapore")
        self.assertTrue(any("Kaugummi" in t for t in sin.negative_intelligence_traps))

        nap = PortCityIntelligenceEngine.get_destination_profile("naples")
        self.assertTrue(any("Tariffa Predefinita" in t or "Taxipreise" in t for t in nap.negative_intelligence_traps))

    def test_shanghai_wusongkou_buffer_and_didi(self):
        """Verify Shanghai Wusongkou requires a 75-minute return buffer due to highway traffic."""
        sh = PortCityIntelligenceEngine.get_destination_profile("shanghai")
        self.assertEqual(sh.shore_time.safe_buffer_minutes, 75)
        self.assertIn("Didi", sh.ride_hailing_apps[0])


if __name__ == "__main__":
    unittest.main()
