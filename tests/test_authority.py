"""
Tests for Central Authority Matrix & StatementEditor Authority Enforcement (P0-B Step 2B.1B.0).

Governed by ADR-0002 §6, §7, §13.
"""

import os
import shutil
import tempfile
import pytest

from timonelo.evidence import (
    ArtifactStore,
    authority,
)
from timonelo.evidence.authority import AuthorityError, authoritative_classes, check
from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.review import ReviewLog
from timonelo.ontology.models import EvidenceCondition, HumanReviewState, PublishStatus


@pytest.fixture
def temp_editor_env(tmp_path):
    reg_dir = tmp_path / "registry"
    reg_dir.mkdir()
    reg = ArtifactRegistry(str(reg_dir))

    doc = tmp_path / "sample_deckplan.pdf"
    doc.write_bytes(b"%PDF-1.4 official deckplan test")

    art = reg.register(
        path=str(doc),
        document_class="cruise_line_deck_plan",
        acquired_on="2026-08-19",
        acquisition_method="download",
        publisher="MSC Cruises",
        version="11.2025 DEU",
    )

    review_log = ReviewLog(str(tmp_path / "reviews.json"))
    conflict_log = ConflictLog(str(tmp_path / "conflicts.json"))
    editor = StatementEditor(
        path=str(tmp_path / "statements.json"),
        registry=reg,
        review_log=review_log,
        conflict_log=conflict_log,
    )

    return {
        "registry": reg,
        "artifact": art,
        "editor": editor,
        "review_log": review_log,
        "conflict_log": conflict_log,
    }


# =============================================================================
# TASK A & B: POSITIVE & NARROW AUTHORITY CHECKS
# =============================================================================

def test_central_authority_deckplan_authoritative_classes():
    """Verify exact authoritative classes for newly added narrow statement types."""
    assert "cruise_line_deck_plan" in authoritative_classes("vessel.total_cabins")
    assert "cruise_line_deck_plan" in authoritative_classes("vessel.passenger_capacity_max")
    assert "cruise_line_deck_plan" in authoritative_classes("cabin.bed_configuration")


def test_statement_editor_accepts_deckplan_supported_narrow_types(temp_editor_env):
    """StatementEditor.create() accepts deckplan-supported narrow statement types."""
    editor = temp_editor_env["editor"]
    art = temp_editor_env["artifact"]

    # 1. vessel.total_cabins
    s1 = editor.create(
        entity_id="msc-meraviglia",
        question_id="vessel.total_cabins",
        statement_type="vessel.total_cabins",
        value=2214,
        artifact_id=art.artifact_id,
        locator="page:2",
        read_by="test_pipeline",
        read_on="2026-08-19",
        page=2,
    )
    assert s1.statement_type == "vessel.total_cabins"
    assert s1.value == 2214
    assert s1.evidence_condition == EvidenceCondition.UNKNOWN.value
    assert s1.human_review_state == HumanReviewState.DRAFT.value
    assert s1.publish_status == PublishStatus.PUBLISH_BLOCKED.value

    # 2. vessel.passenger_capacity_max
    s2 = editor.create(
        entity_id="msc-meraviglia",
        question_id="vessel.passenger_capacity_max",
        statement_type="vessel.passenger_capacity_max",
        value=5714,
        artifact_id=art.artifact_id,
        locator="page:2",
        read_by="test_pipeline",
        read_on="2026-08-19",
        page=2,
    )
    assert s2.statement_type == "vessel.passenger_capacity_max"
    assert s2.value == 5714

    # 3. cabin.bed_configuration
    s3 = editor.create(
        entity_id="msc-meraviglia:cabin:BA",
        question_id="cabin.bed_configuration",
        statement_type="cabin.bed_configuration",
        value="Twin beds convertible to double",
        artifact_id=art.artifact_id,
        locator="page:2",
        read_by="test_pipeline",
        read_on="2026-08-19",
        page=2,
    )
    assert s3.statement_type == "cabin.bed_configuration"
    assert s3.value == "Twin beds convertible to double"


# =============================================================================
# TASK B & F: NEGATIVE AUTHORITY REJECTIONS
# =============================================================================

@pytest.mark.parametrize(
    "unsupported_type",
    [
        "vessel.engine_output",
        "vessel.imo",
        "vessel.mmsi",
        "vessel.gross_tonnage",
        "vessel.length_m",
        "vessel.beam_m",
        "vessel.propulsion",
        "vessel.speed_max_knots",
        "vessel.crew_count",
        "vessel.ship_class",
        "vessel.builder",
        "vessel.build_cost",
        "cabin.balcony_percentage",
        "cabin.standard_amenities",
        "cabin.generic_amenities",
        "ship.fact",
        "vessel.capacity",
    ],
)
def test_authority_check_rejects_unsupported_statement_types(unsupported_type):
    """Direct authority.check() rejects technical/generic claims for cruise_line_deck_plan."""
    with pytest.raises(AuthorityError):
        check(unsupported_type, "cruise_line_deck_plan")


@pytest.mark.parametrize(
    "unsupported_type",
    [
        "vessel.engine_output",
        "vessel.imo",
        "vessel.gross_tonnage",
        "vessel.crew_count",
        "cabin.balcony_percentage",
    ],
)
def test_statement_editor_rejects_unauthorized_claims(temp_editor_env, unsupported_type):
    """StatementEditor.create() rejects unauthorized claims for cruise_line_deck_plan."""
    editor = temp_editor_env["editor"]
    art = temp_editor_env["artifact"]

    with pytest.raises(AuthorityError):
        editor.create(
            entity_id="msc-meraviglia",
            question_id=unsupported_type,
            statement_type=unsupported_type,
            value=12345,
            artifact_id=art.artifact_id,
            locator="page:1",
            read_by="test_pipeline",
            read_on="2026-08-19",
        )


# =============================================================================
# TASK G: NO WORKSPACE OVERRIDE RELIANCE
# =============================================================================

def test_central_authority_curated_classes_protected():
    """Curated class IDs are protected against workspace override tampering."""
    assert "cruise_line_deck_plan" in authority.CURATED_CLASS_IDS
    assert "shipyard_general_arrangement" in authority.CURATED_CLASS_IDS
    assert "builder_specification" in authority.CURATED_CLASS_IDS
    assert "classification_society_record" in authority.CURATED_CLASS_IDS
