"""
tests/test_evidence_gatekeeper.py

Comprehensive Test Suite for Evidence Gatekeeper v1:
- Source Artifact Verification
- Fact-Level Epistemic Integrity
- Geometry Provenance Rules
- Epistemic Ceiling Computation
- Deterministic Coverage Calculation
- Conflict Gate Mechanics
- Publish Gatekeeper (Allow, Warn, Block)
- Negative Regression Test for MSC Meraviglia (Must be PUBLISH_BLOCKED)
- Report Language Guard
"""

import os
import tempfile
import pytest
from timonelo.evidence.gatekeeper import (
    SourceType, VerificationStatus, SourceArtifact, EpistemicStatus,
    EvidenceLocator, FactEvidenceRecord, GeometryProvenanceType,
    GeometryProvenanceRecord, compute_epistemic_ceiling, EpistemicCoverageMetrics,
    ConflictGateResult, PublishStatus, PublishGateResult, EvidenceGatekeeper,
    sanitize_report_content, compute_file_sha256
)


# =========================================================================
# 1. SOURCE ARTIFACT VERIFICATION TESTS
# =========================================================================

def test_source_artifact_verified_with_real_file():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Official General Arrangement Blueprint 2026")
        tmp_path = tmp.name

    try:
        real_hash = compute_file_sha256(tmp_path)
        src = SourceArtifact(
            source_id="SRC-GA-001",
            title="Official GA Plan",
            publisher="Shipyard STX",
            source_type=SourceType.BUILDER_DOC,
            file_path=tmp_path,
            sha256=real_hash
        )
        status = src.verify_physical_artifact()
        assert status == VerificationStatus.VERIFIED
        assert src.verification_status == VerificationStatus.VERIFIED
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_source_artifact_missing_file():
    src = SourceArtifact(
        source_id="SRC-GA-MISSING",
        title="Non-existent Plan",
        publisher="Shipyard STX",
        source_type=SourceType.OFFICIAL_PDF,
        file_path="/invalid/non/existent/path.pdf"
    )
    status = src.verify_physical_artifact()
    assert status == VerificationStatus.MISSING


def test_source_artifact_hash_mismatch():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Content A")
        tmp_path = tmp.name

    try:
        src = SourceArtifact(
            source_id="SRC-GA-TAMPERED",
            title="Tampered Plan",
            publisher="Shipyard STX",
            source_type=SourceType.OFFICIAL_PDF,
            file_path=tmp_path,
            sha256="0000000000000000000000000000000000000000000000000000000000000000"
        )
        status = src.verify_physical_artifact()
        assert status == VerificationStatus.HASH_MISMATCH
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# =========================================================================
# 2. FACT-LEVEL EVIDENCE CONSISTENCY TESTS
# =========================================================================

def test_fact_direct_valid_with_verified_source():
    src = SourceArtifact(
        source_id="SRC-VALID",
        title="Official Brochure",
        publisher="MSC",
        source_type=SourceType.OFFICIAL_PDF,
        verification_status=VerificationStatus.VERIFIED
    )
    fact = FactEvidenceRecord(
        fact_id="FACT-IMO",
        entity_id="msc-bellissima",
        attribute="imo_number",
        value=9760524,
        epistemic_status=EpistemicStatus.DIRECT,
        evidence=[EvidenceLocator(source_id="SRC-VALID", page=2, locator="P2/Specs")]
    )
    valid, err = fact.validate_epistemic_consistency({"SRC-VALID": src})
    assert valid is True
    assert err is None


def test_fact_direct_rejected_without_source():
    fact = FactEvidenceRecord(
        fact_id="FACT-UNGROUNDED",
        entity_id="msc-meraviglia",
        attribute="tonnage_gt",
        value=171598,
        epistemic_status=EpistemicStatus.DIRECT,
        evidence=[]
    )
    valid, err = fact.validate_epistemic_consistency({})
    assert valid is False
    assert "declared DIRECT but contains no evidence" in err


def test_fact_derived_rejected_without_parent_facts():
    fact = FactEvidenceRecord(
        fact_id="FACT-DERIVED-ORPHAN",
        entity_id="msc-bellissima",
        attribute="pax_per_cabin_ratio",
        value=2.55,
        epistemic_status=EpistemicStatus.DERIVED,
        parent_fact_ids=[]
    )
    valid, err = fact.validate_epistemic_consistency({})
    assert valid is False
    assert "specifies no parent_fact_ids" in err


def test_fact_conflicted_requires_two_sources():
    fact = FactEvidenceRecord(
        fact_id="FACT-CONFLICT-SOLO",
        entity_id="msc-bellissima",
        attribute="capacity",
        value=5686,
        epistemic_status=EpistemicStatus.CONFLICTED,
        evidence=[EvidenceLocator(source_id="SRC-1", page=1)]
    )
    valid, err = fact.validate_epistemic_consistency({})
    assert valid is False
    assert "contains fewer than 2 evidence sources" in err


# =========================================================================
# 3. GEOMETRY PROVENANCE TESTS
# =========================================================================

def test_geometry_synthetic_confidence_bound():
    geom_valid = GeometryProvenanceRecord(
        object_id="CABIN-8001",
        deck_number=8,
        geometry_type=GeometryProvenanceType.SYNTHETIC_GEOMETRY,
        confidence=0.50
    )
    valid, err = geom_valid.validate_geometry_provenance({})
    assert valid is True

    geom_invalid = GeometryProvenanceRecord(
        object_id="CABIN-8002",
        deck_number=8,
        geometry_type=GeometryProvenanceType.SYNTHETIC_GEOMETRY,
        confidence=0.95  # Unjustified confidence for template grid
    )
    valid, err = geom_invalid.validate_geometry_provenance({})
    assert valid is False
    assert "unjustified confidence" in err


def test_geometry_direct_requires_verified_source():
    geom = GeometryProvenanceRecord(
        object_id="LIFT-A",
        deck_number=6,
        geometry_type=GeometryProvenanceType.DIRECT_SOURCE_GEOMETRY,
        source_id="SRC-MISSING"
    )
    valid, err = geom.validate_geometry_provenance({"SRC-MISSING": SourceArtifact(
        source_id="SRC-MISSING", title="Missing", publisher="MSC", source_type=SourceType.OFFICIAL_PDF,
        verification_status=VerificationStatus.MISSING
    )})
    assert valid is False
    assert "is not VERIFIED" in err


# =========================================================================
# 4. EPISTEMIC CEILING TESTS
# =========================================================================

def test_compute_epistemic_ceiling_missing_source():
    res = compute_epistemic_ceiling(
        upstream_statuses=[EpistemicStatus.DIRECT],
        source_status=VerificationStatus.MISSING
    )
    assert res == EpistemicStatus.UNVERIFIED


def test_compute_epistemic_ceiling_synthetic_geometry():
    res = compute_epistemic_ceiling(
        upstream_statuses=[EpistemicStatus.DIRECT],
        source_status=VerificationStatus.VERIFIED,
        geometry_type=GeometryProvenanceType.SYNTHETIC_GEOMETRY
    )
    assert res == EpistemicStatus.INFERRED


def test_compute_epistemic_ceiling_mixed_upstream():
    res = compute_epistemic_ceiling(
        upstream_statuses=[EpistemicStatus.DIRECT, EpistemicStatus.DERIVED, EpistemicStatus.DIRECT],
        source_status=VerificationStatus.VERIFIED
    )
    assert res == EpistemicStatus.DERIVED


# =========================================================================
# 5. COVERAGE & CONFLICT GATE TESTS
# =========================================================================

def test_epistemic_coverage_metrics_deterministic():
    metrics = EpistemicCoverageMetrics(
        total_sources=2,
        verified_sources=2,
        total_facts=10,
        direct_facts=8,
        derived_facts=2,
        inferred_facts=0,
        unverified_facts=0,
        total_geometry_objects=100,
        direct_geometry_objects=90,
        synthetic_geometry_objects=10,
        total_graph_relations=50,
        grounded_graph_relations=45
    )
    metrics.compute_all_metrics()
    assert metrics.source_coverage_pct == 100.0
    assert metrics.fact_evidence_coverage_pct == 100.0
    assert metrics.direct_evidence_coverage_pct == 80.0
    assert metrics.geometry_provenance_coverage_pct == 90.0
    assert metrics.graph_provenance_coverage_pct == 90.0
    # Global = 0.3*100 + 0.3*100 + 0.2*90 + 0.2*90 = 30 + 30 + 18 + 18 = 96.0
    assert metrics.global_epistemic_score == 96.0


def test_conflict_gate_unexecuted_status():
    gate = ConflictGateResult(executed=False)
    assert "CONFLICT STATUS UNKNOWN" in gate.status_summary


def test_conflict_gate_executed_status():
    gate = ConflictGateResult(executed=True, checked_entities=50, conflicts_found=3, unresolved_conflicts=0)
    assert "0 Unresolved Conflicts" in gate.status_summary


# =========================================================================
# 6. PUBLISH GATEKEEPER & MERAVIGLIA NEGATIVE REGRESSION TEST
# =========================================================================

def test_publish_gatekeeper_blocks_when_source_missing():
    gk = EvidenceGatekeeper()
    gk.register_source(SourceArtifact(
        source_id="MSC-MER-GA-2025",
        title="MSC Meraviglia GA",
        publisher="MSC",
        source_type=SourceType.OFFICIAL_PDF,
        file_path="/missing/meraviglia.pdf",
        verification_status=VerificationStatus.MISSING
    ))
    gk.set_conflict_result(ConflictGateResult(executed=False))

    res = gk.evaluate_publish_gate()
    assert res.status == PublishStatus.PUBLISH_BLOCKED
    assert any("PRIMARY_SOURCE_MISSING" in r for r in res.reasons)
    assert any("CONFLICT_DETECTION_NOT_EXECUTED" in r for r in res.reasons)


def test_publish_gatekeeper_negative_regression_meraviglia_dataset():
    """
    CRITICAL TEST: The legacy Meraviglia ingestion from commit 0ef5a21 MUST be blocked.
    """
    gk = EvidenceGatekeeper()
    
    # 1. Registered source with synthetic hash and non-existent file
    gk.register_source(SourceArtifact(
        source_id="SRC-MER-2026",
        title="MSC Meraviglia Official Deck Plans (Edition 2025/2026)",
        publisher="Chantiers de l'Atlantique",
        source_type=SourceType.OFFICIAL_PDF,
        file_path="C:/non_existent/msc_meraviglia_ga.pdf",
        sha256="9a71b283c4e512d109f8721a34bc0981e271409283741029c782109283741029"
    ))

    # 2. Fact falsely labeled as DIRECT
    gk.add_fact(FactEvidenceRecord(
        fact_id="MER-TECH-IMO",
        entity_id="msc-meraviglia",
        attribute="imo_number",
        value=9760512,
        epistemic_status=EpistemicStatus.DIRECT,
        evidence=[EvidenceLocator(source_id="SRC-MER-2026", page=1)]
    ))

    # 3. Synthetic Geometry falsely claiming DIRECT
    gk.add_geometry(GeometryProvenanceRecord(
        object_id="MER-CABIN-8001",
        deck_number=8,
        geometry_type=GeometryProvenanceType.DIRECT_SOURCE_GEOMETRY,
        source_id="SRC-MER-2026"
    ))

    # 4. Conflict detection was bypassed
    gk.set_conflict_result(ConflictGateResult(executed=False))

    # Evaluate
    gate_result = gk.evaluate_publish_gate()

    # MUST BE PUBLISH_BLOCKED
    assert gate_result.status == PublishStatus.PUBLISH_BLOCKED
    assert len(gate_result.reasons) >= 3
    assert any("PRIMARY_SOURCE_MISSING" in r for r in gate_result.reasons)
    assert any("INVALID_FACT_EPISTEMIC_STATUS" in r for r in gate_result.reasons)
    assert any("CONFLICT_DETECTION_NOT_EXECUTED" in r for r in gate_result.reasons)


# =========================================================================
# 7. REPORT LANGUAGE GUARD TESTS
# =========================================================================

def test_sanitize_report_content_replaces_fraudulent_claims_when_blocked():
    untruthful_report = "This pack has 100% verified attributes and 0 conflicts."
    blocked_result = PublishGateResult(status=PublishStatus.PUBLISH_BLOCKED, reasons=["MISSING_SOURCE"])

    sanitized = sanitize_report_content(untruthful_report, blocked_result)
    assert "100% verified" not in sanitized
    assert "0 conflicts" not in sanitized
    assert "[UNVERIFIED / BLOCKED]" in sanitized
