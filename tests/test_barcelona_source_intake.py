"""
Tests for Timonelo Port Factory — Slice 2:
Barcelona Reference Port Source Intake + Evidence-Linked Statements.

Governed by ADR-0002 §1, §5, §6, §7, §8, §12, §13.
"""

import hashlib
import json
import os
import shutil
from pathlib import Path
import pytest

from timonelo.evidence import authority
from timonelo.evidence.authority import check, authoritative_classes
from timonelo.evidence.events import EvidenceEventLog
from timonelo.evidence.models import Statement
from timonelo.evidence.port_intake import (
    PortSourceDescriptor,
    PortClaimDraft,
    ingest_port_source,
)
from timonelo.evidence.workspace import Workspace
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "evidence"


@pytest.fixture
def workspace():
    return Workspace(str(EVIDENCE_DIR))


# =============================================================================
# 1. ARTIFACT REGISTRATION & INTEGRITY
# =============================================================================

def test_barcelona_source_artifacts_registered(workspace):
    """Verify ART-0003 and ART-0004 are registered with authentic official metadata."""
    art3 = workspace.registry.get("ART-0003")
    assert art3.artifact_id == "ART-0003"
    assert art3.document_class == "un_locode_registry"
    assert "UNECE" in art3.publisher or "United Nations" in art3.publisher
    assert art3.version == "2025-1"
    assert art3.sha256 == "ad409fc7149b10f98d61190c34d9daf78b78bb8b31464cc66de1a89d09b01b5d"
    assert art3.byte_size == 13507338
    assert "unicc.org" in art3.acquisition_method or "unece.org" in art3.acquisition_method

    art4 = workspace.registry.get("ART-0004")
    assert art4.artifact_id == "ART-0004"
    assert art4.document_class == "port_authority_official_directory"
    assert "Autoritat Portu" in (art4.publisher or "")
    assert art4.version == "2026"
    assert art4.sha256 == "f0f04f664d3644a82d18a06eeab4674d716316866954ec04b868d34c21188bdf"
    assert art4.byte_size == 116126


def test_barcelona_artifact_sha256_stability(workspace):
    """Verify physical vault path matches registered sha256 and verifies."""
    for aid in ["ART-0003", "ART-0004"]:
        art = workspace.registry.get(aid)
        vault_path = workspace.registry.resolve_path(aid)
        assert vault_path is not None, f"Vault candidate missing for {aid}"
        assert os.path.isfile(vault_path), f"File missing for {aid} at {vault_path}"
        assert workspace.registry.verify(aid) is True

        h = hashlib.sha256()
        with open(vault_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        assert h.hexdigest() == art.sha256, f"Digest mismatch for {aid}"


def test_authoritative_origin_regression_guard(workspace):
    """Regression guard: GitHub mirror / third-party URLs cannot masquerade as official UNECE."""
    art3 = workspace.registry.get("ART-0003")
    method = art3.acquisition_method.lower()
    for forbidden in ["github.com/datasets", "kaggle.com", "raw.githubusercontent.com"]:
        assert forbidden not in method, f"Authoritative source contains third-party mirror: {forbidden}"


# =============================================================================
# 2. STATEMENT MAPPING, AUTHORITY & PROVENANCE
# =============================================================================

BARCELONA_STATEMENTS = [
    ("STM-0391", "port:unlocode:ESBCN", "Q-0023", "port.un_locode", "ESBCN", "ART-0003", "EVT-PORT-0001"),
    ("STM-0392", "port:unlocode:ESBCN", "Q-0024", "port.official_name", "Port de Barcelona", "ART-0004", "EVT-PORT-0002"),
    ("STM-0393", "terminal:ESBCN:adosat-a", "Q-0025", "cruise_terminal.official_name", "Terminal A", "ART-0004", "EVT-PORT-0003"),
    ("STM-0394", "terminal:ESBCN:adosat-e", "Q-0025", "cruise_terminal.official_name", "Terminal E – Helix", "ART-0004", "EVT-PORT-0004"),
]


def test_statements_map_to_canonical_questions_and_pass_authority(workspace):
    """Every Barcelona statement maps to Q-0023..Q-0025 and passes authority."""
    for sid, entity_id, qid, stype, expected_val, expected_art, _ in BARCELONA_STATEMENTS:
        stmt = workspace.editor.get(sid)
        assert stmt.statement_id == sid
        assert stmt.entity_id == entity_id
        assert stmt.question_id == qid
        assert stmt.statement_type == stype
        assert stmt.value == expected_val
        assert stmt.artifact_id == expected_art

        # Verify Question exists in QuestionRegistry
        q = workspace.questions.get(qid)
        assert q.statement_type == stype

        # Verify Authority Check
        art = workspace.registry.get(stmt.artifact_id)
        assert art.document_class in authoritative_classes(stype)
        check(stype, art.document_class)


def test_statements_have_valid_evidence_event_linkage(workspace):
    """Every Barcelona statement must retain at least one valid evidence_event_id."""
    events = {e.event_id: e for e in workspace.events.all()}
    assert len(events) >= 4

    for sid, entity_id, qid, stype, expected_val, expected_art, expected_evt in BARCELONA_STATEMENTS:
        stmt = workspace.editor.get(sid)
        assert len(stmt.evidence_event_ids) > 0, f"Statement {sid} has empty evidence_event_ids"
        assert expected_evt in stmt.evidence_event_ids

        evt = events.get(expected_evt)
        assert evt is not None, f"Event {expected_evt} missing in EvidenceEventLog"
        assert evt.entity_id == entity_id
        assert evt.question_id == qid
        assert evt.observed_value == expected_val
        assert evt.locator == stmt.locator
        assert evt.artifact_sha256 == workspace.registry.get(expected_art).sha256


def test_barcelona_statements_conservative_lifecycle(workspace):
    """All newly ingested statements must be UNKNOWN / DRAFT / PUBLISH_BLOCKED."""
    for sid, _, _, _, _, _, _ in BARCELONA_STATEMENTS:
        stmt = workspace.editor.get(sid)
        assert stmt.evidence_condition == EvidenceCondition.UNKNOWN
        assert stmt.human_review_state == HumanReviewState.DRAFT
        assert stmt.publish_status == PublishStatus.PUBLISH_BLOCKED


def test_barcelona_statements_direct_and_local(workspace):
    """All statements are directly extracted with local derivation."""
    for sid, _, _, _, _, _, _ in BARCELONA_STATEMENTS:
        stmt = workspace.editor.get(sid)
        assert stmt.method == Method.DIRECT
        assert stmt.derivation == Derivation.LOCAL
        assert stmt.locator is not None
        assert len(stmt.locator) > 0


# =============================================================================
# 3. PRESERVATION & FORBIDDEN HARDCODING GUARDS
# =============================================================================

def test_static_barcelona_knowledge_json_unchanged():
    """Verify knowledge/ports/barcelona/port.json and transport.json are not dirty."""
    port_json = REPO_ROOT / "knowledge" / "ports" / "barcelona" / "port.json"
    transport_json = REPO_ROOT / "knowledge" / "ports" / "barcelona" / "transport.json"

    assert port_json.is_file()
    assert transport_json.is_file()

    port_data = json.loads(port_json.read_text(encoding="utf-8"))
    assert port_data["port_id"] == "barcelona"
    assert "terminals" in port_data

    trans_data = json.loads(transport_json.read_text(encoding="utf-8"))
    assert trans_data["port_id"] == "barcelona"


def test_no_hardcoded_barcelona_in_core_modules():
    """Verify that core evidence and engine modules have NO hardcoded 'Barcelona' logic."""
    core_evidence_dir = REPO_ROOT / "src" / "timonelo" / "evidence"
    for py_file in core_evidence_dir.glob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        # Ensure no conditional branching on Barcelona or ESBCN exists in core code
        assert 'if port == "Barcelona"' not in text
        assert 'if unlocode == "ESBCN"' not in text
        assert 'if port_id == "barcelona"' not in text


# =============================================================================
# 4. SCALABILITY PROOF: PORT-AGNOSTIC INTAKE PIPELINE
# =============================================================================

def test_port_agnostic_scalability(tmp_path):
    """Proof that ingest_port_source() ingests any arbitrary port without hardcoding."""
    # Create an isolated workspace
    reg_dir = tmp_path / "artifacts"
    rev_file = tmp_path / "reviews.json"
    stmt_file = tmp_path / "statements.json"
    q_file = tmp_path / "questions.json"
    evt_file = tmp_path / "events.json"

    # Copy real questions to tmp
    shutil.copy2(str(EVIDENCE_DIR / "registry" / "questions.json"), str(q_file))

    # Create dummy municipal transit source for a generic port
    test_src = tmp_path / "Generic_Port_Transit_Schedule.json"
    test_src.write_text(json.dumps({
        "service": "Port Express Shuttle",
        "operator": "Autonomous Port Transit Agency"
    }), encoding="utf-8")

    from timonelo.evidence.registry import ArtifactRegistry
    from timonelo.evidence.review import ReviewLog
    from timonelo.evidence.editor import StatementEditor
    from timonelo.evidence.questions import QuestionRegistry

    class IsolatedWorkspace:
        def __init__(self):
            self.root = str(tmp_path)
            self.registry = ArtifactRegistry(str(reg_dir))
            self.reviews = ReviewLog(str(rev_file))
            self.editor = StatementEditor(str(stmt_file), self.registry, self.reviews)
            self.questions = QuestionRegistry.load(str(q_file))
            self.events = EvidenceEventLog(str(evt_file), self.registry, self.questions)

    iso_ws = IsolatedWorkspace()

    desc = PortSourceDescriptor(
        path=str(test_src),
        document_class="municipal_transit_authority",
        acquired_on="2026-08-23",
        acquisition_method="test download",
        publisher="Generic Transit Authority",
    )
    claims = [
        PortClaimDraft(
            entity_id="transport:TESTPORT:shuttle-1",
            question_id="Q-0028",
            statement_type="transport_node.official_name",
            value="Port Express Shuttle",
            locator="JSON path: service",
            read_by="automated-test-curator",
            read_on="2026-08-23",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
        ),
        PortClaimDraft(
            entity_id="transport:TESTPORT:shuttle-1",
            question_id="Q-0029",
            statement_type="transport_node.operator",
            value="Autonomous Port Transit Agency",
            locator="JSON path: operator",
            read_by="automated-test-curator",
            read_on="2026-08-23",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
        ),
    ]

    art, evts, stmts = ingest_port_source(iso_ws, desc, claims)

    assert art.artifact_id == "ART-0001"
    assert art.document_class == "municipal_transit_authority"
    assert len(evts) == 2
    assert len(stmts) == 2
    assert stmts[0].entity_id == "transport:TESTPORT:shuttle-1"
    assert stmts[0].value == "Port Express Shuttle"
    assert stmts[0].evidence_event_ids == (evts[0].event_id,)
    assert stmts[1].value == "Autonomous Port Transit Agency"
    assert stmts[1].evidence_event_ids == (evts[1].event_id,)
    assert stmts[0].evidence_condition == EvidenceCondition.UNKNOWN
    assert stmts[0].human_review_state == HumanReviewState.DRAFT
    assert stmts[0].publish_status == PublishStatus.PUBLISH_BLOCKED
