"""
Tests for Timonelo Port Factory — Slice 1:
Port Authority Document Classes + Canonical Port Question Registration.

Governed by ADR-0002 §6, §7, §8, §12, §13.
"""

import os
import pytest

from timonelo.evidence import authority
from timonelo.evidence.authority import (
    DOCUMENT_CLASSES,
    AUTHORITY,
    AuthorityError,
    authoritative_classes,
    check,
    is_publishable,
    ValidityScope,
    Acquisition,
    UsePermission,
)
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.models import Statement
from timonelo.ontology.models import (
    Method,
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)


PORT_DOCUMENT_CLASSES = [
    "un_locode_registry",
    "port_authority_official_directory",
    "port_authority_berth_directory",
    "terminal_operator_specification",
    "municipal_transit_authority",
]


def test_port_document_classes_registered():
    for class_id in PORT_DOCUMENT_CLASSES:
        assert class_id in DOCUMENT_CLASSES, f"Missing document class {class_id}"
        dc = DOCUMENT_CLASSES[class_id]
        assert dc.class_id == class_id
        assert 0.0 < dc.reliability < 1.0
        assert isinstance(dc.validity_scope, ValidityScope)
        assert isinstance(dc.acquisition, Acquisition)
        assert isinstance(dc.use_permission, UsePermission)
        assert len(dc.label) > 0


def test_port_document_class_exact_properties():
    un = DOCUMENT_CLASSES["un_locode_registry"]
    assert un.reliability == 0.97
    assert un.validity_scope == ValidityScope.STRUCTURAL
    assert un.acquisition == Acquisition.PUBLIC
    assert un.use_permission == UsePermission.CITE_AND_STORE

    pad = DOCUMENT_CLASSES["port_authority_official_directory"]
    assert pad.reliability == 0.95
    assert pad.validity_scope == ValidityScope.SEASON_SCOPED

    pab = DOCUMENT_CLASSES["port_authority_berth_directory"]
    assert pab.reliability == 0.95
    assert pab.validity_scope == ValidityScope.SEASON_SCOPED

    tos = DOCUMENT_CLASSES["terminal_operator_specification"]
    assert tos.reliability == 0.90
    assert tos.validity_scope == ValidityScope.SEASON_SCOPED

    mta = DOCUMENT_CLASSES["municipal_transit_authority"]
    assert mta.reliability == 0.90
    assert mta.validity_scope == ValidityScope.SEASON_SCOPED


PORT_QUESTIONS = {
    "Q-0023": ("port", "port.un_locode"),
    "Q-0024": ("port", "port.official_name"),
    "Q-0025": ("cruise_terminal", "cruise_terminal.official_name"),
    "Q-0026": ("cruise_terminal", "cruise_terminal.official_address"),
    "Q-0027": ("berth", "berth.max_draft"),
    "Q-0028": ("transport_node", "transport_node.official_name"),
    "Q-0029": ("transport_node", "transport_node.operator"),
}


def test_canonical_questions_json_loads_port_questions():
    registry_path = os.path.join("evidence", "registry", "questions.json")
    assert os.path.exists(registry_path), "questions.json must exist"

    registry = QuestionRegistry.load(registry_path)
    assert len(registry) >= 29

    for qid, (expected_entity, expected_stype) in PORT_QUESTIONS.items():
        q = registry.get(qid)
        assert q.question_id == qid
        assert q.entity_type == expected_entity
        assert q.statement_type == expected_stype
        assert "en" in q.labels
        assert q.unknown_guidance is not None
        assert len(q.unknown_guidance) > 0


def test_existing_question_ids_unchanged():
    registry = QuestionRegistry.load(os.path.join("evidence", "registry", "questions.json"))
    q1 = registry.get("Q-0001")
    assert q1.entity_type == "cabin"
    assert q1.statement_type == "cabin.exists"

    q2 = registry.get("Q-0002")
    assert q2.entity_type == "cabin"
    assert q2.statement_type == "cabin.deck"

    q22 = registry.get("Q-0022")
    assert q22.entity_type == "cabin"
    assert q22.statement_type == "cabin.bunk_or_convertible_sofa"


PROVED = [
    ("un_locode_registry", "port.un_locode"),
    ("port_authority_official_directory", "port.official_name"),
    ("un_locode_registry", "port.official_name"),
    ("port_authority_official_directory", "cruise_terminal.official_name"),
    ("terminal_operator_specification", "cruise_terminal.official_name"),
    ("port_authority_official_directory", "cruise_terminal.official_address"),
    ("terminal_operator_specification", "cruise_terminal.official_address"),
    ("port_authority_berth_directory", "berth.max_draft"),
    ("municipal_transit_authority", "transport_node.official_name"),
    ("port_authority_official_directory", "transport_node.official_name"),
    ("municipal_transit_authority", "transport_node.operator"),
    ("port_authority_official_directory", "transport_node.operator"),
]


def test_authority_mapping_positive_cases():
    for class_id, stype in PROVED:
        assert class_id in authoritative_classes(stype)


def test_authority_mapping_negative_rejections():
    with pytest.raises(AuthorityError):
        check("port.un_locode", "cruise_line_deck_plan")

    with pytest.raises(AuthorityError):
        check("berth.max_draft", "cruise_line_deck_plan")

    with pytest.raises(AuthorityError):
        check("berth.max_draft", "un_locode_registry")

    with pytest.raises(AuthorityError):
        check("cabin.deck", "un_locode_registry")

    with pytest.raises(AuthorityError):
        check("cruise_terminal.official_name", "municipal_transit_authority")

    with pytest.raises(AuthorityError):
        check("cabin.category", "municipal_transit_authority")


def test_question_can_be_supported_by_integration():
    registry = QuestionRegistry.load(os.path.join("evidence", "registry", "questions.json"))

    q_unlocode = registry.get("Q-0023")
    assert q_unlocode.can_be_supported_by("un_locode_registry")
    assert not q_unlocode.can_be_supported_by("cruise_line_deck_plan")

    q_terminal = registry.get("Q-0025")
    assert q_terminal.can_be_supported_by("port_authority_official_directory")
    assert q_terminal.can_be_supported_by("terminal_operator_specification")
    assert not q_terminal.can_be_supported_by("un_locode_registry")


def test_port_statements_are_publishable_when_evidenced():
    for stype in [
        "port.un_locode",
        "port.official_name",
        "cruise_terminal.official_name",
        "cruise_terminal.official_address",
        "berth.max_draft",
        "transport_node.official_name",
        "transport_node.operator",
    ]:
        for class_id in authoritative_classes(stype):
            pub, reason = is_publishable(stype, class_id)
            assert pub is True, f"{stype} with {class_id} should be publishable: {reason}"


def test_no_lifecycle_enum_drift():
    assert set(Method.__members__.keys()) == {"DIRECT", "CALCULATED", "INFERRED"}
    assert set(Derivation.__members__.keys()) == {
        "LOCAL",
        "SISTER_SHIP",
        "REFERENCE_MODEL",
        "GENERATED",
    }
    assert set(EvidenceCondition.__members__.keys()) == {
        "SUPPORTED",
        "UNSUPPORTED",
        "CONFLICTED",
        "UNKNOWN",
    }
    assert set(HumanReviewState.__members__.keys()) == {
        "DRAFT",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        "SUPERSEDED",
    }
    assert set(PublishStatus.__members__.keys()) == {
        "PUBLISH_ALLOWED",
        "PUBLISH_ALLOWED_WITH_WARNINGS",
        "PUBLISH_BLOCKED",
    }


def test_statement_defaults_are_conservative():
    stmt = Statement(
        statement_id="STMT-TEST-001",
        entity_id="port:unlocode:ESBCN",
        question_id="Q-0023",
        statement_type="port.un_locode",
        value="ESBCN",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        artifact_id="ART-TEST-001",
        locator="line:42",
        read_by="test_curator",
        read_on="2026-08-23",
    )
    assert stmt.evidence_condition == EvidenceCondition.UNKNOWN
    assert stmt.human_review_state == HumanReviewState.DRAFT
    assert stmt.publish_status == PublishStatus.PUBLISH_BLOCKED
