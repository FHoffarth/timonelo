import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler

from tests.compiler_sandbox import sandbox_root
from src.timonelo.database.sources_schema import SourceCategory, AccessMethod, SourceEntity
from src.timonelo.database.sources_dashboard import SourcesDashboard


class TestSourceNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Sandboxed root: see tests/compiler_sandbox.py.
        compiler = KnowledgeDBCompiler(sandbox_root())
        cls.db = compiler.compile()

    def test_sources_network_ingestion(self):
        """Verify sources are compiled and indexed across categories."""
        sources = self.db.get("sources", {})
        self.assertGreater(len(sources), 10)
        self.assertIn("src:imo-gisis", sources)
        self.assertIn("src:dnv-gl-vessel-register", sources)
        self.assertIn("src:chantiers-atlantique-ga", sources)

    def test_source_attributes_integrity(self):
        """Verify source entity metadata contracts."""
        sources = self.db.get("sources", {})
        gisis = sources["src:imo-gisis"]
        self.assertEqual(gisis.get("priority", 1), 1)
        self.assertEqual(gisis.get("trust_score", 1.0), 1.0)
        self.assertIn("gisis.imo.org", gisis.get("website", gisis.get("url", "")))

    def test_sources_dashboard_metrics(self):
        """Verify sources analytics and dependency chain calculations."""
        dashboard = SourcesDashboard(self.db)
        report = dashboard.generate_sources_report()
        self.assertGreater(report["total_sources_indexed"], 10)
        self.assertGreater(report["average_network_trust_pct"], 90.0)
        self.assertIn("Today (0 days)", report["freshness_distribution"])
        self.assertGreater(len(report["canonical_dependency_chain"]), 3)


if __name__ == "__main__":
    unittest.main()
