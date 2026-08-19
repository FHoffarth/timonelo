"""
Tests for EvidenceGatekeeper — Canonical Gatekeeper Foundation (P0-B Step 1).

Governed by ADR-0002 §4, §6, §7, §8, §9 and P0-A.5 Truth Model.
"""

import os
from enum import Enum
import pytest
from timonelo.evidence.engine import Statement
from timonelo.evidence.gatekeeper import (
    ArtifactVerificationStatus,
    ConflictGateResult,
    EvidenceGatekeeper,
    GeometryProvenanceRecord,
    SourceArtifactRecord,
    sanitize_report_content,
)
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
    import hashlib
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


def test_gatekeeper_1_missing_artifact_blocks_publish(tmp_path):
    """1. Missing physical artifact blocks publication."""
    gk = EvidenceGatekeeper()
    gk.register_source(
        SourceArtifactRecord(
            source_id="SRC-MISSING",
            title="Non-existent document",
            expected_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            file_path=str(tmp_path / "does_not_exist.pdf"),
            document_class="cruise_line_deck_plan",
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert result.is_publishable is False
    assert result.artifact_statuses["SRC-MISSING"] == ArtifactVerificationStatus.MISSING
    assert any("PRIMARY_SOURCE_MISSING" in r for r in result.reasons)


def test_gatekeeper_2_hash_mismatch_blocks_publish(tmp_path):
    """2. Wrong artifact hash blocks publication."""
    f = tmp_path / "corrupted.pdf"
    f.write_bytes(b"corrupted contents")

    gk = EvidenceGatekeeper()
    gk.register_source(
        SourceArtifactRecord(
            source_id="SRC-CORRUPT",
            title="Corrupted document",
            expected_sha256="77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
            file_path=str(f),
            document_class="cruise_line_deck_plan",
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert result.artifact_statuses["SRC-CORRUPT"] == ArtifactVerificationStatus.HASH_MISMATCH
    assert any("SOURCE_HASH_MISMATCH" in r for r in result.reasons)


def test_gatekeeper_3_correct_artifact_hash_alone_does_not_make_statement_supported(valid_meraviglia_source):
    """3. Valid artifact hash alone does not make a statement supported."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)

    # Statement has valid artifact reference, but its evidence_condition is UNKNOWN
    stmt = Statement(
        statement_id="stmt-1",
        entity_id="msc-meraviglia",
        question_id="deck.count",
        value=19,
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("STATEMENT_NOT_SUPPORTED" in r for r in result.reasons)


def test_gatekeeper_4_unknown_evidence_condition_blocks(valid_meraviglia_source):
    """4. EvidenceCondition.UNKNOWN blocks publication."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(
        Statement(
            statement_id="stmt-unk",
            entity_id="msc-meraviglia",
            question_id="ship.imo",
            value=9760512,
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_condition=EvidenceCondition.UNKNOWN,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("STATEMENT_NOT_SUPPORTED" in r for r in result.reasons)


def test_gatekeeper_5_unsupported_evidence_condition_blocks(valid_meraviglia_source):
    """5. EvidenceCondition.UNSUPPORTED blocks publication."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(
        Statement(
            statement_id="stmt-unsup",
            entity_id="msc-meraviglia",
            question_id="cabin.sqm",
            value=35.0,
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_condition=EvidenceCondition.UNSUPPORTED,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED


def test_gatekeeper_6_conflicted_evidence_condition_blocks(valid_meraviglia_source):
    """6. EvidenceCondition.CONFLICTED blocks publication."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(
        Statement(
            statement_id="stmt-conf",
            entity_id="msc-meraviglia",
            question_id="ship.max_passengers",
            value=5686,
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_condition=EvidenceCondition.CONFLICTED,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED


def test_gatekeeper_7_supported_plus_draft_blocks(valid_meraviglia_source):
    """7. SUPPORTED + DRAFT review state blocks publication."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(
        Statement(
            statement_id="stmt-draft",
            entity_id="msc-meraviglia",
            question_id="deck.name",
            value="Deck 16 - Miami",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_condition=EvidenceCondition.SUPPORTED,
            human_review_state=HumanReviewState.DRAFT,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("STATEMENT_NOT_APPROVED" in r for r in result.reasons)


def test_gatekeeper_8_supported_plus_approved_plus_publish_blocked(valid_meraviglia_source):
    """8. SUPPORTED + APPROVED + PUBLISH_BLOCKED blocks publication."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(
        Statement(
            statement_id="stmt-blocked",
            entity_id="msc-meraviglia",
            question_id="deck.name",
            value="Deck 16 - Miami",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_condition=EvidenceCondition.SUPPORTED,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_BLOCKED,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_BLOCKED
    assert any("STATEMENT_PUBLISH_BLOCKED" in r for r in result.reasons)


def test_gatekeeper_9_valid_conjunction_allows_publish(valid_meraviglia_source):
    """9. Valid conjunction (valid artifact + SUPPORTED + APPROVED + PUBLISH_ALLOWED) succeeds."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(
        Statement(
            statement_id="stmt-ok",
            entity_id="msc-meraviglia",
            question_id="deck.name",
            value="Deck 16 - Miami",
            method=Method.DIRECT,
            derivation=Derivation.LOCAL,
            evidence_condition=EvidenceCondition.SUPPORTED,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.status == PublishStatus.PUBLISH_ALLOWED
    assert result.is_publishable is True
    assert result.reasons == []


def test_gatekeeper_10_synthetic_geometry_remains_synthetic(valid_meraviglia_source):
    """10. Synthetic geometry is recognized as synthetic and does not fail when marked synthetic."""
    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_geometry(
        GeometryProvenanceRecord(
            object_id="CABIN-14122",
            deck_number=14,
            geometry_provenance=GeometryProvenance.SYNTHETIC_GEOMETRY,
        )
    )
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    result = gk.evaluate_publish_gate()
    assert result.synthetic_geometry_count == 1
    assert result.direct_geometry_count == 0


def test_gatekeeper_11_12_13_no_state_mutation(valid_meraviglia_source):
    """11, 12, 13: Gatekeeper never mutates EvidenceCondition, HumanReviewState, or PublishStatus."""
    stmt = Statement(
        statement_id="stmt-immutable",
        entity_id="msc-meraviglia",
        question_id="deck.count",
        value=19,
        method=Method.DIRECT,
        derivation=Derivation.LOCAL,
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    )

    gk = EvidenceGatekeeper()
    gk.register_source(valid_meraviglia_source)
    gk.add_statement(stmt)
    gk.set_conflict_result(ConflictGateResult(executed=True, conflicts_found=0, unresolved_conflicts=0))

    _ = gk.evaluate_publish_gate()

    # Assert statement fields are 100% untouched
    assert stmt.evidence_condition == EvidenceCondition.UNKNOWN
    assert stmt.human_review_state == HumanReviewState.DRAFT
    assert stmt.publish_status == PublishStatus.PUBLISH_BLOCKED


def test_gatekeeper_14_no_bare_verified_in_gatekeeper():
    """14. No bare VERIFIED state is returned or accepted."""
    import timonelo.evidence.gatekeeper as gk_mod
    for name, obj in inspect_classes(gk_mod):
        if issubclass(obj, Enum):
            for member in obj:
                assert member.value != "VERIFIED", f"Bare VERIFIED found in enum {obj.__name__}"


def test_gatekeeper_15_official_deckplans_source_not_described_as_builder_or_ga():
    """15. Official MSC Deckplans publication is not mislabeled as builder drawing or shipyard GA."""
    source = SourceArtifactRecord(
        source_id="MSC-MER-DECKPLAN-11-2025-DEU",
        title="Official MSC Cruises Meraviglia Deckplans, Edition 11.2025 DEU",
        expected_sha256="77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9",
        file_path="evidence/raw/sha256/77/77f5a51b2465cf0aa7264a1262a768b58cd43609390a9e21e74be8286d2a45e9.pdf",
        document_class="cruise_line_deck_plan",
        publisher="MSC Cruises",
        edition="11.2025 DEU",
    )
    assert "builder" not in source.title.lower()
    assert "shipyard" not in source.title.lower()
    assert "ga drawing" not in source.title.lower()
    assert source.document_class == "cruise_line_deck_plan"


def test_sanitize_report_content_replaces_fraudulent_claims_when_blocked():
    """Report sanitizer scrubs ungrounded claims when publish gate is blocked."""
    untruthful_report = "This pack has 100% verified attributes and 0 conflicts."
    blocked_result = EvidenceGatekeeper().evaluate_publish_gate()

    sanitized = sanitize_report_content(untruthful_report, blocked_result)
    assert "100% verified" not in sanitized
    assert "0 conflicts" not in sanitized
    assert "[UNVERIFIED / BLOCKED]" in sanitized


def inspect_classes(module):
    import inspect
    return inspect.getmembers(module, inspect.isclass)
