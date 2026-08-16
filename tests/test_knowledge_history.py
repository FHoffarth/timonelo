import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.history import (
    KnowledgeHistoryEngine,
    LifecycleEvent,
    LifecycleEventType,
    ClaimStatus,
)


class TestKnowledgeHistory(unittest.TestCase):
    def setUp(self):
        self.test_history_path = os.path.join(REPO_ROOT, "data", "test_knowledge_history.json")
        if os.path.exists(self.test_history_path):
            os.remove(self.test_history_path)
        self.engine = KnowledgeHistoryEngine(self.test_history_path)

    def tearDown(self):
        if os.path.exists(self.test_history_path):
            os.remove(self.test_history_path)

    def test_immutable_revision_chain(self):
        # Rev 1
        rev1 = self.engine.record_claim_revision(
            entity_id="cabin:test:101",
            field_path="distance_to_nearest_lift",
            value=20.0,
            unit="m",
            evidence_type="SHIPYARD_DRAWING",
            source_id="src:yard",
            confidence=0.9,
            valid_from="2020-01-01",
            reason_for_change="Initial GA plan",
        )
        self.assertEqual(rev1.revision_number, 1)
        self.assertEqual(rev1.status, ClaimStatus.ACTIVE)

        # Rev 2
        rev2 = self.engine.record_claim_revision(
            entity_id="cabin:test:101",
            field_path="distance_to_nearest_lift",
            value=20.5,
            unit="m",
            evidence_type="FIELD_MEASUREMENT",
            source_id="src:laser",
            confidence=0.98,
            valid_from="2024-01-01",
            reason_for_change="Field measurement",
        )
        self.assertEqual(rev2.revision_number, 2)
        self.assertEqual(rev2.status, ClaimStatus.ACTIVE)

        # Inspect Claim
        claim = self.engine.claims["claim:cabin:test:101:distance_to_nearest_lift"]
        self.assertEqual(len(claim.revisions), 2)
        self.assertEqual(claim.revisions[0].status, ClaimStatus.SUPERSEDED)
        self.assertEqual(claim.revisions[0].valid_until, "2024-01-01")
        self.assertEqual(claim.revisions[1].status, ClaimStatus.ACTIVE)

    def test_time_travel_query(self):
        self.engine.record_claim_revision(
            entity_id="cabin:test:101",
            field_path="distance_to_nearest_lift",
            value=20.0,
            unit="m",
            evidence_type="SHIPYARD_DRAWING",
            source_id="src:yard",
            confidence=0.9,
            valid_from="2020-01-01",
        )
        self.engine.record_claim_revision(
            entity_id="cabin:test:101",
            field_path="distance_to_nearest_lift",
            value=20.5,
            unit="m",
            evidence_type="FIELD_MEASUREMENT",
            source_id="src:laser",
            confidence=0.98,
            valid_from="2024-01-01",
        )

        claim = self.engine.claims["claim:cabin:test:101:distance_to_nearest_lift"]
        
        # State in 2022 was 20.0m
        past_state = claim.get_revision_as_of("2022-06-15")
        self.assertIsNotNone(past_state)
        self.assertEqual(past_state.value, 20.0)

        # State in 2025 is 20.5m
        recent_state = claim.get_revision_as_of("2025-06-15")
        self.assertIsNotNone(recent_state)
        self.assertEqual(recent_state.value, 20.5)

    def test_downstream_impact_detection(self):
        self.engine.record_claim_revision(
            entity_id="cabin:test:101",
            field_path="distance_to_nearest_lift",
            value=20.0,
            unit="m",
            evidence_type="SHIPYARD_DRAWING",
            source_id="src:yard",
            confidence=0.9,
            valid_from="2020-01-01",
        )
        self.engine.record_claim_revision(
            entity_id="cabin:test:101",
            field_path="distance_to_nearest_lift",
            value=25.0,
            unit="m",
            evidence_type="FIELD_MEASUREMENT",
            source_id="src:laser",
            confidence=0.98,
            valid_from="2024-01-01",
        )
        self.assertGreater(len(self.engine.downstream_impacts), 0)
        self.assertEqual(self.engine.downstream_impacts[0].impact_severity, "MEDIUM")


if __name__ == "__main__":
    unittest.main()
