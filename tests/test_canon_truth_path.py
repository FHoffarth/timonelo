"""
tests/test_canon_truth_path.py

Truth-Path Hardening and Repository Canon Tests.
Verifies that:
1. One canonical epistemic model is enforced (ADR-0002).
2. Bridge Officer Tim is strictly an orchestrator without truth authoring power.
3. Legacy hypothesis tools are quarantined and cannot write to canonical knowledge.
4. Evidence Gatekeeper blocks ungrounded facts, missing sources, and synthetic geometry.
"""

import pytest
from src.timonelo.ontology.models import (
    Method,
    Derivation,
    ReviewState,
    GeometryProvenance,
)
from src.timonelo.database.bridge_officer import BridgeOfficer
from src.timonelo.factory.patch_engine import ShipPatchEngine
from src.timonelo.factory.archetype_generator import StateroomArchetypeGenerator
from src.timonelo.evidence.gatekeeper import (
    EvidenceGatekeeper,
    SourceArtifact,
    GeometryProvenanceRecord,
    GeometryProvenanceType,
    SourceType,
    VerificationStatus,
)


def test_epistemic_enums_aligned_to_adr0002():
    """Verify epistemic enums match ADR-0002 multi-axial model."""
    assert Method.DIRECT.value == "DIRECT"
    assert Method.CALCULATED.value == "CALCULATED"
    assert Method.INFERRED.value == "INFERRED"

    assert Derivation.LOCAL.value == "LOCAL"
    assert Derivation.SISTER_SHIP.value == "SISTER_SHIP"
    assert Derivation.REFERENCE_MODEL.value == "REFERENCE_MODEL"
    assert Derivation.GENERATED.value == "GENERATED"

    assert ReviewState.UNREVIEWED.value == "UNREVIEWED"
    assert ReviewState.REVIEWED.value == "REVIEWED"
    assert ReviewState.CONFLICTED.value == "CONFLICTED"

    assert GeometryProvenance.DIRECT_SOURCE_GEOMETRY.value == "DIRECT_SOURCE_GEOMETRY"
    assert GeometryProvenance.TRANSFORMED_SOURCE_GEOMETRY.value == "TRANSFORMED_SOURCE_GEOMETRY"
    assert GeometryProvenance.DERIVED_GEOMETRY.value == "DERIVED_GEOMETRY"
    assert GeometryProvenance.SYNTHETIC_GEOMETRY.value == "SYNTHETIC_GEOMETRY"
    assert GeometryProvenance.UNKNOWN_PROVENANCE.value == "UNKNOWN_PROVENANCE"


def test_bridge_officer_is_orchestration_only():
    """Verify Bridge Officer Tim has no authority to declare facts true or store confidence."""
    officer = BridgeOfficer()
    assert officer.is_orchestration_only is True
    assert officer.officer_id == "bridge_officer_tim"

    # Must not store confidence score
    assert not hasattr(officer, "confidence_score")

    # Pipeline status must be purely operational
    status = officer.get_pipeline_status()
    assert status["role"] == "PIPELINE_ORCHESTRATOR"
    assert status["can_author_ground_truth"] is False
    assert status["can_override_evidence_gatekeeper"] is False


def test_patch_engine_is_quarantined_hypothesis_tool():
    """Verify ShipPatchEngine is quarantined for hypothesis use only."""
    assert ShipPatchEngine.is_quarantined_hypothesis_only() is True


def test_archetype_generator_is_quarantined_and_forces_generated_derivation():
    """Verify StateroomArchetypeGenerator is quarantined and forces Derivation.GENERATED."""
    assert StateroomArchetypeGenerator.is_quarantined_hypothesis_only() is True

    # Generate staterooms for Deck 14
    cabins, _, _ = StateroomArchetypeGenerator.generate_full_deck_staterooms(deck_number=14)
    assert len(cabins) > 0
    for c in cabins.values():
        for link in c.evidence_links:
            assert link.derivation == Derivation.GENERATED


def test_evidence_gatekeeper_blocks_missing_source():
    """Verify Evidence Gatekeeper blocks publication if primary source is missing."""
    gatekeeper = EvidenceGatekeeper()

    gatekeeper.register_source(
        SourceArtifact(
            source_id="ART-TEST-MISSING",
            source_type=SourceType.OFFICIAL_PDF,
            title="Nonexistent PDF",
            publisher="MSC Cruises",
            file_path="nonexistent/file.pdf",
            sha256="abc123fake",
            verification_status=VerificationStatus.MISSING,
        )
    )

    result = gatekeeper.evaluate_publish_gate()
    assert result.status.value == "PUBLISH_BLOCKED"
    assert any("PRIMARY_SOURCE_MISSING" in r for r in result.reasons)


def test_evidence_gatekeeper_blocks_synthetic_geometry_with_high_confidence():
    """Verify Evidence Gatekeeper rejects synthetic geometry attempting to claim high confidence."""
    gatekeeper = EvidenceGatekeeper()

    gatekeeper.register_source(
        SourceArtifact(
            source_id="ART-VALID",
            source_type=SourceType.OFFICIAL_PDF,
            title="Verified Deck Plan",
            publisher="MSC Cruises",
            file_path="knowledge/evidence/msc_deck_plan.pdf",
            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            verification_status=VerificationStatus.VERIFIED,
        )
    )

    gatekeeper.add_geometry(
        GeometryProvenanceRecord(
            object_id="CABIN-99999",
            deck_number=10,
            geometry_type=GeometryProvenanceType.SYNTHETIC_GEOMETRY,
            confidence=0.99,  # Unjustified for synthetic geometry
        )
    )

    result = gatekeeper.evaluate_publish_gate()
    assert result.status.value == "PUBLISH_BLOCKED"
    assert any("GEOMETRY_PROVENANCE_VIOLATION" in r for r in result.reasons)
