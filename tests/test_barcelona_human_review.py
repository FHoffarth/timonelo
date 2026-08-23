"""
Tests for Timonelo Port Factory — Barcelona Human Review Promotion.
Governed by ADR-0002 §1, §4, §5, §6, §7, §8, §9.
"""

import hashlib
from pathlib import Path
import pytest

from timonelo.evidence.workspace import Workspace
from timonelo.intelligence.ports import PortIntelligenceEvaluator
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "evidence"


@pytest.fixture
def workspace():
    return Workspace(str(EVIDENCE_DIR))


def test_barcelona_approved_statements_resolve_through_evaluator(workspace):
    """
    Approved Barcelona statements STM-0391..STM-0394 resolve cleanly
    through PortIntelligenceEvaluator.evaluate_fact() with complete provenance.
    """
    # 1. UN/LOCODE: ESBCN (Q-0023)
    unlocode_eval = PortIntelligenceEvaluator.evaluate_fact(
        workspace, "port:unlocode:ESBCN", "Q-0023"
    )
    assert unlocode_eval.is_known is True
    assert unlocode_eval.value == "ESBCN"
    assert unlocode_eval.provenance is not None
    assert unlocode_eval.provenance.statement_id == "STM-0391"
    assert unlocode_eval.provenance.artifact_id == "ART-0003"
    assert unlocode_eval.provenance.evidence_condition == EvidenceCondition.SUPPORTED
    assert unlocode_eval.provenance.human_review_state == HumanReviewState.APPROVED
    assert unlocode_eval.provenance.publish_status == PublishStatus.PUBLISH_ALLOWED
    assert unlocode_eval.provenance.artifact_sha256 == "ad409fc7149b10f98d61190c34d9daf78b78bb8b31464cc66de1a89d09b01b5d"

    # 2. Official Name: Port de Barcelona (Q-0024)
    name_eval = PortIntelligenceEvaluator.evaluate_fact(
        workspace, "port:unlocode:ESBCN", "Q-0024"
    )
    assert name_eval.is_known is True
    assert name_eval.value == "Port de Barcelona"
    assert name_eval.provenance is not None
    assert name_eval.provenance.statement_id == "STM-0392"
    assert name_eval.provenance.artifact_id == "ART-0004"
    assert name_eval.provenance.evidence_condition == EvidenceCondition.SUPPORTED
    assert name_eval.provenance.human_review_state == HumanReviewState.APPROVED
    assert name_eval.provenance.publish_status == PublishStatus.PUBLISH_ALLOWED
    assert name_eval.provenance.artifact_sha256 == "f0f04f664d3644a82d18a06eeab4674d716316866954ec04b868d34c21188bdf"

    # 3. Terminal A (Q-0025)
    term_a_eval = PortIntelligenceEvaluator.evaluate_fact(
        workspace, "terminal:ESBCN:adosat-a", "Q-0025"
    )
    assert term_a_eval.is_known is True
    assert term_a_eval.value == "Terminal A"
    assert term_a_eval.provenance is not None
    assert term_a_eval.provenance.statement_id == "STM-0393"
    assert term_a_eval.provenance.artifact_id == "ART-0004"
    assert term_a_eval.provenance.evidence_condition == EvidenceCondition.SUPPORTED
    assert term_a_eval.provenance.human_review_state == HumanReviewState.APPROVED
    assert term_a_eval.provenance.publish_status == PublishStatus.PUBLISH_ALLOWED

    # 4. Terminal E – Helix (Q-0025)
    term_e_eval = PortIntelligenceEvaluator.evaluate_fact(
        workspace, "terminal:ESBCN:adosat-e", "Q-0025"
    )
    assert term_e_eval.is_known is True
    assert term_e_eval.value == "Terminal E – Helix"
    assert term_e_eval.provenance is not None
    assert term_e_eval.provenance.statement_id == "STM-0394"
    assert term_e_eval.provenance.artifact_id == "ART-0004"
    assert term_e_eval.provenance.evidence_condition == EvidenceCondition.SUPPORTED
    assert term_e_eval.provenance.human_review_state == HumanReviewState.APPROVED
    assert term_e_eval.provenance.publish_status == PublishStatus.PUBLISH_ALLOWED


def test_evaluator_remains_fail_closed_for_aggregate_port_intelligence(workspace):
    """
    Even with port name and terminals approved, aggregate PortIntelligence briefing
    must fail closed (return None) because gangway, town distance, and routes are not yet evidenced.
    """
    briefing = PortIntelligenceEvaluator.evaluate(
        workspace=workspace, port_entity_id="port:unlocode:ESBCN"
    )
    assert briefing is None


def test_unrelated_statements_preserved_unchanged(workspace):
    """
    Statements STM-0001..STM-0390 remain exactly in their original lifecycle state.
    """
    stm_0001 = workspace.editor.get("STM-0001")
    assert stm_0001.entity_id == "cabin:MSC-BELLISSIMA:14122"
    assert stm_0001.value == "true"

    stm_0390 = workspace.editor.get("STM-0390")
    assert stm_0390.statement_id == "STM-0390"
    assert stm_0390.publish_status == PublishStatus.PUBLISH_BLOCKED


def test_source_artifacts_and_events_remain_immutable(workspace):
    """
    Source artifacts ART-0003 and ART-0004 physical bytes and hashes remain completely unchanged.
    """
    art3 = workspace.registry.get("ART-0003")
    path3 = workspace.registry.resolve_path("ART-0003")
    assert art3.sha256 == "ad409fc7149b10f98d61190c34d9daf78b78bb8b31464cc66de1a89d09b01b5d"
    with open(path3, "rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == art3.sha256

    art4 = workspace.registry.get("ART-0004")
    path4 = workspace.registry.resolve_path("ART-0004")
    assert art4.sha256 == "f0f04f664d3644a82d18a06eeab4674d716316866954ec04b868d34c21188bdf"
    with open(path4, "rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == art4.sha256

    # Events EVT-PORT-0001..EVT-PORT-0004 exist
    events = {e.event_id: e for e in workspace.events.all()}
    for eid in ("EVT-PORT-0001", "EVT-PORT-0002", "EVT-PORT-0003", "EVT-PORT-0004"):
        assert eid in events


def test_audit_trail_distinguishes_agent_verifier_and_human_approver(workspace):
    """
    ReviewLog must clearly record the distinct roles:
      1. port-intake-verifier for condition and submission
      2. human-reviewer for explicit project owner approval
    """
    import json
    with open(REPO_ROOT / "evidence" / "reviews" / "log.json", encoding="utf-8") as f:
        log_entries = json.load(f)

    for sid in ("STM-0391", "STM-0392", "STM-0393", "STM-0394"):
        entries = [e for e in log_entries if e["statement_id"] == sid]
        assert len(entries) >= 3, f"Expected full audit lifecycle for {sid}"

        # 1. Condition verification by verifier
        cond_entry = [e for e in entries if e["to_state"] == "CONDITION:SUPPORTED"][0]
        assert cond_entry["actor"] == "port-intake-verifier"

        # 2. Submission to review
        draft_entry = [e for e in entries if e["to_state"] == "UNDER_REVIEW"][0]
        assert draft_entry["actor"] == "port-intake-verifier"

        # 3. Explicit human approval by human-reviewer
        appr_entry = [e for e in entries if e["to_state"] == "APPROVED"][0]
        assert appr_entry["actor"] == "human-reviewer"
        assert "Explicit human approval" in appr_entry["note"]

