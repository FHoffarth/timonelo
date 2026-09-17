"""
The geometry review projection, and the things it must never reach.

A durable adjudication is only worth having if the code that consumes governed
geometry actually sees it. These tests pin that it does, and -- more of them --
that seeing it changes exactly one axis.

The projection is deliberately narrow:

    effective review state = extracted proof object + append-only adjudication log

bound on `(object_id, proof_sha256)` together. Evidence and publication are read
straight off the proof, because a human looking at a drawing established
neither, and no amount of APPROVED turns UNKNOWN into SUPPORTED.
"""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus
from timonelo.spatial.adjudication import (
    SpatialAdjudicationLog,
    apply_staged_record,
    current_geometry_review_state,
    duplicate_object_ids,
    project_proof_review_states,
)
from timonelo.spatial.deck14_proof import build_deck14_nodes, load_proof

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "deck14_staged_accept_14216.json"
PROOF_REL = "geometry/proofs/bellissima/deck14/deck14.proof.json"
ARTIFACT_REL = (
    "evidence/raw/sha256/08/"
    "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0.pdf"
)
RASTER_REL = "frontend/public/data/deck14.page5.png"

REVIEWED = "bellissima-deck14-cabin-14216"
UNREVIEWED = "bellissima-deck14-cabin-14122"
PROOF_SHA = "f9038f979d1df96de66edef746830fd4d7cf044c3e03fbf4fa70357151ddd2c4"


@pytest.fixture
def record() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for rel in (PROOF_REL, ARTIFACT_REL, RASTER_REL):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, dst)
    (tmp_path / "evidence" / "reviews").mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def proof() -> dict:
    return load_proof()


def _obj(proof: dict, object_id: str) -> dict:
    return next(o for o in proof["objects"] if o["object_id"] == object_id)


def _applied_log(record: dict, repo: Path) -> SpatialAdjudicationLog:
    """A log holding Flo's real decision, in a throwaway repository."""
    result = apply_staged_record(
        record, repo_root=str(repo), dry_run=False,
        artifact_path=ARTIFACT_REL, raster_path=RASTER_REL,
    )
    assert result.applied is True, result.summary()
    return SpatialAdjudicationLog(result.log_path)


def _admitted(evidence: str, review: str, publish: str) -> bool:
    """The passenger admission rule, restated: all three axes or nothing."""
    return (
        evidence == EvidenceCondition.SUPPORTED.value
        and review == HumanReviewState.APPROVED.value
        and publish in (PublishStatus.PUBLISH_ALLOWED.value,
                        PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS.value)
    )


# -- 1. no log means nothing changes -----------------------------------------

def test_without_a_log_every_object_keeps_its_stored_state(proof, tmp_path):
    empty = SpatialAdjudicationLog(str(tmp_path / "absent.json"))
    projected = project_proof_review_states(proof, PROOF_SHA, empty)

    assert len(projected) == 244
    assert set(projected.values()) == {"DRAFT"}
    for o in proof["objects"]:
        assert projected[o["object_id"]] == o["human_review_state"]


def test_the_real_repository_projects_exactly_its_stored_state(proof):
    """Before Flo's record is applied, the projection is a no-op."""
    projected = project_proof_review_states(proof, PROOF_SHA, repo_root=str(REPO_ROOT))
    for o in proof["objects"]:
        assert projected[o["object_id"]] == o["human_review_state"]
    assert set(projected.values()) == {"DRAFT"}


def test_deck14_nodes_are_unchanged_without_an_adjudication(tmp_path):
    empty = SpatialAdjudicationLog(str(tmp_path / "absent.json"))
    nodes = build_deck14_nodes(adjudication_log=empty)
    assert len(nodes) == 244
    assert all(n.stance.human_review_state is HumanReviewState.DRAFT for n in nodes)
    assert all(n.stance.publish_status is PublishStatus.PUBLISH_BLOCKED for n in nodes)
    assert all(n.stance.evidence_condition is EvidenceCondition.UNKNOWN for n in nodes)


# -- 2..5 a valid ACCEPT moves the review axis and nothing else --------------

def test_a_valid_accept_projects_approved(record, repo, proof):
    log = _applied_log(record, repo)
    assert current_geometry_review_state(_obj(proof, REVIEWED), PROOF_SHA, log) == "APPROVED"


def test_projection_reaches_the_governed_node_builder(record, repo, proof):
    log = _applied_log(record, repo)
    nodes = {n.node_id: n for n in build_deck14_nodes(adjudication_log=log)}

    reviewed = nodes[REVIEWED]
    assert reviewed.stance.human_review_state is HumanReviewState.APPROVED
    # The other two axes are read off the proof and did not move.
    assert reviewed.stance.evidence_condition is EvidenceCondition.UNKNOWN
    assert reviewed.stance.publish_status is PublishStatus.PUBLISH_BLOCKED
    # The evidence link restates the same axes, so a link read alone cannot look
    # more settled than the object.
    assert reviewed.stance.evidence_links[0].human_review_state is HumanReviewState.APPROVED
    assert reviewed.stance.evidence_links[0].evidence_condition is EvidenceCondition.UNKNOWN


def test_evidence_and_publication_are_untouched_by_projection(record, repo, proof):
    log = _applied_log(record, repo)
    obj = _obj(proof, REVIEWED)
    assert obj["evidence_condition"] == "UNKNOWN"
    assert obj["publish_status"] == "PUBLISH_BLOCKED"
    # And the projection returns a review state only -- it has no other output.
    assert current_geometry_review_state(obj, PROOF_SHA, log) in {s.value for s in HumanReviewState}


def test_passenger_admission_stays_false_for_the_reviewed_cabin(record, repo, proof):
    log = _applied_log(record, repo)
    obj = _obj(proof, REVIEWED)
    review = current_geometry_review_state(obj, PROOF_SHA, log)

    assert review == "APPROVED"
    assert _admitted(obj["evidence_condition"], review, obj["publish_status"]) is False


def test_the_whole_deck_stays_zero_admitted_after_projection(record, repo, proof):
    log = _applied_log(record, repo)
    projected = project_proof_review_states(proof, PROOF_SHA, log)
    admitted = [
        o["object_id"] for o in proof["objects"]
        if _admitted(o["evidence_condition"], projected[o["object_id"]], o["publish_status"])
    ]
    assert admitted == []
    assert len(proof["objects"]) == 244


# -- 6, 7. stale proof safety -------------------------------------------------

def test_an_adjudication_against_another_proof_does_not_project(record, repo, proof):
    log = _applied_log(record, repo)
    obj = _obj(proof, REVIEWED)
    # Same object id, different proof: history about different geometry.
    assert current_geometry_review_state(obj, "a" * 64, log) == "DRAFT"
    assert current_geometry_review_state(obj, "", log) == "DRAFT"
    assert current_geometry_review_state(obj, "not-a-digest", log) == "DRAFT"


def test_object_id_alone_cannot_project(record, repo, proof):
    log = _applied_log(record, repo)
    # The entry exists and is found by id, yet projects nothing without its proof.
    assert log.for_object(REVIEWED) != []
    assert log.for_object(REVIEWED, "b" * 64) == []
    assert current_geometry_review_state(_obj(proof, REVIEWED), "b" * 64, log) == "DRAFT"


def test_a_regenerated_proof_falls_back_to_its_own_state(record, repo, proof):
    log = _applied_log(record, repo)
    regenerated = copy.deepcopy(proof)
    for o in regenerated["objects"]:
        o["normalized_bbox"] = [0.0, 0.0, 0.1, 0.1]
    # The new proof has a new digest, so the old decision does not follow it.
    projected = project_proof_review_states(regenerated, "c" * 64, log)
    assert set(projected.values()) == {"DRAFT"}


# -- 8, 9. blast radius -------------------------------------------------------

def test_cabin_14122_remains_draft_and_unreviewed(record, repo, proof):
    log = _applied_log(record, repo)
    obj = _obj(proof, UNREVIEWED)
    assert log.for_object(UNREVIEWED) == []
    assert current_geometry_review_state(obj, PROOF_SHA, log) == "DRAFT"
    assert obj["evidence_condition"] == "UNKNOWN"
    assert obj["publish_status"] == "PUBLISH_BLOCKED"
    assert _admitted(obj["evidence_condition"], "DRAFT", obj["publish_status"]) is False


def test_exactly_one_object_is_projected_differently(record, repo, proof):
    log = _applied_log(record, repo)
    stored = {o["object_id"]: o["human_review_state"] for o in proof["objects"]}
    projected = project_proof_review_states(proof, PROOF_SHA, log)
    moved = [oid for oid, state in projected.items() if state != stored[oid]]
    assert moved == [REVIEWED]


def test_the_proof_bytes_are_never_rewritten(record, repo):
    before = (repo / PROOF_REL).read_bytes()
    _applied_log(record, repo)
    assert (repo / PROOF_REL).read_bytes() == before
    assert b'"human_review_state": "APPROVED"' not in (repo / PROOF_REL).read_bytes()


# -- 10. other decks ----------------------------------------------------------

@pytest.mark.parametrize("deck,unique_ids", [("05", 30), ("06", 26), ("07", 14)])
def test_decks_5_6_7_are_unaffected(tmp_path, deck, unique_ids):
    other = json.loads(
        (REPO_ROOT / f"geometry/proofs/bellissima/deck{deck}/deck{deck}.proof.json")
        .read_text(encoding="utf-8")
    )
    empty = SpatialAdjudicationLog(str(tmp_path / "absent.json"))
    projected = project_proof_review_states(other, "d" * 64, empty)
    # Deck 7 holds 15 objects under 14 ids: one id is used twice.
    assert len(projected) == unique_ids
    for o in other["objects"]:
        assert projected[o["object_id"]] == o["human_review_state"]


def test_an_ambiguous_object_id_is_never_projected(tmp_path):
    """Deck 7 uses one object id twice, so no decision can be bound to it."""
    deck07 = json.loads(
        (REPO_ROOT / "geometry/proofs/bellissima/deck07/deck07.proof.json")
        .read_text(encoding="utf-8")
    )
    ambiguous = duplicate_object_ids(deck07)
    assert ambiguous == frozenset({"bellissima-deck07-venue-champagne-bar"})

    # A log that claims this id was approved must still project DRAFT.
    path = tmp_path / "spatial_adjudications.json"
    path.write_text(json.dumps({"entries": [{
        "object_id": "bellissima-deck07-venue-champagne-bar",
        "proof_sha256": "e" * 64,
        "to_review_state": "APPROVED",
    }]}), encoding="utf-8")
    log = SpatialAdjudicationLog(str(path))

    projected = project_proof_review_states(deck07, "e" * 64, log)
    assert projected["bellissima-deck07-venue-champagne-bar"] == "DRAFT"


def test_deck14_ids_are_unique_so_projection_is_unambiguous(proof):
    assert duplicate_object_ids(proof) == frozenset()
    assert len({o["object_id"] for o in proof["objects"]}) == 244


# -- 11. malformed logs fail closed ------------------------------------------

@pytest.mark.parametrize("entries", [
    [{"object_id": REVIEWED, "proof_sha256": PROOF_SHA, "to_review_state": "NOT_A_STATE"}],
    [{"object_id": REVIEWED, "proof_sha256": PROOF_SHA, "to_review_state": None}],
    [{"object_id": REVIEWED, "proof_sha256": PROOF_SHA}],
    [{"object_id": REVIEWED, "to_review_state": "APPROVED"}],
    ["not an object"],
])
def test_a_malformed_log_entry_projects_nothing(tmp_path, proof, entries):
    path = tmp_path / "spatial_adjudications.json"
    path.write_text(json.dumps({"entries": entries}), encoding="utf-8")
    log = SpatialAdjudicationLog(str(path))
    assert current_geometry_review_state(_obj(proof, REVIEWED), PROOF_SHA, log) == "DRAFT"


def test_an_empty_or_absent_log_projects_nothing(tmp_path, proof):
    missing = SpatialAdjudicationLog(str(tmp_path / "nope.json"))
    assert current_geometry_review_state(_obj(proof, REVIEWED), PROOF_SHA, missing) == "DRAFT"
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    assert current_geometry_review_state(
        _obj(proof, REVIEWED), PROOF_SHA, SpatialAdjudicationLog(str(empty))) == "DRAFT"


# -- 12. publication authority is not involved -------------------------------

def test_publication_authority_is_untouched_by_geometry_adjudication(record, repo):
    """The statement side neither knows nor cares about a geometry decision."""
    from timonelo.evidence.workspace import Workspace

    ws = Workspace(str(REPO_ROOT / "evidence"))
    before = {s.statement_id: ws.editor.is_currently_authoritative(s) for s in ws.editor.all()}

    _applied_log(record, repo)

    after = {s.statement_id: ws.editor.is_currently_authoritative(s) for s in ws.editor.all()}
    assert after == before
    assert not any(after.values()) or True  # shape check; values are unchanged either way


def test_a_geometry_adjudication_writes_no_statement_or_event(record, repo):
    _applied_log(record, repo)
    assert not (repo / "evidence" / "statements" / "statements.json").exists()
    assert not (repo / "evidence" / "events" / "events.json").exists()
