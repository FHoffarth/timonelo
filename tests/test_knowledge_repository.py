import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from backend.knowledge import (
    KnowledgeRepository,
    ShipNotFoundError,
    DeckNotFoundError,
    DomainNotFoundError,
    SchemaValidationError,
)


class TestKnowledgeRepository(unittest.TestCase):
    def setUp(self):
        self.repo = KnowledgeRepository()

    def test_get_ship_technical(self):
        ship = self.repo.getShip("msc-bellissima")
        self.assertEqual(ship["vessel_id"], "msc-bellissima")
        self.assertEqual(ship["vessel_name"], "MSC Bellissima")
        self.assertEqual(ship["technical_specifications"]["imo_number"], 9760524)
        self.assertEqual(ship["technical_specifications"]["tonnage_gt"], 171598)

    def test_get_ship_not_found(self):
        with self.assertRaises(ShipNotFoundError):
            self.repo.getShip("non-existent-vessel-xyz")

    def test_get_decks(self):
        decks = self.repo.getDecks("msc-bellissima")
        self.assertGreaterEqual(len(decks), 14)
        deck_numbers = [d["deck_number"] for d in decks]
        self.assertIn(4, deck_numbers)
        self.assertIn(14, deck_numbers)
        self.assertIn(19, deck_numbers)
        self.assertNotIn(17, deck_numbers) # 17 skipped due to Italian superstition

    def test_get_deck_by_number_and_name(self):
        deck14 = self.repo.getDeck("msc-bellissima", 14)
        self.assertEqual(deck14["deck_number"], 14)
        self.assertIn("World Class", deck14["name"])

        deck5 = self.repo.getDeck("msc-bellissima", "DECK-05")
        self.assertEqual(deck5["deck_number"], 5)
        self.assertIn("Opera", deck5["name"])

    def test_get_deck_not_found(self):
        with self.assertRaises(DeckNotFoundError):
            self.repo.getDeck("msc-bellissima", 99)

    def test_get_restaurants(self):
        restaurants = self.repo.getRestaurants("msc-bellissima")
        self.assertGreaterEqual(len(restaurants), 10)
        names = [r["name"] for r in restaurants]
        self.assertTrue(any("Marketplace Buffet" in n for n in names))
        self.assertTrue(any("Butcher" in n for n in names))
        self.assertTrue(any("Kaito" in n for n in names))

    def test_get_bars(self):
        bars = self.repo.getBars("msc-bellissima")
        self.assertGreaterEqual(len(bars), 8)
        names = [b["name"] for b in bars]
        self.assertTrue(any("Masters of the Sea" in n for n in names))
        self.assertTrue(any("Champagne Bar" in n for n in names))

    def test_get_lounges(self):
        lounges = self.repo.getLounges("msc-bellissima")
        self.assertGreaterEqual(len(lounges), 4)
        names = [l["name"] for l in lounges]
        self.assertTrue(any("Carousel Lounge" in n for n in names))
        self.assertTrue(any("Sky Lounge" in n for n in names))

    def test_get_pools(self):
        pools = self.repo.getPools("msc-bellissima")
        self.assertGreaterEqual(len(pools), 4)
        names = [p["name"] for p in pools]
        self.assertTrue(any("Atmosphere Pool" in n for n in names))
        self.assertTrue(any("Bamboo Pool" in n for n in names))

    def test_get_spa(self):
        spa = self.repo.getSpa("msc-bellissima")
        self.assertEqual(spa["id"], "SPA-AUREA-COMPLEX")
        self.assertEqual(len(spa["sub_venues"]), 4)
        sub_names = [s["name"] for s in spa["sub_venues"]]
        self.assertTrue(any("Thermal Suite" in n for n in sub_names))

    def test_get_entertainment(self):
        entertainment = self.repo.getEntertainment("msc-bellissima")
        self.assertGreaterEqual(len(entertainment), 4)
        names = [e["name"] for e in entertainment]
        self.assertTrue(any("London Theatre" in n for n in names))
        self.assertTrue(any("Imperial Casino" in n for n in names))

    def test_get_sports(self):
        sports = self.repo.getSports("msc-bellissima")
        self.assertGreaterEqual(len(sports), 4)
        names = [s["name"] for s in sports]
        self.assertTrue(any("Sportplex" in n for n in names))
        self.assertTrue(any("Himalayan" in n for n in names))

    def test_get_cabins(self):
        cabins_data = self.repo.getCabins("msc-bellissima")
        self.assertIn("summary", cabins_data)
        self.assertIn("cabin_categories", cabins_data)
        categories = cabins_data["cabin_categories"]
        self.assertGreaterEqual(len(categories), 9)
        names = [c["name"] for c in categories]
        self.assertTrue(any("Deluxe Balcony" in n for n in names))
        self.assertTrue(any("Swarovski" in n for n in names))

    def test_get_public_areas(self):
        areas = self.repo.getPublicAreas("msc-bellissima")
        self.assertGreaterEqual(len(areas), 4)
        names = [a["name"] for a in areas]
        self.assertTrue(any("Galleria Bellissima" in n for n in names))
        self.assertTrue(any("Swarovski" in n for n in names))

    def test_in_memory_caching(self):
        self.repo.clear_cache()
        self.assertEqual(len(self.repo._doc_cache), 0)

        # First call loads and caches
        ship1 = self.repo.getShip("msc-bellissima")
        self.assertEqual(len(self.repo._doc_cache), 1)

        # Second call returns cached reference
        ship2 = self.repo.getShip("msc-bellissima")
        self.assertIs(ship1, ship2)

    def test_snake_case_method_aliases(self):
        self.assertEqual(self.repo.get_ship("msc-bellissima")["vessel_id"], "msc-bellissima")
        self.assertGreaterEqual(len(self.repo.get_restaurants("msc-bellissima")), 10)
        self.assertGreaterEqual(len(self.repo.get_bars("msc-bellissima")), 8)
        self.assertGreaterEqual(len(self.repo.get_sports("msc-bellissima")), 4)


if __name__ == "__main__":
    unittest.main()
