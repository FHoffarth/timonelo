import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.cruise_dna import (
    CruiseDNAMatcher,
    CANONICAL_GENOMES,
    PassengerPreferenceDNA,
    ShipArchetype,
)


class TestCruiseDNA(unittest.TestCase):
    def test_genome_similarity_between_sisters(self):
        """Verify Bellissima and Meraviglia have >99% similarity vector."""
        bellissima = CANONICAL_GENOMES["msc-bellissima"]
        meraviglia = CANONICAL_GENOMES["msc-meraviglia"]
        sim = CruiseDNAMatcher.compute_similarity(bellissima.dna, meraviglia.dna)
        self.assertGreater(sim, 99.0)

    def test_top_matches_ranking(self):
        """Verify top matches for Bellissima prioritize Meraviglia family and World Europa."""
        matches = CruiseDNAMatcher.find_top_matches("msc-bellissima", top_k=4)
        matched_slugs = [m["slug"] for m in matches]
        self.assertIn("msc-meraviglia", matched_slugs)
        self.assertIn("msc-virtuosa", matched_slugs)
        self.assertIn("msc-grandiosa", matched_slugs)

    def test_passenger_preference_reasoning(self):
        """Verify adults-only and modern luxury preferences recommend Celebrity and Virgin."""
        pref = PassengerPreferenceDNA(
            avoids_children_and_noise=True,
            prefers_modern_luxury=True,
            seeks_quiet_and_relaxation=True,
        )
        recommendations = CruiseDNAMatcher.match_passenger_preferences(pref, top_k=2)
        top_slugs = [r["slug"] for r in recommendations]
        self.assertTrue("celebrity-ascent" in top_slugs or "scarlet-lady" in top_slugs)
        self.assertTrue(len(recommendations[0]["why"]) > 0)

    def test_river_compact_reasoning(self):
        """Verify intimate river preference correctly recommends MS Andorinha."""
        pref = PassengerPreferenceDNA(
            prefers_intimate_river_feeling=True,
            dislikes_long_walking_distances=True,
        )
        recommendations = CruiseDNAMatcher.match_passenger_preferences(pref, top_k=1)
        self.assertEqual(recommendations[0]["slug"], "ms-andorinha")
        self.assertEqual(recommendations[0]["archetype"], ShipArchetype.INTIMATE_SCENIC_RIVER_YACHT.value)


if __name__ == "__main__":
    unittest.main()
