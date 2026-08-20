"""Evidence-only guards for the Bellissima primary-source intake."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest
from pypdf import PdfReader

from timonelo.evidence.editor import EditorError
from timonelo.evidence.workspace import Workspace
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO_ROOT / "evidence" / "artifacts"
AUDIT_PATH = (
    REPO_ROOT / "evidence" / "audits" / "bellissima-primary-source-intake.json"
)
DIGEST = "085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0"
MERAVIGLIA_DIGEST = (
    "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9"
)
VAULT_PATH = (
    REPO_ROOT
    / "evidence"
    / "raw"
    / "sha256"
    / DIGEST[:2]
    / f"{DIGEST}.pdf"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _workspace() -> Workspace:
    return Workspace(str(REPO_ROOT / "evidence"))


def _art_0001_statements(workspace: Workspace):
    return workspace.statements_for_artifact("ART-0001")


def test_art_0001_registry_path_resolves_to_exact_physical_bytes():
    index = json.loads((ARTIFACTS / "index.json").read_text(encoding="utf-8"))
    artifact = index["ART-0001"]

    assert artifact["sha256"] == DIGEST
    assert artifact["byte_size"] == 1_970_414
    assert VAULT_PATH.is_file()
    assert VAULT_PATH.stat().st_size == artifact["byte_size"]
    assert _sha256(VAULT_PATH) == artifact["sha256"]


def test_art_0001_physical_document_proves_bellissima_identity():
    reader = PdfReader(VAULT_PATH)
    first_page = " ".join((reader.pages[0].extract_text() or "").split())
    last_page = " ".join((reader.pages[-1].extract_text() or "").split())

    assert len(reader.pages) == 6
    assert "MSC BELLISSIMA" in first_page
    assert "DECKPL" in first_page
    assert "11.2025" in last_page
    assert "DEU" in last_page
    assert "MSCCRUISES.DE" in last_page


def test_art_0001_is_not_the_meraviglia_artifact():
    meraviglia = (
        REPO_ROOT
        / "evidence"
        / "raw"
        / "sha256"
        / "77"
        / f"{MERAVIGLIA_DIGEST}.pdf"
    )

    assert meraviglia.is_file()
    assert _sha256(meraviglia) == MERAVIGLIA_DIGEST
    assert _sha256(VAULT_PATH) != MERAVIGLIA_DIGEST


def test_intake_reconciles_identity_without_promoting_dependent_claims():
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))

    assert audit["reconciliation"]["classification"] == "EXACT_MATCH"
    assert audit["reconciliation"]["historical_registry_record_modified"] is False
    assert audit["dependent_claims"]["statement_count"] == 113
    assert audit["dependent_claims"]["classification"] == "SOURCE_IDENTITY_REPAIRED"
    assert audit["dependent_claims"]["semantic_revalidation"] == "REQUIRES_REEXTRACTION"
    assert audit["dependent_claims"]["trust_promotion_performed"] is False


def test_existing_synthetic_geometry_is_not_retroactively_canonicalized():
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    geometry = audit["geometry"]

    assert geometry["classification"] == "SYNTHETIC_GEOMETRY"
    assert geometry["canonical_truth_eligible"] is False
    assert geometry["source_relabel_performed"] is False
    assert len(geometry["files"]) == 15
    for relative_path in geometry["files"]:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert DIGEST not in content


def test_intake_does_not_authorize_field_or_cross_deck_claims():
    scope = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))["scope"]

    assert scope == {
        "cross_deck_claims_created": False,
        "field_queries_created": False,
        "geometry_created_or_modified": False,
    }


def test_art_0001_inventory_and_historical_states_remain_auditable():
    raw = json.loads(
        (REPO_ROOT / "evidence" / "statements" / "statements.json").read_text(
            encoding="utf-8"
        )
    )
    affected = [record for record in raw.values() if record["artifact_id"] == "ART-0001"]

    assert len(affected) == 113
    assert Counter(record["review_state"] for record in affected) == {
        "PUBLISHED": 112,
        "SUPERSEDED": 1,
    }


def test_all_active_art_0001_claims_are_gated_pending_reextraction():
    statements = _art_0001_statements(_workspace())
    active = [s for s in statements if s.state is not HumanReviewState.SUPERSEDED]

    assert len(active) == 112
    assert all(s.state is HumanReviewState.APPROVED for s in active)
    assert all(s.publishing is PublishStatus.PUBLISH_ALLOWED for s in active)
    assert all(s.condition is EvidenceCondition.UNKNOWN for s in active)


def test_gated_art_0001_claims_cannot_answer_through_truth_engine():
    workspace = _workspace()

    for statement in _art_0001_statements(workspace):
        answer = workspace.engine.answer(statement.entity_id, statement.question_id)
        assert answer.known is False, statement.statement_id
        assert answer.value is None, statement.statement_id


def test_gated_art_0001_claim_cannot_pass_publication_defense():
    workspace = _workspace()

    with pytest.raises(EditorError, match="Evidence condition must be SUPPORTED"):
        workspace.publish_statement(
            "STM-0001",
            actor="quarantine.behavior.test",
            occurred_on="2026-08-20",
        )


def test_source_integrity_restoration_does_not_promote_any_trust_axis():
    workspace = _workspace()
    statements = _art_0001_statements(workspace)
    before = {
        s.statement_id: (s.condition, s.state, s.publishing) for s in statements
    }

    assert VAULT_PATH.is_file()
    assert _sha256(VAULT_PATH) == workspace.registry.get("ART-0001").sha256

    after = {
        s.statement_id: (s.condition, s.state, s.publishing)
        for s in _art_0001_statements(workspace)
    }
    assert after == before
    assert {axes[0] for axes in after.values()} == {EvidenceCondition.UNKNOWN}


def test_superseded_art_0001_statement_stays_superseded_and_blocked():
    statements = _art_0001_statements(_workspace())
    superseded = [s for s in statements if s.state is HumanReviewState.SUPERSEDED]

    assert [s.statement_id for s in superseded] == ["STM-0009"]
    assert superseded[0].condition is EvidenceCondition.UNKNOWN
    assert superseded[0].publishing is PublishStatus.PUBLISH_BLOCKED


def test_review_reference_mismatch_is_the_superseded_duplicate_read():
    workspace = _workspace()
    affected_ids = {s.statement_id for s in _art_0001_statements(workspace)}
    artifact_review_ids = {
        entry.statement_id
        for entry in workspace.reviews.all()
        if "ART-0001" in entry.note
    }

    assert len(affected_ids) == 113
    assert len(artifact_review_ids) == 112
    assert affected_ids - artifact_review_ids == {"STM-0009"}
    history = workspace.reviews.history("STM-0009")
    assert len(history) == 1
    assert history[0].to_state == "SUPERSEDED"
    assert "STM-0005 (CFL-0001)" in history[0].note


def test_intake_records_the_enforced_quarantine_and_utf8_title():
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    quarantine = audit["reextraction_quarantine"]

    assert audit["artifact"]["visible_title"] == "MSC BELLISSIMA DECKPLÄNE"
    assert quarantine["mechanism"] == "CANONICAL_EVIDENCE_CONDITION_GATE"
    assert quarantine["effective_evidence_condition"] == "UNKNOWN"
    assert quarantine["truth_engine_required_condition"] == "SUPPORTED"
    assert quarantine["active_statement_count"] == 112
    assert quarantine["superseded_statement_count"] == 1
    assert quarantine["publication_eligible_statement_count"] == 0
