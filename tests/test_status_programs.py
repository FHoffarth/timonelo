import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.status_programs import (
    StatusProgramsEngine,
    LoyaltyCategory,
)


class TestStatusPrograms(unittest.TestCase):
    def test_msc_voyagers_club_diamond(self):
        """Verify MSC Diamond benefits include priority boarding, specialty dinner and late checkout."""
        stat = StatusProgramsEngine.evaluate_status("MSC Voyagers Club", "Diamond")
        self.assertEqual(stat.category, LoyaltyCategory.CRUISE)
        self.assertEqual(stat.tier_name, "Diamond")
        self.assertIn("09:00", stat.guaranteed_late_checkout)
        self.assertIn("Spezialitätenrestaurant", stat.key_unlocked_perks[1])

    def test_world_of_hyatt_globalist(self):
        """Verify Hyatt Globalist guaranteed 16:00 checkout and lounge access."""
        stat = StatusProgramsEngine.evaluate_status("World of Hyatt", "Globalist")
        self.assertEqual(stat.category, LoyaltyCategory.HOTEL)
        self.assertIn("16:00", stat.guaranteed_late_checkout)
        self.assertIn("Club Lounge", stat.lounge_access)

    def test_miles_and_more_senator(self):
        """Verify Senator Star Alliance Gold lounge access and baggage allowance."""
        stat = StatusProgramsEngine.evaluate_status("Miles & More", "Senator")
        self.assertEqual(stat.category, LoyaltyCategory.AIRLINE)
        self.assertIn("Freigepäck", stat.key_unlocked_perks[0])


if __name__ == "__main__":
    unittest.main()
