import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.compiler import KnowledgeDBCompiler

from tests.compiler_sandbox import sandbox_root
from src.timonelo.database.operations_schema import (
    SeasonalPeriod,
    PortCallType,
    PortCall,
    Voyage,
    SeasonalDeployment,
    LiveFleetStatus,
)


class TestLiveFleetOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Sandboxed root: see tests/compiler_sandbox.py.
        compiler = KnowledgeDBCompiler(sandbox_root())
        cls.db = compiler.compile()

    def test_operations_layer_compiled_entities(self):
        """Verify that deployments, voyages, and fleet_status are ingested."""
        self.assertIn("deployments", self.db)
        self.assertIn("voyages", self.db)
        self.assertIn("fleet_status", self.db)
        self.assertGreater(len(self.db["deployments"]), 0)
        self.assertGreater(len(self.db["voyages"]), 0)
        self.assertGreater(len(self.db["fleet_status"]), 0)

    def test_seasonal_deployment_bellissima(self):
        """Verify seasonal deployment transitions for MSC Bellissima."""
        deployments = self.db["deployments"]
        self.assertIn("dep:bellissima:summer-2026", deployments)
        summer_dep = deployments["dep:bellissima:summer-2026"]
        self.assertEqual(summer_dep["region_slug"], "western-mediterranean")
        self.assertIn("genoa", summer_dep["homeports"])

    def test_voyage_port_call_integrity(self):
        """Verify voyage port call sequence and gangway deck assignments."""
        voyages = self.db["voyages"]
        self.assertIn("voyage:bellissima:2026-10-04", voyages)
        voy = voyages["voyage:bellissima:2026-10-04"]
        self.assertEqual(voy["embarkation_port"], "genoa")
        self.assertEqual(voy["disembarkation_port"], "genoa")
        self.assertEqual(len(voy["port_calls"]), 8)
        
        # Genoa turnaround call check
        first_call = voy["port_calls"][0]
        self.assertEqual(first_call["port_slug"], "genoa")
        self.assertEqual(first_call["gangway_deck"], 5)
        self.assertTrue(first_call["is_turnaround"])

    def test_fleet_status_and_provenance(self):
        """Verify live fleet status has source feed, coordinates, and freshness."""
        fleet_status = self.db["fleet_status"]
        self.assertIn("msc-bellissima", fleet_status)
        status = fleet_status["msc-bellissima"]
        self.assertEqual(status["operational_state"], "DOCKED")
        self.assertEqual(status["current_port_slug"], "genoa")
        self.assertEqual(status["next_port_slug"], "naples")
        self.assertIsNotNone(status["position_lat_lon"])


if __name__ == "__main__":
    unittest.main()
