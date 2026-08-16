import unittest
import os
import json
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

FRONTEND_GEN_DIR = os.path.join(REPO_ROOT, "frontend", "src", "generated")


class TestFrontendBridge(unittest.TestCase):
    def test_generated_database_json_exists(self):
        """Verify generated database.json exists and is valid."""
        db_path = os.path.join(FRONTEND_GEN_DIR, "database.json")
        self.assertTrue(os.path.exists(db_path), "frontend/src/generated/database.json must exist")
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("ships", data)
        self.assertIn("ports", data)
        self.assertGreater(len(data["ships"]), 100)

    def test_generated_fleet_ts_exists(self):
        """Verify generated fleet.ts exists and exports FLEET_REGISTRY."""
        fleet_path = os.path.join(FRONTEND_GEN_DIR, "fleet.ts")
        self.assertTrue(os.path.exists(fleet_path), "frontend/src/generated/fleet.ts must exist")
        with open(fleet_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("export const FLEET_REGISTRY", content)
        self.assertIn("msc-bellissima", content)
        self.assertIn("msc-world-europa", content)

    def test_generated_ports_ts_exists(self):
        """Verify generated ports.ts exists and exports PORTS_REGISTRY."""
        ports_path = os.path.join(FRONTEND_GEN_DIR, "ports.ts")
        self.assertTrue(os.path.exists(ports_path), "frontend/src/generated/ports.ts must exist")
        with open(ports_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("export const PORTS_REGISTRY", content)
        self.assertIn("genoa", content)

    def test_generated_decisions_ts_exists(self):
        """Verify generated decisions.ts exists and exports PRECOMPUTED_DECISIONS."""
        dec_path = os.path.join(FRONTEND_GEN_DIR, "decisions.ts")
        self.assertTrue(os.path.exists(dec_path), "frontend/src/generated/decisions.ts must exist")
        with open(dec_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("export const PRECOMPUTED_DECISIONS", content)
        self.assertIn("MSC World Europa", content)

    def test_legacy_shim_redirection(self):
        """Verify fleet.ts and ports.ts re-export from generated sources."""
        fleet_shim = os.path.join(REPO_ROOT, "frontend", "src", "fleet.ts")
        ports_shim = os.path.join(REPO_ROOT, "frontend", "src", "ports.ts")

        with open(fleet_shim, "r", encoding="utf-8") as f:
            self.assertIn("export * from './generated/fleet'", f.read())

        with open(ports_shim, "r", encoding="utf-8") as f:
            self.assertIn("export * from './generated/ports'", f.read())


if __name__ == "__main__":
    unittest.main()
