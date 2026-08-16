import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.shipmate_memory import (
    BridgeMemoryEngine,
    HabitCategory,
)


class TestShipmateMemory(unittest.TestCase):
    def test_canonical_profile_statistics(self):
        """Verify shipmate profile statistics: voyages, sea days, visited countries and ships."""
        prof = BridgeMemoryEngine.get_shipmate_profile("Florian")
        self.assertEqual(prof.traveller_name, "Florian")
        self.assertEqual(prof.total_voyages_count, 2)
        self.assertEqual(prof.total_sea_days, 18)
        self.assertIn("China", prof.visited_countries)
        self.assertIn("Japan", prof.visited_countries)
        self.assertIn("MSC Bellissima", prof.visited_ships)
        self.assertIn("MS Andorinha", prof.visited_ships)

    def test_favourite_locations_and_habits(self):
        """Verify favourite venues and observed travel habits."""
        prof = BridgeMemoryEngine.get_shipmate_profile("Florian")
        self.assertGreaterEqual(len(prof.favourite_places), 3)
        self.assertTrue(any("Horizon" in f.name for f in prof.favourite_places))
        self.assertTrue(any("Posidonia" in f.name for f in prof.favourite_places))

        self.assertGreaterEqual(len(prof.confirmed_habits), 4)
        hab_cats = [h.category for h in prof.confirmed_habits]
        self.assertIn(HabitCategory.DINING, hab_cats)
        self.assertIn(HabitCategory.MOVEMENT, hab_cats)

    def test_bridge_journal_entries(self):
        """Verify factual one-sentence daily journal entries exist for completed voyages."""
        prof = BridgeMemoryEngine.get_shipmate_profile("Florian")
        self.assertGreaterEqual(len(prof.voyage_history), 2)
        bellissima_voy = [v for v in prof.voyage_history if "Bellissima" in v.ship_name][0]
        self.assertGreaterEqual(len(bellissima_voy.journal_entries), 3)
        self.assertTrue(any("Kabine 14122" in j.factual_milestone_sentence for j in bellissima_voy.journal_entries))

    def test_bot_welcome_greeting_and_closing_log(self):
        """Verify BOT respectful welcome back greeting and permanent bridge log closing note."""
        prof = BridgeMemoryEngine.get_shipmate_profile("Florian")
        self.assertIn("Willkommen zurück an Bord", prof.bot_welcome_back_greeting)
        self.assertIn("Voyage completed successfully", prof.bot_closing_log_note)
        self.assertIn("entered this journey into the ship's log", prof.bot_closing_log_note)

    def test_proactive_memory_insights(self):
        """Verify proactive insights are generated from past voyage observations."""
        insights = BridgeMemoryEngine.generate_proactive_memory_insights("Florian")
        self.assertGreaterEqual(len(insights), 3)
        self.assertTrue(any("Frühstück" in ins for ins in insights))
        self.assertTrue(any("Horizon Bar" in ins for ins in insights))


if __name__ == "__main__":
    unittest.main()
