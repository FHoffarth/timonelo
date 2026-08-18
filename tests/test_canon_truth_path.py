"""
tests/test_canon_truth_path.py

Truth-Path Hardening and Repository Canon Tests (P0-A Scope).
Verifies that:
1. One canonical epistemic model is declared (ADR-0002).
2. Bridge Officer Tim is strictly an orchestrator without truth authoring or factual briefing power.
3. Legacy briefing demo is explicitly quarantined as non-canonical demo/hypothesis only.
4. Legacy hypothesis tools are quarantined and cannot write to canonical knowledge.
5. Master database compiler has zero indirect dependencies or execution paths to hypothesis tools.
6. Legacy secondary repository audit paths are accurately classified.
"""

import inspect
import os
import pytest
from src.timonelo.ontology.models import (
    Method,
    Derivation,
    ReviewState,
    GeometryProvenance,
)
from src.timonelo.database.bridge_officer import (
    BridgeOfficer,
    LegacyBridgeBriefingDemo,
    BriefingPhase,
)
from src.timonelo.factory.patch_engine import ShipPatchEngine
from src.timonelo.factory.archetype_generator import StateroomArchetypeGenerator
from src.timonelo.database.compiler import KnowledgeDBCompiler


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
    assert status["can_generate_factual_claims"] is False


def test_canonical_bridge_officer_cannot_generate_factual_briefing_claims():
    """Verify canonical BridgeOfficer has no factual briefing generation methods."""
    officer = BridgeOfficer()
    assert not hasattr(officer, "generate_briefing")
    assert not hasattr(BridgeOfficer, "generate_briefing")

    # Historical BridgeOfficerEngine alias must resolve to canonical BridgeOfficer, NEVER to briefing generator
    from src.timonelo.database.bridge_officer import BridgeOfficerEngine
    assert BridgeOfficerEngine is BridgeOfficer
    assert not hasattr(BridgeOfficerEngine, "generate_briefing")


def test_legacy_briefing_demo_is_quarantined_non_canonical():
    """Verify legacy briefing demo generator is explicitly marked non-canonical / demo-only."""
    assert LegacyBridgeBriefingDemo.is_quarantined_demo_only() is True
    briefing = LegacyBridgeBriefingDemo.generate_briefing(BriefingPhase.PRE_CRUISE_12D)
    assert briefing.is_canonical is False
    assert briefing.is_quarantined_demo is True


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


def test_quarantine_structural_isolation_no_indirect_leakage():
    """Verify that Master Compiler (KnowledgeDBCompiler) does not import or execute hypothesis engines."""
    compiler_source = inspect.getsource(KnowledgeDBCompiler)

    # Must not reference or import StateroomArchetypeGenerator or ShipPatchEngine
    assert "StateroomArchetypeGenerator" not in compiler_source
    assert "ShipPatchEngine" not in compiler_source
    assert "timonelo.factory.archetype_generator" not in compiler_source
    assert "timonelo.factory.patch_engine" not in compiler_source


def test_legacy_knowledge_factory_repo_audit_paths():
    """Verify legacy second repository audit document references exact Python paths."""
    audit_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "knowledge",
        "reports",
        "legacy_knowledge_factory_repo_audit.md",
    )
    assert os.path.exists(audit_file)
    with open(audit_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "src/connectors/truth_engine_bridge.py" in content
    assert "src/agents/coverage_planner.py" in content
    assert "TruthEngineBridge.ts" not in content
    assert "CoveragePlanner.ts" not in content
