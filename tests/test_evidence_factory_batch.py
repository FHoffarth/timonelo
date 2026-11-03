"""Private real-source batch: reuse genuine recorded owner decisions, never infer them."""
from copy import deepcopy
import json
from pathlib import Path
import os

import pytest

from timonelo.factory.evidence_batch import BatchError, inspect_batch, process_private_batch

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "reports/evidence-factory-automation"


@pytest.fixture
def inputs():
    return (json.loads((PACKET / "pilot-batch.json").read_text(encoding="utf8")),
            json.loads((PACKET / "pilot-approvals.json").read_text(encoding="utf8")))


def test_real_approved_eight_use_existing_gates_and_leave_source_unchanged(inputs, tmp_path):
    batch, decisions = inputs
    result = process_private_batch(ROOT, batch, decisions, tmp_path / "private")
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
def test_approval_cannot_be_reused_after_binding_change(inputs, field, value):
    batch, decisions = inputs
    batch["claims"][0][field] = value
    row = inspect_batch(ROOT, batch, decisions)["claims"][0]
    assert row["status"] == "BLOCKED"
    assert "APPROVAL_BINDING_MISMATCH" in row["reasons"]


def test_missing_deferred_and_rejected_decisions_never_create_approved_records(inputs, tmp_path):
    batch, decisions = inputs
    decisions["decisions"][0]["decision"] = "DEFER"
    decisions["decisions"][1]["decision"] = "REJECT"
    decisions["decisions"] = decisions["decisions"][:2]
    result = process_private_batch(ROOT, batch, decisions, tmp_path / "pending")
    assert result["counts"] == {"admitted": 0, "blocked": 0, "pending": 7, "rejected": 1}
    assert result["human_approvals_recorded"] == 0
    assert not json.loads(json.loads((tmp_path / "pending/private.snapshot.json").read_text())["payload"])["ships"]["msc-bellissima"]["facts"]


def test_duplicate_selection_and_unconfigured_drive_route_refuse(inputs):
    batch, decisions = inputs
    batch["claims"] = [batch["claims"][0], deepcopy(batch["claims"][0])]
    with pytest.raises(BatchError, match="DUPLICATE_CLAIM_ID"):
        inspect_batch(ROOT, batch, decisions)
    batch["claims"] = batch["claims"][:1]
    batch["source_route"] = "GOOGLE_DRIVE"
    with pytest.raises(BatchError, match="UNCONFIGURED_SOURCE_ROUTE"):
        inspect_batch(ROOT, batch, decisions)


def test_claim_contradiction_is_an_unresolved_exception(inputs):
    batch, decisions = inputs
    claim = batch["claims"][1]
    claim["value"] = [5]
    decisions["decisions"][1]["binding"] = deepcopy(claim)  # Synthetic negative control, not owner data.
    row = inspect_batch(ROOT, batch, decisions)["claims"][1]
    assert row["status"] == "BLOCKED" and "CONTRADICTORY_EXISTING_CLAIM" in row["reasons"]


def test_source_revision_is_checked_even_when_input_decision_is_forged(inputs):
    batch, decisions = inputs
    claim = batch["claims"][0]
    claim["artifact_sha256"] = "0" * 64
    decisions["decisions"][0]["binding"] = deepcopy(claim)
    row = inspect_batch(ROOT, batch, decisions)["claims"][0]
    assert row["status"] == "BLOCKED" and "ARTIFACT_SHA_MISMATCH" in row["reasons"]


def test_output_inside_source_or_existing_directory_is_not_allowed(inputs, tmp_path):
    batch, decisions = inputs
    with pytest.raises(BatchError, match="OUTPUT_INSIDE_SOURCE"):
        process_private_batch(ROOT, batch, decisions, ROOT / "frontend/public/new-snapshot")
    with pytest.raises(BatchError, match="OUTPUT_EXISTS"):
        process_private_batch(ROOT, batch, decisions, tmp_path)


def test_missing_human_metadata_does_not_manufacture_a_reviewer(inputs):
    batch, decisions = inputs
    decisions["reviewer"] = ""
    plan = inspect_batch(ROOT, batch, decisions)
    assert all(r["status"] == "BLOCKED" for r in plan["claims"])
    assert all("MISSING_HUMAN_REVIEW_METADATA" in r["reasons"] for r in plan["claims"])


def test_inspection_never_calls_a_writer_on_the_source_checkout(inputs, monkeypatch):
    batch, decisions = inputs
    original = os.makedirs

    def outside_source(path, *args, **kwargs):
        assert not Path(path).resolve().is_relative_to(ROOT), "source directory creation attempted"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(os, "makedirs", outside_source)
    assert all(r["status"] == "READY" for r in inspect_batch(ROOT, batch, decisions)["claims"])


def test_real_approval_is_audited_even_when_publication_gate_refuses(inputs, tmp_path, monkeypatch):
    from timonelo.evidence.editor import EditorError, StatementEditor

    def refuse(*args, **kwargs):
        raise EditorError("negative control: publication refused")

    monkeypatch.setattr(StatementEditor, "publish", refuse)
    result = process_private_batch(ROOT, *inputs, tmp_path / "refused")
    assert result["counts"]["blocked"] == 8 and result["counts"]["admitted"] == 0
    assert result["human_approvals_recorded"] == 8
    assert all(r["review_entry"]["to_state"] == "APPROVED" for r in result["claims"])
    assert all(r["statement_record"]["publish_status"] == "PUBLISH_BLOCKED" for r in result["claims"])
