"""
Tests for Timonelo Port Factory — Slice 3:
Truth-backed PortIntelligenceEvaluator traversal.

Governed by ADR-0002 §1, §4, §6, §7, §8, §9, §13.
"""

from dataclasses import replace
import hashlib
import json
import os
import shutil
from pathlib import Path
import pytest

from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.events import EvidenceEvent, EvidenceEventLog
from timonelo.evidence.port_intake import (
    PortClaimDraft,
    PortSourceDescriptor,
    ingest_port_source,
)
from timonelo.evidence.questions import QuestionRegistry
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.review import ReviewLog
from timonelo.evidence.truth import TruthEngine
from timonelo.evidence.workspace import Workspace
from timonelo.intelligence.ports import (
    PortFactEvaluation,
    PortFactProvenance,
    PortIntelligenceEvaluator,
)
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
# 1. UNPROMOTED / UNKNOWN PORT STATEMENTS FAIL CLOSED BY DEFAULT
# =============================================================================

def test_unpromoted_port_statements_fail_closed_by_default(workspace):
    """
    Unpromoted port statements must fail closed and return is_known=False.
    """
    # 1. Non-existent / unpromoted port UN/LOCODE (Q-0023)
    unlocode_eval = PortIntelligenceEvaluator.evaluate_fact(workspace, "port:unlocode:DEHAM", "Q-0023")
    assert unlocode_eval.is_known is False
    assert unlocode_eval.value is None
    assert unlocode_eval.refusal_reason is not None

    # 2. Non-existent / unpromoted port official name (Q-0024)
    name_eval = PortIntelligenceEvaluator.evaluate_fact(workspace, "port:unlocode:DEHAM", "Q-0024")
    assert name_eval.is_known is False
    assert name_eval.value is None

    # 3. Full PortIntelligence briefing returns None because required facts are not yet publishable
    briefing = PortIntelligenceEvaluator.evaluate(workspace=workspace, port_entity_id="port:unlocode:DEHAM")
    assert briefing is None


# =============================================================================
# 2. CANONICAL PUBLICATION GATEWAY TESTS (ISOLATED WORKSPACE)
# =============================================================================

@pytest.fixture
def test_workspace(tmp_path):
    """Creates a hermetic test workspace with valid schemas and mock sources."""
    reg_dir = tmp_path / "artifacts"
    rev_file = tmp_path / "reviews.json"
    conf_file = tmp_path / "conflicts.json"
    stmt_file = tmp_path / "statements.json"
    q_file = tmp_path / "questions.json"
    evt_file = tmp_path / "events.json"

    shutil.copy2(str(EVIDENCE_DIR / "registry" / "questions.json"), str(q_file))

    # Create dummy port directory source
    src_file = tmp_path / "Test_Port_Authority_Directory.html"
    src_file.write_text("<meta property='og:site_name' content='Port of Marseille' />", encoding="utf-8")

    class HermeticWorkspace:
        def __init__(self):
            self.root = str(tmp_path)
            self.registry = ArtifactRegistry(str(reg_dir))
            self.reviews = ReviewLog(str(rev_file))
            self.conflicts = ConflictLog(str(conf_file))
            self.editor = StatementEditor(str(stmt_file), self.registry, self.reviews, self.conflicts)
            self.questions = QuestionRegistry.load(str(q_file))
            self.events = EvidenceEventLog(str(evt_file), self.registry, self.questions)
            self.engine = TruthEngine(self.questions, self.editor, self.registry, self.conflicts)

    ws = HermeticWorkspace()

    desc = PortSourceDescriptor(
        path=str(src_file),
        document_class="port_authority_official_directory",
        acquired_on="2026-08-23",
        acquisition_method="official publication download",
        publisher="Marseille Port Authority",
        version="2026",
    )
    claims = [
        PortClaimDraft(
            entity_id="port:unlocode:FRMRS",
            question_id="Q-0024",
            statement_type="port.official_name",
            value="Port of Marseille",
            locator="HTML meta: og:site_name",
            read_by="test-curator",
            read_on="2026-08-23",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
        )
    ]
    art, evts, stmts = ingest_port_source(ws, desc, claims)
    return ws, art, evts[0], stmts[0]


def test_evaluator_resolves_when_approved_and_supported_and_published(test_workspace):
    """When a statement passes all canonical gates via TruthEngine & Gatekeeper, it resolves with rich provenance."""
    ws, art, evt, stmt = test_workspace

    # Initially fails closed (DRAFT / UNKNOWN / PUBLISH_BLOCKED)
    res_draft = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res_draft.is_known is False

    # Transition to SUPPORTED + APPROVED + PUBLISH_ALLOWED
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res_allowed = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res_allowed.is_known is True
    assert res_allowed.value == "Port of Marseille"
    assert res_allowed.provenance is not None
    assert res_allowed.provenance.artifact_id == art.artifact_id
    assert res_allowed.provenance.document_class == "port_authority_official_directory"
    assert res_allowed.provenance.locator == "HTML meta: og:site_name"
    assert res_allowed.provenance.statement_id == stmt.statement_id
    assert res_allowed.provenance.evidence_event_id == evt.event_id
    assert res_allowed.provenance.artifact_sha256 == art.sha256

    link = res_allowed.to_evidence_link()
    assert link is not None
    assert link.source_id == art.artifact_id
    assert link.sha256 == art.sha256


def test_evaluator_rejects_draft_state(test_workspace):
    """SUPPORTED + PUBLISH_ALLOWED but DRAFT human review must fail closed via TruthEngine."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert res.refusal_reason == "TRUTH_NOT_ADMISSIBLE"


def test_evaluator_rejects_unknown_condition(test_workspace):
    """APPROVED + PUBLISH_ALLOWED but UNKNOWN condition must fail closed via TruthEngine."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert res.refusal_reason == "TRUTH_NOT_ADMISSIBLE"


def test_evaluator_rejects_blocked_publish_status(test_workspace):
    """SUPPORTED + APPROVED but PUBLISH_BLOCKED must fail closed via TruthEngine."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert res.refusal_reason == "TRUTH_NOT_ADMISSIBLE"


def test_evaluator_rejects_missing_evidence_events(test_workspace):
    """Statement with empty evidence_event_ids must fail closed via EvidenceGatekeeper."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
        evidence_event_ids=(),
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert "STATEMENT_ZERO_EVIDENCE_EVENTS" in (res.refusal_reason or "")


def test_evaluator_rejects_missing_referenced_event(test_workspace):
    """Statement referencing non-existent event ID must fail closed via EvidenceGatekeeper."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
        evidence_event_ids=("EVT-NON-EXISTENT",),
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert "UNKNOWN_EVIDENCE_EVENT" in (res.refusal_reason or "")


def test_evaluator_rejects_hash_mismatch(test_workspace):
    """Tampered physical artifact file must trigger hash mismatch via EvidenceGatekeeper."""
    ws, art, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    # Tamper with the physical file
    vault_path = ws.registry.resolve_path(art.artifact_id)
    with open(vault_path, "ab") as f:
        f.write(b"TAMPERED_BYTES")

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert "SOURCE_HASH_MISMATCH" in (res.refusal_reason or "") or "PRIMARY_SOURCE_MISSING" in (res.refusal_reason or "")


def test_evaluator_rejects_authority_class_mismatch(test_workspace, tmp_path):
    """Artifact class without authority over the question statement_type must fail closed via Gatekeeper."""
    ws, art, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
        question_id="Q-0001",
        statement_type="cabin.exists",
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0001")
    assert res.is_known is False
    assert "INELIGIBLE_DOCUMENT_CLASS" in (res.refusal_reason or "")


def test_evaluator_rejects_unresolved_conflicts(test_workspace):
    """Active open conflict on (entity_id, question_id) must fail closed via TruthEngine & ConflictLog."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    # Record open conflict
    ws.conflicts.record(
        entity_id="port:unlocode:FRMRS",
        question_id="Q-0024",
        statement_type="port.official_name",
        incumbent_statement_id=stmt.statement_id,
        incumbent_value=stmt.value,
        challenger_statement_id="STM-CHALLENGER",
        challenger_value="Grand Port Maritime de Marseille",
        detected_on="2026-08-23",
    )

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert res.refusal_reason == "ACTIVE_CONFLICT_UNRESOLVED"


def test_evaluator_rejects_missing_physical_artifact(test_workspace):
    """Missing physical artifact file on disk must fail closed via Gatekeeper."""
    ws, art, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    # Delete physical vault file
    vault_path = ws.registry.resolve_path(art.artifact_id)
    if vault_path and os.path.isfile(vault_path):
        os.remove(vault_path)

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is False
    assert "PRIMARY_SOURCE_MISSING" in (res.refusal_reason or "")


def test_evaluator_rejects_expired_validity(test_workspace):
    """Statement with expired validity must fail closed via TruthEngine."""
    ws, _, _, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
        valid_until="2025-12-31",
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024", as_of="2026-08-23")
    assert res.is_known is False
    assert res.refusal_reason == "TRUTH_NOT_ADMISSIBLE"


def test_evaluator_works_for_generic_arbitrary_port_entities(test_workspace):
    """Evaluator is completely port-agnostic and resolves arbitrary port entities (e.g. Valletta / ITGOA)."""
    ws, art, evt, stmt = test_workspace
    valletta_stmt = replace(
        stmt,
        statement_id="STM-VALLETTA",
        entity_id="port:unlocode:MTMLA",
        question_id="Q-0024",
        value="Grand Harbour Valletta",
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id["STM-VALLETTA"] = valletta_stmt
    ws.editor._flush()

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:MTMLA", "Q-0024")
    assert res.is_known is True
    assert res.value == "Grand Harbour Valletta"
    assert res.provenance.statement_id == "STM-VALLETTA"


def test_evaluator_does_not_invent_unsupported_defaults(test_workspace):
    """PortIntelligenceEvaluator.evaluate() does NOT return fabricated defaults when only port.official_name is known."""
    ws, art, evt, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    # Fact is known
    fact = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert fact.is_known is True
    assert fact.value == "Port of Marseille"

    # Briefing evaluation MUST return None to avoid fabricating gangway, town distance, walking summary, etc.
    briefing = PortIntelligenceEvaluator.evaluate(workspace=ws, port_entity_id="port:unlocode:FRMRS")
    assert briefing is None


def test_architecture_no_duplicate_lifecycle_predicates_in_ports_py():
    """Static architecture guard: ports.py MUST NOT directly filter candidates on lifecycle predicates."""
    ports_py = REPO_ROOT / "src" / "timonelo" / "intelligence" / "ports.py"
    content = ports_py.read_text(encoding="utf-8")

    forbidden_predicates = [
        "s.evidence_condition ==",
        "s.evidence_condition in",
        "s.human_review_state ==",
        "s.human_review_state in",
        "s.publish_status ==",
        "s.publish_status in",
        "s.publishing in",
        "s.state in",
        "s.condition in",
        "s.is_valid_at(",
    ]
    for predicate in forbidden_predicates:
        assert predicate not in content, f"ports.py duplicates canonical truth logic via '{predicate}'"


def test_evaluator_delegates_to_truth_engine_and_gatekeeper(test_workspace, monkeypatch):
    """Architecture test: proving PortIntelligenceEvaluator delegates directly to TruthEngine & Gatekeeper."""
    ws, art, evt, stmt = test_workspace
    updated = replace(
        stmt,
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    ws.editor._by_id[stmt.statement_id] = updated
    ws.editor._flush()

    engine_called = []
    original_answer = ws.engine.answer

    def mock_answer(entity_id, question_id, as_of=None):
        engine_called.append((entity_id, question_id))
        return original_answer(entity_id, question_id, as_of=as_of)

    monkeypatch.setattr(ws.engine, "answer", mock_answer)

    res = PortIntelligenceEvaluator.evaluate_fact(ws, "port:unlocode:FRMRS", "Q-0024")
    assert len(engine_called) == 1
    assert engine_called[0] == ("port:unlocode:FRMRS", "Q-0024")
    assert res.is_known is True
    assert res.value == "Port of Marseille"
