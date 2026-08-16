import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.hotel_intelligence import (
    HotelIntelligenceEngine,
    TransferComplexityLevel,
)


class TestHotelIntelligence(unittest.TestCase):
    def test_hyatt_on_the_bund_shanghai_evaluation(self):
        """Verify Hyatt on the Bund pre-cruise hotel facts and transfer recommendation."""
        hotel = HotelIntelligenceEngine.get_hotel_by_id("hyatt-on-the-bund-shanghai")
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.city, "Shanghai")
        self.assertEqual(hotel.transfer_complexity, TransferComplexityLevel.HIGH_TRAFFIC_TRANSFER)
        self.assertIn("10:45", hotel.recommended_departure_time)
        self.assertIn("FamilyMart", hotel.nearby_conveniences[0])

    def test_grand_hotel_savoia_genoa_walk(self):
        """Verify Grand Hotel Savoia in Genoa provides direct walking access to terminal."""
        hotel = HotelIntelligenceEngine.get_hotel_by_id("grand-hotel-savoia-genoa")
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.transfer_complexity, TransferComplexityLevel.DIRECT_WALK)
        self.assertLessEqual(hotel.distance_to_terminal_km, 0.5)


if __name__ == "__main__":
    unittest.main()
