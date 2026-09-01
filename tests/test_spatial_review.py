"""
Unit & boundary tests for Spatial Review Adjudication Engine (ADR-0002 §5, ADR-0003 §7).
"""

import json
from pathlib import Path
import pytest

from timonelo.evidence.gatekeeper import is_canonical_statement_admitted
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)
from timonelo.evidence.gatekeeper import lifecycle_axes_pass
from timonelo.spatial.review import (
    ReviewDecisionState,
    VenueAssociationState,
    SpatialReviewDecision,
    compute_proof_snapshot_hash,
    match_venue_statement,
    adjudicate_spatial_objects,
)


@pytest.fixture
def sample_statements():
    stmts_path = Path("evidence/statements/statements.json")
    if stmts_path.exists():
        return json.loads(stmts_path.read_text(encoding="utf-8"))
    return {}


@pytest.fixture
def sample_deck05_proof():
    proof_path = Path("geometry/proofs/bellissima/deck05/deck05.proof.json")
    if proof_path.exists():
        return json.loads(proof_path.read_text(encoding="utf-8"))
    return {"deck": {"number": 5}, "objects": []}


def test_canonical_statement_admitted_predicate_exact_behavior():
    # 1. Axes agree -- and that alone is no longer admission. A decoded record
    #    with no link to current evidence cannot establish that its stored
    #    grant still holds, so the predicate refuses and says why. The axes
    #    question still has an honest answer; it is just a different question.
    valid_stmt = {
        "statement_id": "stmt-001",
        "evidence_condition": "SUPPORTED",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_ALLOWED",
    }
    assert lifecycle_axes_pass(valid_stmt)[0] is True
    admitted, msg = is_canonical_statement_admitted(valid_stmt)
    assert admitted is False
    assert "current publication authority was not checked" in msg

    # 2. Superficially plausible statement (SUPPORTED + APPROVED, but PUBLISH_BLOCKED)
    plausible_blocked_stmt = {
        "statement_id": "stmt-002",
        "evidence_condition": "SUPPORTED",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_BLOCKED",
    }
    admitted, msg = is_canonical_statement_admitted(plausible_blocked_stmt)
    assert admitted is False
    assert "publish_status is PUBLISH_BLOCKED" in msg

    # 3. Superficially plausible statement (APPROVED + PUBLISH_ALLOWED, but UNKNOWN evidence condition)
    unsupported_stmt = {
        "statement_id": "stmt-003",
        "evidence_condition": "UNKNOWN",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_ALLOWED",
    }
    admitted, msg = is_canonical_statement_admitted(unsupported_stmt)
    assert admitted is False
    assert "evidence_condition is UNKNOWN" in msg


def test_spatial_review_adjudication_delegates_to_canonical_gate(sample_deck05_proof):
    if not sample_deck05_proof["objects"]:
        pytest.skip("No deck 5 objects")
    target_oid = sample_deck05_proof["objects"][0]["object_id"]

    # Synthetic statement that looks superficially plausible but is blocked by canonical gate
    mock_statements = {
        "stmt-fake-theatre": {
            "statement_type": "deck.venue_present",
            "deck_number": 5,
            "target_entity": "LONDON THEATRE",
            "locator": '"London Theatre"',
            "evidence_condition": "SUPPORTED",
            "human_review_state": "APPROVED",
            "publish_status": "PUBLISH_BLOCKED", # Canonical gate rejects this!
        }
    }

    decisions = {
        target_oid: SpatialReviewDecision(
            object_id=target_oid,
            decision=ReviewDecisionState.ACCEPT,
            reviewer="synthetic_test_reviewer",
            timestamp="2026-08-24T00:00:00Z",
            deck_number=5,
            note="Extracted region aligns with the labeled area on the source drawing.",
        )
    }

    updated, deltas, audit = adjudicate_spatial_objects(sample_deck05_proof, decisions, mock_statements)
    assert len(deltas) == 1
    # Spatial review MUST receive the canonical gate rejection and keep publish status BLOCKED
    assert deltas[0].to_publish_status == "PUBLISH_BLOCKED"
    assert deltas[0].adjudication_outcome in (
        "GEOMETRY_APPROVED_IDENTITY_STATEMENT_BLOCKED",
        "GEOMETRY_APPROVED_IDENTITY_UNADMITTED",
        "GEOMETRY_APPROVED_INFRASTRUCTURE_BLOCKED",
    )


def test_phantom_reviewer_fails_closed(sample_deck05_proof, sample_statements):
    if not sample_deck05_proof["objects"]:
        pytest.skip("No deck 5 objects")
    target_oid = sample_deck05_proof["objects"][0]["object_id"]

    # 1. Empty reviewer name
    decisions_empty = {
        target_oid: SpatialReviewDecision(
            object_id=target_oid,
            decision=ReviewDecisionState.ACCEPT,
            reviewer="",
            timestamp="2026-08-24T00:00:00Z",
            deck_number=5,
        )
    }
    with pytest.raises(ValueError, match="Reviewer name is required before finalizing decisions."):
        adjudicate_spatial_objects(sample_deck05_proof, decisions_empty, sample_statements)

    # 2. UNSPECIFIED_REVIEWER phantom identity
    decisions_unspecified = {
        target_oid: SpatialReviewDecision(
            object_id=target_oid,
            decision=ReviewDecisionState.ACCEPT,
            reviewer="UNSPECIFIED_REVIEWER",
            timestamp="2026-08-24T00:00:00Z",
            deck_number=5,
        )
    }
    with pytest.raises(ValueError, match="Reviewer name is required before finalizing decisions."):
        adjudicate_spatial_objects(sample_deck05_proof, decisions_unspecified, sample_statements)

    # 3. human_curator phantom identity
    decisions_curator = {
        target_oid: SpatialReviewDecision(
            object_id=target_oid,
            decision=ReviewDecisionState.ACCEPT,
            reviewer="human_curator",
            timestamp="2026-08-24T00:00:00Z",
            deck_number=5,
        )
    }
    with pytest.raises(ValueError, match="Reviewer name is required before finalizing decisions."):
        adjudicate_spatial_objects(sample_deck05_proof, decisions_curator, sample_statements)


def test_proof_snapshot_hash_deterministic(sample_deck05_proof):
    h1 = compute_proof_snapshot_hash(sample_deck05_proof)
    h2 = compute_proof_snapshot_hash(sample_deck05_proof)
    assert h1 == h2
    assert len(h1) == 64


def test_unreviewed_object_cannot_be_promoted(sample_deck05_proof, sample_statements):
    decisions = {}
    updated, deltas, audit = adjudicate_spatial_objects(sample_deck05_proof, decisions, sample_statements)
    assert len(deltas) == 0
    assert len(audit) == 0
    assert all(o["human_review_state"] == "DRAFT" for o in updated["objects"])
    assert all(o["publish_status"] == "PUBLISH_BLOCKED" for o in updated["objects"])


def test_reject_remains_blocked(sample_deck05_proof, sample_statements):
    if not sample_deck05_proof["objects"]:
        pytest.skip("No deck 5 objects")
    target_oid = sample_deck05_proof["objects"][0]["object_id"]
    decisions = {
        target_oid: SpatialReviewDecision(
            object_id=target_oid,
            decision=ReviewDecisionState.REJECT,
            reviewer="synthetic_test_reviewer",
            timestamp="2026-08-24T00:00:00Z",
            deck_number=5,
            note="Spurious text extraction artifact",
        )
    }
    updated, deltas, audit = adjudicate_spatial_objects(sample_deck05_proof, decisions, sample_statements)
    assert len(deltas) == 1
    assert deltas[0].to_review_state == "REJECTED"
    assert deltas[0].to_publish_status == "PUBLISH_BLOCKED"
    assert deltas[0].to_condition == "UNSUPPORTED"
    assert audit[0]["reviewer"] == "synthetic_test_reviewer"


def test_finalization_touches_only_reviewed_object_ids(sample_deck05_proof, sample_statements):
    if len(sample_deck05_proof["objects"]) < 2:
        pytest.skip("Need at least 2 objects")
    oid0 = sample_deck05_proof["objects"][0]["object_id"]
    oid1 = sample_deck05_proof["objects"][1]["object_id"]
    decisions = {
        oid0: SpatialReviewDecision(
            object_id=oid0,
            decision=ReviewDecisionState.ACCEPT,
            reviewer="synthetic_test_reviewer",
            timestamp="2026-08-24T00:00:00Z",
            deck_number=5,
        )
    }
    updated, deltas, audit = adjudicate_spatial_objects(sample_deck05_proof, decisions, sample_statements)
    assert len(deltas) == 1
    assert deltas[0].object_id == oid0
    # Object 1 must be untouched
    obj1_after = next(o for o in updated["objects"] if o["object_id"] == oid1)
    assert obj1_after["human_review_state"] == "DRAFT"
    assert obj1_after["publish_status"] == "PUBLISH_BLOCKED"
