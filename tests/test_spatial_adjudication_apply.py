"""
The governed apply path for staged human geometry adjudications.

A staged record is a proposal. These tests pin what it takes to turn one into
repository truth, and -- more of them -- what it never buys. The fixture is the
real session: one human, one object, `bellissima-deck14-cabin-14216`, ACCEPT.

Every test runs against a temporary copy of the repository, so nothing here can
apply Flo's decision to the real store by accident.
"""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus
from timonelo.spatial.adjudication import (
    ApplyRefusal,
    SpatialAdjudicationLog,
    StagedRecordError,
    apply_staged_record,
    current_geometry_review_state,
    evaluate_staged_record,
    require_apply,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "deck14_staged_accept_14216.json"
OBJECT_ID = "bellissima-deck14-cabin-14216"
PROOF_REL = "geometry/proofs/bellissima/deck14/deck14.proof.json"
ARTIFACT_REL = (
    "evidence/raw/sha256/08/"
    "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0.pdf"
)
RASTER_REL = "frontend/public/data/deck14.page5.png"


@pytest.fixture
def record() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway repository holding only what the apply path reads."""
    for rel in (PROOF_REL, ARTIFACT_REL, RASTER_REL):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, dst)
    (tmp_path / "evidence" / "reviews").mkdir(parents=True, exist_ok=True)
    return tmp_path


def _apply(record: dict, repo: Path, *, dry_run: bool = True):
    return apply_staged_record(
        record,
        repo_root=str(repo),
        dry_run=dry_run,
        artifact_path=ARTIFACT_REL,
        raster_path=RASTER_REL,
    )


def _proof(repo: Path) -> dict:
    return json.loads((repo / PROOF_REL).read_text(encoding="utf-8"))


def _obj(repo: Path, object_id: str = OBJECT_ID) -> dict:
    return next(o for o in _proof(repo)["objects"] if o["object_id"] == object_id)


# -- the happy path -----------------------------------------------------------

def test_a_valid_staged_accept_is_admitted(record, repo):
    result = _apply(record, repo)
    assert result.refusals == []
    assert len(result.planned) == 1
    m = result.planned[0]
    assert m.object_id == OBJECT_ID
    assert m.from_review_state == HumanReviewState.DRAFT.value
    assert m.to_review_state == HumanReviewState.APPROVED.value
    assert m.geometry_judgement == "ACCEPTED"
    assert m.reviewer == "Flo"


def test_a_dry_run_writes_nothing(record, repo):
    log_path = repo / "evidence" / "reviews" / "spatial_adjudications.json"
    before = _proof(repo)
    result = _apply(record, repo, dry_run=True)

    assert result.dry_run is True
    assert result.applied is False
    assert not log_path.exists()
    assert _proof(repo) == before


def test_applying_appends_a_log_entry_and_leaves_the_proof_alone(record, repo):
    proof_before = (repo / PROOF_REL).read_bytes()
    result = _apply(record, repo, dry_run=False)

    assert result.applied is True
    # The proof is an extraction record. A review outcome does not rewrite it,
    # which is also what keeps proof_sha256 a usable binding.
    assert (repo / PROOF_REL).read_bytes() == proof_before

    log = SpatialAdjudicationLog(result.log_path)
    assert len(log.all()) == 1
    entry = log.all()[0]
    assert entry["object_id"] == OBJECT_ID
    assert entry["decision"] == "ACCEPT"
    assert entry["reviewer"] == "Flo"
    assert entry["from_review_state"] == "DRAFT"
    assert entry["to_review_state"] == "APPROVED"


def test_the_log_answers_every_audit_question(record, repo):
    result = _apply(record, repo, dry_run=False)
    entry = SpatialAdjudicationLog(result.log_path).all()[0]
    for key in (
        "reviewer", "reviewed_at", "object_id", "decision",
        "proof_sha256", "source_artifact_sha256", "review_image_sha256",
        "from_review_state", "to_review_state", "staged_record_generated_at",
    ):
        assert entry.get(key), f"{key} missing from the durable record"


def test_review_state_becomes_a_projection_of_proof_plus_log(record, repo):
    obj = _obj(repo)
    sha = record["proof_sha256"]
    empty = SpatialAdjudicationLog(str(repo / "evidence/reviews/spatial_adjudications.json"))
    assert current_geometry_review_state(obj, sha, empty) == "DRAFT"

    result = _apply(record, repo, dry_run=False)
    after = SpatialAdjudicationLog(result.log_path)
    assert current_geometry_review_state(obj, sha, after) == "APPROVED"
    # A decision about one proof says nothing about different geometry.
    assert current_geometry_review_state(obj, "0" * 64, after) == "DRAFT"


# -- what an ACCEPT never buys ------------------------------------------------

def test_accept_preserves_unknown_evidence_and_blocked_publication(record, repo):
    result = _apply(record, repo, dry_run=False)
    m = result.planned[0]
    assert m.evidence_condition == EvidenceCondition.UNKNOWN.value
    assert m.publish_status == PublishStatus.PUBLISH_BLOCKED.value

    obj = _obj(repo)
    assert obj["evidence_condition"] == "UNKNOWN"
    assert obj["publish_status"] == "PUBLISH_BLOCKED"

    entry = SpatialAdjudicationLog(result.log_path).all()[0]
    assert entry["evidence_condition_unchanged"] == "UNKNOWN"
    assert entry["publish_status_unchanged"] == "PUBLISH_BLOCKED"


def test_accept_creates_no_evidence_event(record, repo):
    events = repo / "evidence" / "events" / "events.json"
    _apply(record, repo, dry_run=False)
    assert not events.exists(), "a review act must not write an evidence event"


def test_accept_creates_no_cabin_identity_statement(record, repo):
    statements = repo / "evidence" / "statements" / "statements.json"
    _apply(record, repo, dry_run=False)
    assert not statements.exists(), "a review act must not author identity statements"


def test_passenger_admission_remains_false_after_apply(record, repo):
    _apply(record, repo, dry_run=False)
    obj = _obj(repo)
    # The frontend predicate's rule, restated: SUPPORTED + APPROVED +
    # PUBLISH_ALLOWED. Evidence never moved, so this is false however the review
    # axis ends up.
    admitted = (
        obj["evidence_condition"] == "SUPPORTED"
        and obj["human_review_state"] == "APPROVED"
        and obj["publish_status"] in ("PUBLISH_ALLOWED", "PUBLISH_ALLOWED_WITH_WARNINGS")
    )
    assert admitted is False


def test_a_record_that_would_move_evidence_is_refused(record, repo):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["postReviewState"]["evidenceCondition"] = "SUPPORTED"
    result = _apply(tampered, repo)
    assert ApplyRefusal.REVIEW_ACT_WOULD_CHANGE_EVIDENCE in result.refusal_codes


def test_a_record_that_would_publish_is_refused(record, repo):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["postReviewState"]["publishStatus"] = "PUBLISH_ALLOWED"
    result = _apply(tampered, repo)
    assert ApplyRefusal.REVIEW_ACT_WOULD_CHANGE_PUBLICATION in result.refusal_codes


# -- provenance binding -------------------------------------------------------

def test_proof_digest_mismatch_refuses(record, repo):
    tampered = copy.deepcopy(record)
    tampered["proof_sha256"] = "b" * 64
    result = _apply(tampered, repo)
    assert ApplyRefusal.PROOF_DIGEST_MISMATCH in result.refusal_codes
    assert result.planned == []


def test_a_regenerated_proof_refuses_the_old_record(record, repo):
    proof = _proof(repo)
    proof["objects"][0]["normalized_bbox"] = [0.1, 0.1, 0.2, 0.2]
    (repo / PROOF_REL).write_text(json.dumps(proof, indent=2), encoding="utf-8")
    result = _apply(record, repo)
    assert ApplyRefusal.PROOF_DIGEST_MISMATCH in result.refusal_codes


def test_artifact_digest_mismatch_refuses(record, repo):
    (repo / ARTIFACT_REL).write_bytes(b"a different document")
    result = _apply(record, repo)
    assert ApplyRefusal.ARTIFACT_DIGEST_MISMATCH in result.refusal_codes


def test_raster_digest_mismatch_refuses(record, repo):
    (repo / RASTER_REL).write_bytes(b"a different raster")
    result = _apply(record, repo)
    assert ApplyRefusal.RASTER_DIGEST_MISMATCH in result.refusal_codes


def test_missing_files_refuse_rather_than_skip(record, repo):
    (repo / RASTER_REL).unlink()
    result = _apply(record, repo)
    assert ApplyRefusal.RASTER_NOT_FOUND in result.refusal_codes


# -- object and state integrity ----------------------------------------------

def test_missing_object_refuses(record, repo):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["objectId"] = "bellissima-deck14-cabin-does-not-exist"
    result = _apply(tampered, repo)
    assert ApplyRefusal.OBJECT_NOT_IN_PROOF in result.refusal_codes


def test_deck_drift_refuses(record, repo):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["deckNumber"] = 5
    result = _apply(tampered, repo)
    assert ApplyRefusal.OBJECT_IDENTITY_DRIFT in result.refusal_codes


def test_pre_state_drift_refuses(record, repo):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["preReviewState"]["humanReviewState"] = "UNDER_REVIEW"
    result = _apply(tampered, repo)
    assert ApplyRefusal.PRE_STATE_DRIFT in result.refusal_codes


def test_a_record_made_against_an_already_adjudicated_object_refuses(record, repo):
    _apply(record, repo, dry_run=False)
    # A second, different decision made from the same stale DRAFT view.
    second = copy.deepcopy(record)
    second["entries"][0]["decision"] = "REJECT"
    second["entries"][0]["geometryJudgement"] = "REJECTED"
    second["entries"][0]["timestamp"] = "2026-09-18T09:00:00.000Z"
    result = _apply(second, repo)
    assert result.refusals, "a conflicting decision must not silently replace the first"
    assert result.planned == []


# -- reviewer and decision ----------------------------------------------------

@pytest.mark.parametrize("who", ["", "   ", "UNSPECIFIED_REVIEWER", "human_curator", "null"])
def test_placeholder_reviewer_refuses(record, repo, who):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["reviewer"] = who
    tampered["reviewer"] = who
    result = _apply(tampered, repo)
    assert ApplyRefusal.REVIEWER_MISSING_OR_PLACEHOLDER in result.refusal_codes


@pytest.mark.parametrize("decision", ["UNREVIEWED", "APPROVE", "", "PUBLISH", None])
def test_unsupported_decision_refuses(record, repo, decision):
    tampered = copy.deepcopy(record)
    tampered["entries"][0]["decision"] = decision
    result = _apply(tampered, repo)
    assert ApplyRefusal.UNSUPPORTED_DECISION in result.refusal_codes


# -- record shape -------------------------------------------------------------

@pytest.mark.parametrize(
    "mutate,expected",
    [
        (lambda r: r.update({"record_type": "something.else.v9"}), ApplyRefusal.UNSUPPORTED_RECORD_TYPE),
        (lambda r: r.update({"application_status": "APPLIED"}), ApplyRefusal.NOT_STAGED),
        (lambda r: r.update({"applied_to_repository": True}), ApplyRefusal.ALREADY_MARKED_APPLIED),
        (lambda r: r.update({"entries": []}), ApplyRefusal.MALFORMED_RECORD),
        (lambda r: r.update({"proof_sha256": "not-a-digest"}), ApplyRefusal.MALFORMED_RECORD),
    ],
)
def test_malformed_records_refuse_atomically(record, repo, mutate, expected):
    tampered = copy.deepcopy(record)
    mutate(tampered)
    result = _apply(tampered, repo)
    assert expected in result.refusal_codes
    assert result.planned == []
    assert not (repo / "evidence" / "reviews" / "spatial_adjudications.json").exists()


def test_a_non_object_record_refuses(repo):
    for junk in ([], "staged", 7, None):
        result = apply_staged_record(junk, repo_root=str(repo))
        assert ApplyRefusal.MALFORMED_RECORD in result.refusal_codes


def test_require_apply_raises_on_refusal(record, repo):
    tampered = copy.deepcopy(record)
    tampered["proof_sha256"] = "c" * 64
    with pytest.raises(StagedRecordError):
        require_apply(tampered, repo_root=str(repo), dry_run=False,
                      artifact_path=ARTIFACT_REL, raster_path=RASTER_REL)


# -- replay -------------------------------------------------------------------

def test_replaying_the_same_record_does_not_duplicate_history(record, repo):
    first = _apply(record, repo, dry_run=False)
    assert first.applied is True
    assert len(SpatialAdjudicationLog(first.log_path).all()) == 1

    second = _apply(record, repo, dry_run=False)
    assert second.already_applied is True
    assert second.applied is False
    assert second.planned == []
    assert len(SpatialAdjudicationLog(second.log_path).all()) == 1

    third = _apply(record, repo, dry_run=False)
    assert len(SpatialAdjudicationLog(third.log_path).all()) == 1


# -- blast radius -------------------------------------------------------------

def test_no_other_deck14_object_is_touched(record, repo):
    before = {o["object_id"]: dict(o) for o in _proof(repo)["objects"]}
    result = _apply(record, repo, dry_run=False)

    after = {o["object_id"]: dict(o) for o in _proof(repo)["objects"]}
    assert after == before, "applying one decision must not mutate the proof at all"
    assert len(before) == 244

    log = SpatialAdjudicationLog(result.log_path)
    assert {e["object_id"] for e in log.all()} == {OBJECT_ID}


def test_cabin_14122_is_untouched_and_unreviewed(record, repo):
    result = _apply(record, repo, dry_run=False)
    log = SpatialAdjudicationLog(result.log_path)

    obj = _obj(repo, "bellissima-deck14-cabin-14122")
    assert obj["human_review_state"] == "DRAFT"
    assert obj["evidence_condition"] == "UNKNOWN"
    assert obj["publish_status"] == "PUBLISH_BLOCKED"
    assert log.for_object("bellissima-deck14-cabin-14122") == []
    assert current_geometry_review_state(obj, record["proof_sha256"], log) == "DRAFT"


def test_the_real_repository_has_no_adjudication_log_yet(record):
    """Nothing in this sprint applies Flo's decision to the real store."""
    assert not (REPO_ROOT / "evidence" / "reviews" / "spatial_adjudications.json").exists()


def test_evaluate_never_writes(record, repo):
    evaluate_staged_record(
        record,
        repo_root=str(repo),
        artifact_path=ARTIFACT_REL,
        raster_path=RASTER_REL,
    )
    assert not (repo / "evidence" / "reviews" / "spatial_adjudications.json").exists()
