"""
Tests for EvidenceGatekeeper — Statement -> Evidence Event -> Artifact Closure (P0-B Step 1B).

Governed by ADR-0002 §4, §6, §7, §8, §9 and P0-A.5 / P0-B Truth Model.
"""

from enum import Enum
import hashlib
import os
import pytest

from timonelo.evidence.engine import Statement
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.gatekeeper import (
    ArtifactVerificationStatus,
    ConflictGateResult,
    EvidenceGatekeeper,
    GeometryProvenanceRecord,
    SourceArtifactRecord,
    sanitize_report_content,
)
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.ontology.models import (
    Derivation,
    EvidenceCondition,
    GeometryProvenance,
    HumanReviewState,
    Method,
    PublishStatus,
)


@pytest.fixture
def valid_meraviglia_source(tmp_path):
    # Create real file matching hash
    f = tmp_path / "meraviglia_deckplans.pdf"
    content = b"%PDF-1.4 official msc deckplans 11.2025 DEU"
    f.write_bytes(content)
    sha = hashlib.sha256(content).hexdigest()

    return SourceArtifactRecord(
        source_id="MSC-MER-DECKPLAN-11-2025-DEU",
        title="Official MSC Cruises Meraviglia Deckplans, Edition 11.2025 DEU",
        expected_sha256=sha,
        file_path=str(f),
        document_class="cruise_line_deck_plan",
        publisher="MSC Cruises",
        edition="11.2025 DEU",
    )


# =============================================================================
# TASK F — NEGATIVE TEST MATRIX (STATEMENT -> EVENT -> ARTIFACT CLOSURE)
# =============================================================================

def test_gatekeeper_closure_1_supported_with_zero_evidence_events_blocks(valid_meraviglia_source):
    """1. SUPPORTED statement with zero evidence events is blocked."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        value="Deck 16 - Miami",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=(),  # Zero evidence events!
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("STATEMENT_ZERO_EVIDENCE_EVENTS" in r for r in result.reasons)


def test_gatekeeper_closure_2_unknown_evidence_event_id_blocks(valid_meraviglia_source):
    """2. Statement referencing unknown/unrecorded evidence event ID is blocked."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        value="Deck 16 - Miami",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-NON-EXISTENT",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("UNKNOWN_EVIDENCE_EVENT" in r for r in result.reasons)


def test_gatekeeper_closure_3_event_references_unknown_artifact_blocks(valid_meraviglia_source):
    """3. EvidenceEvent referencing unregistered artifact SHA is blocked."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)

    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256="deadbeef" * 8,  # Not in registered sources!
        locator="p.3",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        observed_value="Deck 16",
        observed_by="auditor",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        value="Deck 16",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("EVENT_ARTIFACT_NOT_REGISTERED" in r for r in result.reasons)


def test_gatekeeper_closure_4_event_artifact_hash_mismatch_blocks(tmp_path):
    """4. Event referencing hash-mismatched/corrupted artifact is blocked."""
    f = tmp_path / "corrupted.pdf"
    f.write_bytes(b"bad bytes")

    corrupt_source = SourceArtifactRecord(
        source_id="SRC-CORRUPT",
        title="Corrupted doc",
        expected_sha256="77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
        file_path=str(f),
        document_class="cruise_line_deck_plan",
    )

    gk = EvidenceGatekeeper()
    gk.register_source(corrupt_source)

    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256="77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
        locator="p.3",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        observed_value="Deck 16",
        observed_by="auditor",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        value="Deck 16",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("EVENT_ARTIFACT_HASH_MISMATCH" in r for r in result.reasons)


def test_gatekeeper_closure_5_placeholder_locator_blocks(valid_meraviglia_source):
    """5. Event with placeholder locator (e.g. 'unknown', 'n/a', 'source') is blocked."""
    placeholders = ["", "unknown", "n/a", "source", "document", "none", "null"]

    for ph in placeholders:
        gk = EvidenceGatekeeper()
        gk.register_source(valid_meraviglia_source)

        evt_id = f"EVT-{ph or 'empty'}"
        event = EvidenceEvent(
            event_id=evt_id,
            artifact_sha256=valid_meraviglia_source.expected_sha256,
            locator=ph,
            entity_id="msc-meraviglia",
            question_id="deck.name",
            observed_value="Deck 16",
            observed_by="auditor",
            observed_on="2026-08-19",
        )
        gk.register_event(event)

        stmt = Statement(
            statement_id=f"stmt-{ph or 'empty'}",
            entity_id="msc-meraviglia",
            question_id="deck.name",
            value="Deck 16",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_event_ids=(evt_id,),
            evidence_condition=EvidenceCondition.SUPPORTED,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        )
        gk.add_statement(stmt)
        gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

        result = gk.evaluate_publish_gate()
        assert result.status == PublishStatus.PUBLISH_BLOCKED, f"Placeholder {ph!r} was not blocked"
        assert any("INVALID_EVENT_LOCATOR" in r for r in result.reasons)


def test_gatekeeper_closure_6_unrelated_registered_artifact_cannot_satisfy_statement(valid_meraviglia_source, tmp_path):
    """6. A valid but unrelated registered artifact cannot satisfy a statement citing another artifact."""
    f2 = tmp_path / "other.pdf"
    f2.write_bytes(b"%PDF-1.4 other document")
    sha2 = hashlib.sha256(b"%PDF-1.4 other document").hexdigest()

    other_source = SourceArtifactRecord(
        source_id="SRC-OTHER",
        title="Other doc",
        expected_sha256=sha2,
        file_path=str(f2),
        document_class="cruise_line_deck_plan",
    )

    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.register_source(other_source)

    # Event cites an artifact hash that was never registered
    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256="c0ffee" * 10 + "0000",
        locator="p.1",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        observed_value="Deck 5",
        observed_by="auditor",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia",
        question_id="deck.name",
        value="Deck 5",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("EVENT_ARTIFACT_NOT_REGISTERED" in r for r in result.reasons)


def test_gatekeeper_closure_7_ineligible_document_class_blocks(valid_meraviglia_source):
    """7. Ineligible document class (e.g. deck plans for technical specs) is blocked."""
    reg = QuestionRegistry()
    reg.register(
        Question(
            question_id="Q-0010",
            entity_type="vessel",
            statement_type="cabin.area_sqm",  # Requires shipyard_general_arrangement or builder_specification
            supportable_by=("shipyard_general_arrangement", "builder_specification"),
        )
    )

    gk = EvidenceGatekeeper(question_registry=reg)
    gk.register_source(valid_meraviglia_source)  # document_class is cruise_line_deck_plan!

    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256=valid_meraviglia_source.expected_sha256,
        locator="p.3",
        entity_id="msc-meraviglia:cabin:14122",
        question_id="Q-0010",
        observed_value=22.5,
        observed_by="auditor",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia:cabin:14122",
        question_id="Q-0010",
        value=22.5,
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("INELIGIBLE_DOCUMENT_CLASS" in r for r in result.reasons)


def test_gatekeeper_closure_8_valid_closure_allows_publish(valid_meraviglia_source):
    """8. Valid event + valid artifact + valid locator + eligible class + APPROVED + allowed publish -> ALLOWED."""
    reg = QuestionRegistry()
    reg.register(
        Question(
            question_id="Q-0001",
            entity_type="deck",
            statement_type="deck.venue_present",
            supportable_by=("cruise_line_deck_plan", "shipyard_general_arrangement"),
        )
    )

    gk = EvidenceGatekeeper(question_registry=reg)
    gk.register_source(valid_meraviglia_source)

    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256=valid_meraviglia_source.expected_sha256,
        locator="page:2",
        entity_id="msc-meraviglia:deck:5",
        question_id="Q-0001",
        observed_value="Broadway Theatre",
        observed_by="auditor",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia:deck:5",
        question_id="Q-0001",
        value="Broadway Theatre",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_ALLOWED
    assert result.is_publishable is True
    assert result.reasons == []


def test_gatekeeper_closure_9_unknown_condition_remains_blocked_with_event(valid_meraviglia_source):
    """9. UNKNOWN evidence condition remains blocked even if an evidence event is cited."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)

    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256=valid_meraviglia_source.expected_sha256,
        locator="p.2",
        entity_id="msc-meraviglia:deck:5",
        question_id="deck.name",
        observed_value="Deck 5",
        observed_by="auditor",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia:deck:5",
        question_id="deck.name",
        value="Deck 5",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.UNKNOWN,  # NOT SUPPORTED!
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("STATEMENT_NOT_SUPPORTED" in r for r in result.reasons)


def test_gatekeeper_closure_10_zero_state_mutation(valid_meraviglia_source):
    """10. Gatekeeper evaluation performs zero state mutation on inputs."""
    event = EvidenceEvent(
        event_id="EVT-001",
        artifact_sha256=valid_meraviglia_source.expected_sha256,
        locator="p.2",
        entity_id="msc-meraviglia:deck:5",
        question_id="deck.name",
        observed_value="Deck 5",
        observed_by="auditor",
        observed_on="2026-08-19",
    )

    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia:deck:5",
        question_id="deck.name",
        value="Deck 5",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-001",),
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    )

    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.register_event(event)
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    _ = gk.evaluate_publish_gate()

    # Statement unchanged
    assert stmt.evidence_condition == EvidenceCondition.UNKNOWN
    assert stmt.human_review_state == HumanReviewState.DRAFT
    assert stmt.publish_status == PublishStatus.PUBLISH_BLOCKED
    # Event unchanged
    assert event.locator == "p.2"


# =============================================================================
# TASK G — REAL MERAVIGLIA SOURCE SMOKE TEST
# =============================================================================

def test_real_meraviglia_artifact_closure_smoke():
    """Real MSC Meraviglia Deckplans (11.2025 DEU) end-to-end evidence closure smoke test."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(
        repo_root,
        "evidence",
        "raw",
        "sha256",
        "77",
        "77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf",
    )
    assert os.path.exists(pdf_path), f"Real artifact must exist at {pdf_path}"

    real_source = SourceArtifactRecord(
        source_id="MSC-MER-DECKPLAN-11-2025-DEU",
        title="Official MSC Cruises Meraviglia Deckplans, Edition 11.2025 DEU",
        expected_sha256="77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
        file_path=pdf_path,
        document_class="cruise_line_deck_plan",
        publisher="MSC Cruises",
        edition="11.2025 DEU",
    )

    reg = QuestionRegistry()
    reg.register(
        Question(
            question_id="Q-0005",
            entity_type="deck",
            statement_type="deck.venue_present",
            supportable_by=("cruise_line_deck_plan", "shipyard_general_arrangement"),
        )
    )

    gk = EvidenceGatekeeper(question_registry=reg)
    gk.register_source(real_source)

    # Deck 5 - Corallo is on Page 2 of the official MSC deckplans PDF
    event = EvidenceEvent(
        event_id="EVT-MER-DECK-5",
        artifact_sha256="77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
        locator="page:2",
        entity_id="msc-meraviglia:deck:5",
        question_id="Q-0005",
        observed_value="Deck 5 - Corallo",
        observed_by="human_curator",
        observed_on="2026-08-19",
    )
    gk.register_event(event)

    stmt = Statement(
        statement_id="STMT-MER-DECK-5",
        entity_id="msc-meraviglia:deck:5",
        question_id="Q-0005",
        value="Deck 5 - Corallo",
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_event_ids=("EVT-MER-DECK-5",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()

    assert result.status == PublishStatus.PUBLISH_ALLOWED
    assert result.is_publishable is True
    assert result.artifact_statuses["MSC-MER-DECKPLAN-11-2025-DEU"] == ArtifactVerificationStatus.PRESENT
    assert result.supported_statement_count == 1
    assert result.approved_statement_count == 1
    assert result.reasons == []


def test_sanitize_report_content_replaces_fraudulent_claims_when_blocked():
    """Report sanitizer scrubs ungrounded claims when publish gate is blocked."""
    untruthful_report = "This pack has 100% verified attributes and 0 conflicts."
    blocked_result = EvidenceGatekeeper().evaluate_publish_gate()

    sanitized = sanitize_report_content(untruthful_report, blocked_result)
    assert "100% verified" not in sanitized
    assert "0 conflicts" not in sanitized
    assert "[UNVERIFIED / BLOCKED]" in sanitized


def test_gatekeeper_no_bare_verified_in_enums():
    """No bare VERIFIED state is defined in gatekeeper enums."""
    import timonelo.evidence.gatekeeper as gk_mod
    import inspect
    for name, obj in inspect.getmembers(gk_mod, inspect.isclass):
        if issubclass(obj, Enum):
            for member in obj:
                assert member.value != "VERIFIED", f"Bare VERIFIED found in enum {obj.__name__}"
