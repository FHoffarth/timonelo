import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.destination_engine import DestinationIntelligenceEngine
from src.timonelo.database.destination_schema import PowerPlugType


class TestDestinationIntelligence(unittest.TestCase):
    def test_canonical_destinations_exist(self):
        """Verify that major global homeports are indexed."""
        for slug in ["shanghai", "tokyo-yokohama", "genoa", "barcelona"]:
            dest = DestinationIntelligenceEngine.get_destination_by_slug(slug)
            self.assertIsNotNone(dest, f"Destination {slug} must exist")
            self.assertGreater(len(dest.airports), 0)
            self.assertGreater(len(dest.terminals), 0)
            self.assertGreater(len(dest.recommended_hotel_zones), 0)

    def test_negative_intelligence_completeness(self):
        """Verify each destination has exactly 3 top negative intelligence rules and airport warnings."""
        for dest in DestinationIntelligenceEngine.list_all_destinations():
            self.assertEqual(len(dest.negative_intelligence_top_3), 3)
            for a in dest.airports:
                self.assertGreater(len(a.negative_intelligence), 20)
                self.assertGreater(len(a.evidence_source), 0)

    def test_genoa_operational_facts(self):
        """Verify Genoa destination profile matches official port facts."""
        genoa = DestinationIntelligenceEngine.get_destination_by_slug("genoa")
        self.assertEqual(genoa.country, "Italy")
        self.assertEqual(genoa.power_plugs, PowerPlugType.TYPE_C_F)
        self.assertIn("Ponte dei Mille", genoa.terminals[0].terminal_name)
        self.assertIn("GOA", [a.iata_code for a in genoa.airports])

    def test_shanghai_operational_facts(self):
        """Verify Shanghai destination profile matches Baoshan/Wusongkou logistics."""
        sh = DestinationIntelligenceEngine.get_destination_by_slug("shanghai")
        self.assertEqual(sh.country, "China")
        self.assertEqual(sh.power_plugs, PowerPlugType.TYPE_I)
        self.assertIn("Wusongkou", sh.terminals[0].terminal_name)
        self.assertIn("PVG", [a.iata_code for a in sh.airports])
        self.assertIn("SHA", [a.iata_code for a in sh.airports])


if __name__ == "__main__":
    unittest.main()
