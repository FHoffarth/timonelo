import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.ingestion.importers import OfficialCruiseLineImporter, MaritimeIMOImporter
from src.timonelo.ingestion.validator import IngestionValidator
from src.timonelo.ingestion.diff_engine import KnowledgeDiffEngine
from src.timonelo.ingestion.review_queue import KnowledgeReviewQueue, ReviewStatus
from src.timonelo.ingestion.pipeline import KnowledgeFactoryPipeline


class TestIngestionFactory(unittest.TestCase):
    def setUp(self):
        self.pipeline = KnowledgeFactoryPipeline(REPO_ROOT)
        self.importer = OfficialCruiseLineImporter("src:test-line", "Test Cruise Line")

    def test_importer_sealing_and_checksum(self):
        raw = {"slug": "test-vessel", "name": "Test Vessel", "imo": "9876543"}
        payload = self.importer.ingest_payload(raw, "https://test.com/spec", 1.0)
        self.assertTrue(len(payload.sha256_checksum) == 64)
        self.assertEqual(payload.confidence, 1.0)

    def test_validator_rejects_impossible_dimensions(self):
        invalid_ship = {
            "slug": "bad-ship",
            "name": "Bad Ship",
            "imo": "1234567",
            "dimensions": {"length_m": 30.0, "beam_m": 45.0, "draft_m": 8.0, "gross_tonnage": 10000},
        }
        errors = IngestionValidator.validate_ship(invalid_ship)
        self.assertTrue(any("impossible dimensions" in e for e in errors))

    def test_validator_rejects_invalid_imo(self):
        invalid_imo_ship = {
            "slug": "bad-imo",
            "name": "Bad IMO",
            "imo": "12345",  # Too short
            "dimensions": {"length_m": 300.0, "beam_m": 40.0, "draft_m": 8.0, "gross_tonnage": 100000},
        }
        errors = IngestionValidator.validate_ship(invalid_imo_ship)
        self.assertTrue(any("invalid IMO" in e for e in errors))

    def test_diff_engine_detects_changes(self):
        old_ship = {
            "slug": "diff-ship",
            "dimensions": {"gross_tonnage": {"value": 170000}, "length_m": {"value": 315.0}},
            "capacities": {"passenger_max": {"value": 5000}},
        }
        new_ship = {
            "slug": "diff-ship",
            "dimensions": {"gross_tonnage": 180000, "length_m": 315.0},
            "capacities": {"passenger_max": 5600},
        }
        diff = KnowledgeDiffEngine.compare_ship(old_ship, new_ship)
        self.assertEqual(diff.diff_type, "MODIFIED")
        self.assertTrue(diff.review_required)
        self.assertEqual(len(diff.field_diffs), 2)

    def test_review_queue_lifecycle(self):
        queue = KnowledgeReviewQueue(os.path.join(REPO_ROOT, "data", "test_review_queue.json"))
        item = queue.submit_candidate(
            entity_id="ship:test-queue",
            entity_type="Ship",
            importer_source_id="src:test",
            candidate_payload={"slug": "test-queue"},
            diff_summary={"diff_type": "ADDED"},
            validation_errors=[],
        )
        self.assertEqual(item.status, ReviewStatus.PENDING)
        
        # Approve item
        approved = queue.approve_item(item.item_id, "Test approval")
        self.assertTrue(approved)
        self.assertEqual(queue.items[item.item_id].status, ReviewStatus.APPROVED)

        # Cleanup test file
        if os.path.exists(queue.staging_file):
            os.remove(queue.staging_file)


if __name__ == "__main__":
    unittest.main()
