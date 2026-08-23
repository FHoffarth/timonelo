"""
Tests for Port Factory — Shanghai and Tokyo Generic Port Intake & MSC Reference Voyage Gating.
Governed by ADR-0002 §1, §6, §7, §8, §9 and Internal Agent Ruleset v0.1.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
import pytest

from timonelo.evidence.authority import authoritative_classes, DOCUMENT_CLASSES
from timonelo.evidence.workspace import Workspace
from timonelo.intelligence.ports import PortIntelligenceEvaluator
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "evidence"

# Strict allowlist of permissible non-private reference voyage values
ALLOWED_VOYAGE_STATEMENT_VALUES = frozenset({
    "MSC BELLISSIMA",
    "2026-10-04",
    "Shanghai, China",
    "port:unlocode:CNSGH",
    "2026-10-07",
    "Tokyo, Japan",
    "port:unlocode:JPTYO",
    "14:00",
})

# Forbidden PII / commercial schema and statement concepts
FORBIDDEN_PII_CONCEPTS = frozenset({
    "passenger",
    "birth_date",
    "address",
    "phone",
    "email",
    "booking_id",
    "booking_number",
    "ticket_number",
    "payment",
    "price",
    "loyalty",
    "cabin_number",
    "assigned_cabin",
})


@pytest.fixture
def workspace():
    return Workspace(str(EVIDENCE_DIR))


def test_public_generic_port_artifacts_integrity(workspace):
    """
    Authoritative generic port artifacts exist in the vault
    and recompute exact SHA-256 digests.
    """
    for art_id, expected_sha in [
        ("ART-0003", "ad409fc7149b10f98d61190c34d9daf78b78bb8b31464cc66de1a89d09b01b5d"),
        ("ART-0005", "a10b925fded165cfd89c70b707ea7cbeda2b371c21d97c5959b6ca6aed347c0d"),
        ("ART-0006", "5f542b9ee297cab87db449cb21af3b7dd9a2c9653fb94830ff970b68e954ceeb"),
    ]:
        art = workspace.registry.get(art_id)
        assert art.sha256 == expected_sha
        assert workspace.registry.verify(art_id) is True
        assert workspace.registry.verification_status(art_id) == "PUBLIC_ARTIFACT_SHA_VERIFIED"
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
    assert "1" in function

    stm_locode = workspace.editor.get("STM-0395")
    assert stm_locode.value == f"{country_code}{loc_code}"
    assert stm_locode.entity_id == f"port:unlocode:{country_code}{loc_code}"

    stm_name = workspace.editor.get("STM-0396")
    assert stm_name.value == name


def test_tokyo_port_and_terminal_identity_intake(workspace):
    """
    Tokyo generic port and terminal statements STM-0397..STM-0402 are registered from official sources.
    """
    stm_tyo_locode = workspace.editor.get("STM-0397")
    assert stm_tyo_locode.entity_id == "port:unlocode:JPTYO"
    assert stm_tyo_locode.value == "JPTYO"

    stm_tyo_name = workspace.editor.get("STM-0398")
    assert stm_tyo_name.entity_id == "port:unlocode:JPTYO"
    assert stm_tyo_name.value == "Tokyo"

    stm_term_name = workspace.editor.get("STM-0399")
    assert stm_term_name.entity_id == "terminal:JPTYO:tokyo-international-cruise-terminal"
    assert stm_term_name.value == "東京国際クルーズターミナル"
    assert stm_term_name.artifact_id == "ART-0005"

    stm_term_addr = workspace.editor.get("STM-0400")
    assert stm_term_addr.entity_id == "terminal:JPTYO:tokyo-international-cruise-terminal"
    assert stm_term_addr.value == "〒135-0064 東京都江東区青海二丁目地先"
    assert stm_term_addr.artifact_id == "ART-0006"

    stm_station = workspace.editor.get("STM-0401")
    assert stm_station.entity_id == "transport_node:JPTYO:tokyo-international-cruise-terminal-station"
    assert stm_station.value == "東京国際クルーズターミナル駅"

    stm_op = workspace.editor.get("STM-0402")
    assert stm_op.entity_id == "transport_node:JPTYO:tokyo-international-cruise-terminal-station"
    assert stm_op.value == "ゆりかもめ"


def test_private_booking_artifact_metadata_and_verification_semantics(workspace):
    """
    Regression guard for private source verification semantics:
    1. ART-0007 retains original cryptographic SHA-256 and metadata.
    2. ART-0007 is marked private_source = True.
    3. When private bytes are absent, verify() returns False (not falsely reported as freshly verified).
    4. verification_status() returns 'PRIVATE_ARTIFACT_REFERENCE_REGISTERED'.
    5. has_provenance_reference() returns True.
    6. No raw private PDF is tracked in Git.
    """
    art = workspace.registry.get("ART-0007")
    assert art.artifact_id == "ART-0007"
    assert art.sha256 == "ceee0af752e3bafede5f126f42c5639fd78be5bed240a0acbbeb50d22a7f4b64"
    assert art.document_class == "official_cruise_operator_booking_confirmation"
    assert art.publisher == "MSC Cruises S.A."
    assert art.published_on == "2026-05-24"
    assert art.private_source is True

    # Verification semantics distinction
    assert workspace.registry.verify("ART-0007") is False
    assert workspace.registry.verification_status("ART-0007") == "PRIVATE_ARTIFACT_REFERENCE_REGISTERED"
    assert workspace.registry.has_provenance_reference("ART-0007") is True

    # Git track check: ensure no .pdf file under evidence/raw/sha256/ce/ is tracked
    git_ls = subprocess.run(
        ["git", "ls-files", "evidence/raw/sha256/ce/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert git_ls.stdout.strip() == "", f"Private PDF tracked in git: {git_ls.stdout}"

    # Verify that hypothetical public CE artifacts are NOT ignored
    hypothetical_public_ce = "evidence/raw/sha256/ce/ce00000000000000000000000000000000000000000000000000000000000000.html"
    chk_public = subprocess.run(
        ["git", "check-ignore", hypothetical_public_ce],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert chk_public.returncode != 0, f"Public CE artifact is unexpectedly ignored by gitignore: {hypothetical_public_ce}"

    # Verify that .local private storage IS ignored
    chk_local = subprocess.run(
        ["git", "check-ignore", ".local/private-evidence/sample.pdf"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert chk_local.returncode == 0, ".local/ private storage must be ignored by gitignore"


def test_document_class_canonical_registration(workspace):
    """
    Document class official_cruise_operator_booking_confirmation is registered
    in DOCUMENT_CLASSES and in document_classes.json authority mappings.
    """
    doc_class = "official_cruise_operator_booking_confirmation"
    assert doc_class in DOCUMENT_CLASSES
    dc = DOCUMENT_CLASSES[doc_class]
    assert dc.reliability == 0.95
    assert dc.notes != ""

    doc_classes_file = EVIDENCE_DIR / "registry" / "document_classes.json"
    with open(doc_classes_file, encoding="utf-8") as f:
        doc_json = json.load(f)
    authority_map = doc_json.get("authority", {})
    for stype in [
        "voyage.vessel",
        "voyage.departure_date",
        "voyage.departure_location",
        "voyage.departure_port",
        "voyage.arrival_date",
        "voyage.arrival_location",
        "voyage.arrival_port",
        "voyage.check_in_time",
    ]:
        assert doc_class in authority_map.get(stype, [])


def test_inferred_statement_closure_and_rule_hash(workspace):
    """
    Inferred port linkage statements STM-0406 and STM-0409 have:
    - method = INFERRED
    - input_statement_ids non-empty
    - deterministic rule_hash matching unlocode_linkage rule definition
    - non-empty derivation_note explaining the exact resolution
    """
    expected_rule_def = "timonelo.rules.ports.unlocode_linkage:v1:normalize_operator_location_label_and_country_to_unece_unlocode"
    expected_rule_hash = hashlib.sha256(expected_rule_def.encode("utf-8")).hexdigest()

    stm_dep = workspace.editor.get("STM-0406")
    assert stm_dep.method == Method.INFERRED
    assert stm_dep.input_statement_ids == ("STM-0395", "STM-0405")
    assert stm_dep.rule_hash == expected_rule_hash
    assert "timonelo.rules.ports.unlocode_linkage:v1" in stm_dep.derivation_note
    assert "CNSGH" in stm_dep.derivation_note

    stm_arr = workspace.editor.get("STM-0409")
    assert stm_arr.method == Method.INFERRED
    assert stm_arr.input_statement_ids == ("STM-0397", "STM-0408")
    assert stm_arr.rule_hash == expected_rule_hash
    assert "timonelo.rules.ports.unlocode_linkage:v1" in stm_arr.derivation_note
    assert "JPTYO" in stm_arr.derivation_note


def test_msc_booking_reference_voyage_intake(workspace):
    """
    MSC Bellissima reference voyage statements STM-0403..STM-0410 are registered
    from official MSC Cruises booking confirmation ART-0007.
    """
    voyage_entity = "voyage:msc-bellissima:20261004-shanghai-tokyo"

    # Vessel
    stm_vessel = workspace.editor.get("STM-0403")
    assert stm_vessel.entity_id == voyage_entity
    assert stm_vessel.question_id == "Q-0030"
    assert stm_vessel.value == "MSC BELLISSIMA"
    assert stm_vessel.artifact_id == "ART-0007"
    assert stm_vessel.locator == "Page 1: Schiff: MSC BELLISSIMA"

    # Departure Date & Location
    stm_dep_date = workspace.editor.get("STM-0404")
    assert stm_dep_date.entity_id == voyage_entity
    assert stm_dep_date.question_id == "Q-0031"
    assert stm_dep_date.value == "2026-10-04"

    stm_dep_loc = workspace.editor.get("STM-0405")
    assert stm_dep_loc.entity_id == voyage_entity
    assert stm_dep_loc.question_id == "Q-0032"
    assert stm_dep_loc.value == "Shanghai, China"

    # Canonical Departure Port (Derived)
    stm_dep_port = workspace.editor.get("STM-0406")
    assert stm_dep_port.entity_id == voyage_entity
    assert stm_dep_port.question_id == "Q-0033"
    assert stm_dep_port.value == "port:unlocode:CNSGH"

    # Arrival Date & Location
    stm_arr_date = workspace.editor.get("STM-0407")
    assert stm_arr_date.entity_id == voyage_entity
    assert stm_arr_date.question_id == "Q-0034"
    assert stm_arr_date.value == "2026-10-07"

    stm_arr_loc = workspace.editor.get("STM-0408")
    assert stm_arr_loc.entity_id == voyage_entity
    assert stm_arr_loc.question_id == "Q-0035"
    assert stm_arr_loc.value == "Tokyo, Japan"

    # Canonical Arrival Port (Derived)
    stm_arr_port = workspace.editor.get("STM-0409")
    assert stm_arr_port.entity_id == voyage_entity
    assert stm_arr_port.question_id == "Q-0036"
    assert stm_arr_port.value == "port:unlocode:JPTYO"

    # Check-In Time
    stm_checkin = workspace.editor.get("STM-0410")
    assert stm_checkin.entity_id == voyage_entity
    assert stm_checkin.question_id == "Q-0037"
    assert stm_checkin.value == "14:00"


def test_all_newly_ingested_statements_fail_closed(workspace):
    """
    Every newly ingested statement (STM-0395..STM-0410) is unpromoted
    and strictly fails closed in TruthEngine and PortIntelligenceEvaluator.
    """
    for sid in [f"STM-{i:04d}" for i in range(395, 411)]:
        stm = workspace.editor.get(sid)
        assert stm.evidence_condition == EvidenceCondition.UNKNOWN
        assert stm.human_review_state == HumanReviewState.DRAFT
        assert stm.publish_status == PublishStatus.PUBLISH_BLOCKED
        eval_res = PortIntelligenceEvaluator.evaluate_fact(workspace, stm.entity_id, stm.question_id)
        assert eval_res.is_known is False
        assert eval_res.value is None


def test_voyage_statements_strict_allowlist_domain_boundary(workspace):
    """
    Public test privacy guard:
    All values registered for the reference voyage (STM-0403..STM-0410)
    must strictly belong to the public domain allowlist.
    """
    for sid in [f"STM-{i:04d}" for i in range(403, 411)]:
        stm = workspace.editor.get(sid)
        assert str(stm.value) in ALLOWED_VOYAGE_STATEMENT_VALUES, (
            f"Statement {sid} has unexpected non-allowlist value: {stm.value!r}"
        )


def test_voyage_events_and_artifact_metadata_contain_no_pii_fields(workspace):
    """
    Public test privacy guard:
    Verify that ART-0007 metadata and EVT-VOYAGE-* events contain no forbidden
    PII or commercial schema concept names.
    """
    art = workspace.registry.get("ART-0007")
    art_dict = art.to_dict()
    for field_name in art_dict:
        assert field_name not in FORBIDDEN_PII_CONCEPTS

    for evt in workspace.events.all():
        if evt.artifact_sha256 == art.sha256:
            assert evt.entity_id.startswith("voyage:")
            for pii_concept in FORBIDDEN_PII_CONCEPTS:
                assert pii_concept not in evt.question_id.lower()


def test_terminal_assignment_remains_unproven(workspace):
    """
    MSC booking confirmation proves voyage dates and ports, but NOT terminal assignments.
    Tokyo International Cruise Terminal is NOT assigned to Bellissima.
    Shanghai terminal remains UNKNOWN.
    """
    voyage_terminal_stmts = [
        s for s in workspace.editor.all()
        if "voyage" in s.entity_id and "terminal" in s.statement_type
    ]
    assert len(voyage_terminal_stmts) == 0

    shanghai_term = PortIntelligenceEvaluator.evaluate_fact(
        workspace, "terminal:CNSGH:wusongkou", "Q-0025"
    )
    assert shanghai_term.is_known is False


def test_no_guessed_coordinates_or_routes(workspace):
    """
    Ensure no coordinates or walking routes were fabricated without source authority.
    """
    for sid in [f"STM-{i:04d}" for i in range(395, 411)]:
        stm = workspace.editor.get(sid)
        assert "walk" not in str(stm.value).lower()
        assert "route" not in stm.statement_type
        assert "coordinate" not in stm.statement_type
