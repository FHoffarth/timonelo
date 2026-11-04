"""Private real-source batch: reuse genuine recorded owner decisions, never infer them."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import os
import shutil

import pytest

from timonelo.factory.evidence_batch import BatchError, inspect_batch, process_private_batch
from timonelo.canonical import canonical_dump

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reports/evidence-factory-automation"

# Immutable pre-apply contract from the owner-authorized frozen manifest.
# Reconstruct only on a private test copy, never by editing the repository.
PRE_APPLY_HASHES = {
    "events/events.json": "f04708461de9f87d30ac052810fb810b7ebb305eb6093f324528480302efa3c6",
    "reviews/conflicts.json": "78234ec41327ce464dd9ea534499d015e5de1fc125cc57688a324cf5912629cb",
    "reviews/log.json": "a9a8050932420842c8120eebfb8dfc8ea6b101cb58e5aaa09f0a3851d17702e0",
    "statements/statements.json": "50d3ccb7e6cb00a828274877e258c26d4815df407bf3c3079402c40d0d8b731e",
}


def _restore_frozen_pre_apply_evidence(evidence):
    """Recover the hash-pinned historical cohort, independent of later additions.

    Only private test copies are passed here. Prefix lengths describe the
    immutable historical logs, not a maximum size of the canonical collection.
    Every reconstructed byte must still match the original four digests.
    """
    live = json.loads((evidence / "statements/statements.json").read_text(encoding="utf8"))
    statements = {f"STM-{n:04d}": live[f"STM-{n:04d}"] for n in range(1, 411)}
    events = json.loads((evidence / "events/events.json").read_text(encoding="utf8"))
    reviews = json.loads((evidence / "reviews/log.json").read_text(encoding="utf8"))
    conflicts = json.loads((evidence / "reviews/conflicts.json").read_text(encoding="utf8"))
    conflicts = {"conflicts": {"CFL-0001": conflicts["conflicts"]["CFL-0001"]},
                 "history": conflicts["history"][:2], "detection_runs": conflicts["detection_runs"][:198]}
    restored = {
        "statements/statements.json": statements,
        "events/events.json": events[:18],
        "reviews/log.json": reviews[:397],
        "reviews/conflicts.json": conflicts,
    }
    for rel, data in restored.items():
        path = evidence / rel
        if hashlib.sha256(path.read_bytes()).hexdigest() != PRE_APPLY_HASHES[rel]:
            canonical_dump(data, str(path))
        assert hashlib.sha256(path.read_bytes()).hexdigest() == PRE_APPLY_HASHES[rel], rel
    assert len(statements) == 410


@pytest.fixture(scope="session")
def pre_apply_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("frozen-pre-apply")
    for folder in ("evidence", "knowledge"):
        shutil.copytree(ROOT / folder, root / folder)
    catalog = Path("frontend/src/passenger/fleetCatalog.json")
    (root / catalog).parent.mkdir(parents=True)
    shutil.copyfile(ROOT / catalog, root / catalog)
    _restore_frozen_pre_apply_evidence(root / "evidence")
    return root


@pytest.fixture
def inputs():
    return (json.loads((PACKET / "pilot-batch.json").read_text(encoding="utf8")),
            json.loads((PACKET / "pilot-approvals.json").read_text(encoding="utf8")))


def test_frozen_pre_apply_fixture_ignores_later_pending_additions(pre_apply_root, tmp_path):
    from timonelo.evidence.workspace import Workspace

    copy = tmp_path / "later-evidence"
    shutil.copytree(pre_apply_root / "evidence", copy)
    workspace = Workspace(str(copy))
    added = workspace.editor.create(entity_id="venue:MSC-BELLISSIMA:fixture-only-addition",
        question_id="Q-0016", statement_type="deck.venue_present", value=[5], artifact_id="ART-0001",
        locator="Synthetic fixture, never canonical or published", read_by="Fixture instrument", read_on="2026-11-04")
    assert not workspace.editor.authority.evaluate(added).admitted
    # Preserve old persisted records; editor serialization of legacy values
    # is a separate migration and is not part of this fixture-only addition.
    old = json.loads((pre_apply_root / "evidence/statements/statements.json").read_text(encoding="utf8"))
    canonical_dump({**old, added.statement_id: added.to_dict()}, str(copy / "statements/statements.json"))
    _restore_frozen_pre_apply_evidence(copy)
    assert all(hashlib.sha256((copy / rel).read_bytes()).hexdigest() == digest
               for rel, digest in PRE_APPLY_HASHES.items())


def test_real_approved_eight_use_existing_gates_and_leave_source_unchanged(pre_apply_root, inputs, tmp_path):
    batch, decisions = inputs
    result = process_private_batch(pre_apply_root, batch, decisions, tmp_path / "private")
    assert result["counts"] == {"admitted": 8, "blocked": 0, "pending": 0, "rejected": 0}
    assert result["original_statement_count"] == 410
    assert result["original_states_and_authority_unchanged"]
    assert result["source_unchanged"] and result["art2_unchanged"]
    assert result["human_approvals_recorded"] == 8
    assert len({r["statement_id"] for r in result["claims"]}) == 8
    assert all(r["truth_engine_known"] for r in result["claims"])
    assert all(r["review_entry"]["actor"] == "Product Owner" for r in result["claims"])
    assert all(r["review_entry"]["occurred_on"] == "2026-11-03" for r in result["claims"])
    snapshot = json.loads((tmp_path / "private/private.snapshot.json").read_text())
    profile = json.loads(snapshot["payload"])["ships"]["msc-bellissima"]
    assert len(profile["facts"]) == 8
    assert all(f["artifact_id"] == "ART-0001" for f in profile["facts"])
    assert not list((tmp_path / "private").rglob("*.pdf"))
    assert json.loads((tmp_path / "private/decision-records.json").read_text()) == decisions


@pytest.mark.parametrize("field,value", [
    ("value", [7]), ("source_version", "12.2025 DEU"),
    ("target_vessel", "IMO9803613"), ("artifact_id", "ART-0002"),
    ("artifact_sha256", "f" * 64), ("locator", "different locator"),
    ("page", 4), ("entity_id", "venue:MSC-BELLISSIMA:other"),
    ("question_id", "Q-0001"), ("statement_type", "cabin.exists"),
    ("scope", "CURRENT_OPERATIONS"), ("source_boxes", [[0, 0, 1, 1]]),
])
def test_approval_cannot_be_reused_after_binding_change(pre_apply_root, inputs, field, value):
    batch, decisions = inputs
    batch["claims"][0][field] = value
    row = inspect_batch(pre_apply_root, batch, decisions)["claims"][0]
    assert row["status"] == "BLOCKED"
    assert "APPROVAL_BINDING_MISMATCH" in row["reasons"]


def test_missing_deferred_and_rejected_decisions_never_create_approved_records(pre_apply_root, inputs, tmp_path):
    batch, decisions = inputs
    decisions["decisions"][0]["decision"] = "DEFER"
    decisions["decisions"][1]["decision"] = "REJECT"
    decisions["decisions"] = decisions["decisions"][:2]
    result = process_private_batch(pre_apply_root, batch, decisions, tmp_path / "pending")
    assert result["counts"] == {"admitted": 0, "blocked": 0, "pending": 7, "rejected": 1}
    assert result["human_approvals_recorded"] == 0
    assert not json.loads(json.loads((tmp_path / "pending/private.snapshot.json").read_text())["payload"])["ships"]["msc-bellissima"]["facts"]


def test_duplicate_selection_and_unconfigured_drive_route_refuse(pre_apply_root, inputs):
    batch, decisions = inputs
    batch["claims"] = [batch["claims"][0], deepcopy(batch["claims"][0])]
    with pytest.raises(BatchError, match="DUPLICATE_CLAIM_ID"):
        inspect_batch(pre_apply_root, batch, decisions)
    batch["claims"] = batch["claims"][:1]
    batch["source_route"] = "GOOGLE_DRIVE"
    with pytest.raises(BatchError, match="UNCONFIGURED_SOURCE_ROUTE"):
        inspect_batch(pre_apply_root, batch, decisions)


def test_claim_contradiction_is_an_unresolved_exception(pre_apply_root, inputs):
    batch, decisions = inputs
    claim = batch["claims"][1]
    claim["value"] = [5]
    decisions["decisions"][1]["binding"] = deepcopy(claim)  # Synthetic negative control, not owner data.
    row = inspect_batch(pre_apply_root, batch, decisions)["claims"][1]
    assert row["status"] == "BLOCKED" and "CONTRADICTORY_EXISTING_CLAIM" in row["reasons"]


def test_source_revision_is_checked_even_when_input_decision_is_forged(pre_apply_root, inputs):
    batch, decisions = inputs
    claim = batch["claims"][0]
    claim["artifact_sha256"] = "0" * 64
    decisions["decisions"][0]["binding"] = deepcopy(claim)
    row = inspect_batch(pre_apply_root, batch, decisions)["claims"][0]
    assert row["status"] == "BLOCKED" and "ARTIFACT_SHA_MISMATCH" in row["reasons"]


def test_output_inside_source_or_existing_directory_is_not_allowed(pre_apply_root, inputs, tmp_path):
    batch, decisions = inputs
    with pytest.raises(BatchError, match="OUTPUT_INSIDE_SOURCE"):
        process_private_batch(pre_apply_root, batch, decisions, pre_apply_root / "frontend/public/new-snapshot")
    with pytest.raises(BatchError, match="OUTPUT_EXISTS"):
        process_private_batch(pre_apply_root, batch, decisions, tmp_path)


def test_missing_human_metadata_does_not_manufacture_a_reviewer(pre_apply_root, inputs):
    batch, decisions = inputs
    decisions["reviewer"] = ""
    plan = inspect_batch(pre_apply_root, batch, decisions)
    assert all(r["status"] == "BLOCKED" for r in plan["claims"])
    assert all("MISSING_HUMAN_REVIEW_METADATA" in r["reasons"] for r in plan["claims"])


def test_inspection_never_calls_a_writer_on_the_source_checkout(pre_apply_root, inputs, monkeypatch):
    batch, decisions = inputs
    original = os.makedirs

    def outside_source(path, *args, **kwargs):
        assert not Path(path).resolve().is_relative_to(pre_apply_root), "source directory creation attempted"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(os, "makedirs", outside_source)
    assert all(r["status"] == "READY" for r in inspect_batch(pre_apply_root, batch, decisions)["claims"])


def test_real_approval_is_audited_even_when_publication_gate_refuses(pre_apply_root, inputs, tmp_path, monkeypatch):
    from timonelo.evidence.editor import EditorError, StatementEditor

    def refuse(*args, **kwargs):
        raise EditorError("negative control: publication refused")

    monkeypatch.setattr(StatementEditor, "publish", refuse)
    result = process_private_batch(pre_apply_root, *inputs, tmp_path / "refused")
    assert result["counts"]["blocked"] == 8 and result["counts"]["admitted"] == 0
    assert result["human_approvals_recorded"] == 8
    assert all(r["review_entry"]["to_state"] == "APPROVED" for r in result["claims"])
    assert all(r["statement_record"]["publish_status"] == "PUBLISH_BLOCKED" for r in result["claims"])


def test_post_apply_repeat_refuses_duplicates_without_revoking_existing_answers(pre_apply_root, inputs, tmp_path, monkeypatch):
    from timonelo.factory import evidence_batch

    post = tmp_path / "post-apply"
    shutil.copytree(pre_apply_root, post)
    projector = evidence_batch.project_fleet

    def capture_real_post_state(workspace, catalog, today):
        # Observe real API-created records; never replace an authority result.
        shutil.copytree(workspace.root, post / "evidence", dirs_exist_ok=True)
        return projector(workspace, catalog, today)

    with monkeypatch.context() as observation:
        observation.setattr(evidence_batch, "project_fleet", capture_real_post_state)
        initial = process_private_batch(pre_apply_root, *inputs, tmp_path / "initial")
    assert initial["counts"] == {"admitted": 8, "blocked": 0, "pending": 0, "rejected": 0}
    # Keep old persisted records intact, just as the minimal canonical overlay
    # does; incidental legacy serializer normalization is not part of this test.
    old = json.loads((pre_apply_root / "evidence/statements/statements.json").read_text(encoding="utf8"))
    new = {row["statement_id"]: row["statement_record"] for row in initial["claims"]}
    canonical_dump({**old, **new}, str(post / "evidence/statements/statements.json"))
    before = {p.relative_to(post).as_posix(): p.read_bytes() for p in post.rglob("*") if p.is_file()}
    repeated = process_private_batch(post, *inputs, tmp_path / "repeated")
    assert repeated["counts"] == {"admitted": 0, "blocked": 8, "pending": 0, "rejected": 0}
    assert all(r["reasons"] == ["DUPLICATE_EXISTING_SOURCE_CLAIM"] for r in repeated["claims"])
    assert repeated["human_approvals_recorded"] == 0
    assert repeated["original_statement_count"] == 418
    assert repeated["original_states_and_authority_unchanged"]
    assert repeated["source_unchanged"] and repeated["art2_unchanged"]
    assert before == {p.relative_to(post).as_posix(): p.read_bytes() for p in post.rglob("*") if p.is_file()}
    snapshot = json.loads((tmp_path / "repeated/private.snapshot.json").read_text(encoding="utf8"))
    facts = json.loads(snapshot["payload"])["ships"]["msc-bellissima"]["facts"]
    assert {f["statement_id"] for f in facts} == set(new)
    assert all(f["artifact_id"] == "ART-0001" for f in facts)
