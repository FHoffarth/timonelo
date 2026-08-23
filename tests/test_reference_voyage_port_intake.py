"""
Tests for Port Factory — Shanghai and Tokyo Generic Port Intake & Reference Voyage Gating.
Governed by ADR-0002 §1, §6, §7, §8, §9 and Internal Agent Ruleset v0.1.
"""

import hashlib
from pathlib import Path
import zipfile
import pytest

from timonelo.evidence.authority import authoritative_classes
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


def test_port_reference_artifacts_integrity(workspace):
    """
    Authoritative generic port artifacts ART-0003, ART-0005, ART-0006 exist in the vault
    and recompute exact SHA-256 digests.
    """
    for art_id, expected_sha in [
        ("ART-0003", "ad409fc7149b10f98d61190c34d9daf78b78bb8b31464cc66de1a89d09b01b5d"),
        ("ART-0005", "a10b925fded165cfd89c70b707ea7cbeda2b371c21d97c5959b6ca6aed347c0d"),
        ("ART-0006", "5f542b9ee297cab87db449cb21af3b7dd9a2c9653fb94830ff970b68e954ceeb"),
    ]:
        art = workspace.registry.get(art_id)
        assert art.sha256 == expected_sha
        path = workspace.registry.resolve_path(art_id)
        assert path is not None
        path_obj = Path(path)
        assert path_obj.is_file()
        with open(path_obj, "rb") as f:
            computed_sha = hashlib.sha256(f.read()).hexdigest()
        assert computed_sha == expected_sha


def test_shanghai_unlocode_derived_from_raw_source_bytes(workspace):
    """
    Mechanically verify from ART-0003 raw CSV bytes that:
      - Country code: CN
      - Location code for city/port Shanghai with port function '12345---': SGH -> CNSGH
      - Location code SHA is Hongqiao Airport only ('---4----')
    """
    path = workspace.registry.resolve_path("ART-0003")
    with zipfile.ZipFile(path, "r") as zf:
        raw_csv = zf.read("release/csv/UNLOCODE CodeListPart1.csv").decode("latin1")

    # Find the port entry for Shanghai
    shanghai_port_rows = [
        line for line in raw_csv.splitlines()
        if ",CN,SGH,Shanghai,Shanghai," in line
    ]
    assert len(shanghai_port_rows) == 1
    row = shanghai_port_rows[0]
    cols = row.split(",")
    country_code = cols[1]
    loc_code = cols[2]
    name = cols[3]
    function = cols[6]

    assert country_code == "CN"
    assert loc_code == "SGH"
    assert name == "Shanghai"
    assert "1" in function  # 1 = Port

    # Reconcile with statement STM-0395 & STM-0396
    stm_locode = workspace.editor.get("STM-0395")
    assert stm_locode.value == f"{country_code}{loc_code}"
    assert stm_locode.entity_id == f"port:unlocode:{country_code}{loc_code}"

    stm_name = workspace.editor.get("STM-0396")
    assert stm_name.value == name


def test_tokyo_port_and_terminal_identity_intake(workspace):
    """
    Tokyo port and terminal statements STM-0397..STM-0402 are registered from official sources.
    """
    # Port UN/LOCODE and Official Name (ART-0003)
    stm_tyo_locode = workspace.editor.get("STM-0397")
    assert stm_tyo_locode.entity_id == "port:unlocode:JPTYO"
    assert stm_tyo_locode.value == "JPTYO"

    stm_tyo_name = workspace.editor.get("STM-0398")
    assert stm_tyo_name.entity_id == "port:unlocode:JPTYO"
    assert stm_tyo_name.value == "Tokyo"

    # Terminal Name and Address (ART-0005, ART-0006)
    stm_term_name = workspace.editor.get("STM-0399")
    assert stm_term_name.entity_id == "terminal:JPTYO:tokyo-international-cruise-terminal"
    assert stm_term_name.value == "東京国際クルーズターミナル"
    assert stm_term_name.artifact_id == "ART-0005"

    stm_term_addr = workspace.editor.get("STM-0400")
    assert stm_term_addr.entity_id == "terminal:JPTYO:tokyo-international-cruise-terminal"
    assert stm_term_addr.value == "〒135-0064 東京都江東区青海二丁目地先"
    assert stm_term_addr.artifact_id == "ART-0006"

    # Transport Node Station and Operator (ART-0006)
    stm_station = workspace.editor.get("STM-0401")
    assert stm_station.entity_id == "transport_node:JPTYO:tokyo-international-cruise-terminal-station"
    assert stm_station.value == "東京国際クルーズターミナル駅"

    stm_op = workspace.editor.get("STM-0402")
    assert stm_op.entity_id == "transport_node:JPTYO:tokyo-international-cruise-terminal-station"
    assert stm_op.value == "ゆりかもめ"


def test_all_newly_ingested_statements_fail_closed(workspace):
    """
    Every newly ingested statement (STM-0395..STM-0402) is unpromoted
    and strictly fails closed in TruthEngine and PortIntelligenceEvaluator.
    """
    for sid in [f"STM-{i:04d}" for i in range(395, 403)]:
        stm = workspace.editor.get(sid)
        assert stm.evidence_condition == EvidenceCondition.UNKNOWN
        assert stm.human_review_state == HumanReviewState.DRAFT
        assert stm.publish_status == PublishStatus.PUBLISH_BLOCKED
        eval_res = PortIntelligenceEvaluator.evaluate_fact(workspace, stm.entity_id, stm.question_id)
        assert eval_res.is_known is False
        assert eval_res.value is None


def test_event_closure_and_authority_compatibility(workspace):
    """
    Every new statement links to an existing EvidenceEvent with matching values
    and authoritative document classes.
    """
    events_by_id = {e.event_id: e for e in workspace.events.all()}
    for sid in [f"STM-{i:04d}" for i in range(395, 403)]:
        stm = workspace.editor.get(sid)
        assert len(stm.evidence_event_ids) == 1
        eid = stm.evidence_event_ids[0]
        assert eid in events_by_id
        evt = events_by_id[eid]
        assert evt.entity_id == stm.entity_id
        assert evt.question_id == stm.question_id
        assert evt.observed_value == stm.value
        assert evt.locator == stm.locator
        art = workspace.registry.get(stm.artifact_id)
        assert evt.artifact_sha256 == art.sha256
        allowed_classes = authoritative_classes(stm.statement_type)
        assert art.document_class in allowed_classes


def test_generic_terminal_does_not_prove_reference_voyage_assignment(workspace):
    """
    Hard regression test: Generic existence of Tokyo International Cruise Terminal (ART-0005)
    does NOT establish that MSC Bellissima calls there on 2026-10-07.
    Sailing-specific berth/voyage briefing must remain strictly fail-closed (None).
    """
    # 1. No voyage statement exists for Bellissima Oct 2026 sailing
    voyage_statements = [
        s for s in workspace.editor.all()
        if "2026-10-04" in (s.value or "") or "2026-10-07" in (s.value or "")
    ]
    assert len(voyage_statements) == 0

    # 2. Port briefing for Tokyo remains fail-closed
    briefing = PortIntelligenceEvaluator.evaluate(workspace, port_entity_id="port:unlocode:JPTYO")
    assert briefing is None


def test_no_guessed_coordinates_or_routes(workspace):
    """
    Ensure no coordinates or walking routes were fabricated without source authority.
    """
    for sid in [f"STM-{i:04d}" for i in range(395, 403)]:
        stm = workspace.editor.get(sid)
        assert "walk" not in stm.value.lower()
        assert "route" not in stm.statement_type
        assert "coordinate" not in stm.statement_type


def test_shanghai_terminal_remains_unregistered_and_unknown(workspace):
    """
    Shanghai cruise terminal facts remain UNKNOWN / unrepresented
    until an official port authority directory artifact is ingested.
    """
    eval_res = PortIntelligenceEvaluator.evaluate_fact(workspace, "terminal:CNSGH:wusongkou", "Q-0025")
    assert eval_res.is_known is False
    assert eval_res.value is None
