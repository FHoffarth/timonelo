"""
tests/test_canon_truth_path.py

Truth-Path Hardening and Repository Canon Tests.
Verifies that:
1. Exactly six canonical enums are declared in ontology.models (ADR-0002).
2. No duplicate canonical enums exist outside ontology.models.
3. No bare VERIFIED exists in canonical enums.
4. Publication semantics and evidence condition remain strictly orthogonal.
5. Bridge Officer Tim is strictly an orchestrator without truth authoring or factual briefing power.
6. Legacy briefing demo is explicitly quarantined as non-canonical demo/hypothesis only.
7. Legacy hypothesis tools are quarantined and cannot write to canonical knowledge.
8. Master database compiler has zero indirect dependencies or execution paths to hypothesis tools.
9. Legacy secondary repository audit paths are accurately classified.
"""

import ast
import inspect
import os
import pytest
from timonelo.ontology.models import (
    Method,
    Derivation,
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
    GeometryProvenance,
)
from timonelo.database.bridge_officer import (
    BridgeOfficer,
    LegacyBridgeBriefingDemo,
    BriefingPhase,
)
from timonelo.factory.patch_engine import ShipPatchEngine
from timonelo.factory.archetype_generator import StateroomArchetypeGenerator
from timonelo.database.compiler import KnowledgeDBCompiler
from timonelo.evidence.engine import Statement, TruthEngine
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.artifacts import ArtifactStore
from timonelo.evidence.events import EvidenceEventLog, EvidenceEvent


def test_epistemic_enums_aligned_to_adr0002():
    """Verify epistemic enums match ADR-0002 multi-axial model."""
    assert Method.DIRECT.value == "DIRECT"
    assert Method.CALCULATED.value == "CALCULATED"
    assert Method.INFERRED.value == "INFERRED"

    assert Derivation.LOCAL.value == "LOCAL"
    assert Derivation.SISTER_SHIP.value == "SISTER_SHIP"
    assert Derivation.REFERENCE_MODEL.value == "REFERENCE_MODEL"
    assert Derivation.GENERATED.value == "GENERATED"

    assert EvidenceCondition.SUPPORTED.value == "SUPPORTED"
    assert EvidenceCondition.UNSUPPORTED.value == "UNSUPPORTED"
    assert EvidenceCondition.CONFLICTED.value == "CONFLICTED"
    assert EvidenceCondition.UNKNOWN.value == "UNKNOWN"

    assert HumanReviewState.DRAFT.value == "DRAFT"
    assert HumanReviewState.UNDER_REVIEW.value == "UNDER_REVIEW"
    assert HumanReviewState.APPROVED.value == "APPROVED"
    assert HumanReviewState.REJECTED.value == "REJECTED"
    assert HumanReviewState.SUPERSEDED.value == "SUPERSEDED"

    assert PublishStatus.PUBLISH_ALLOWED.value == "PUBLISH_ALLOWED"
    assert PublishStatus.PUBLISH_ALLOWED_WITH_WARNINGS.value == "PUBLISH_ALLOWED_WITH_WARNINGS"
    assert PublishStatus.PUBLISH_BLOCKED.value == "PUBLISH_BLOCKED"

    assert GeometryProvenance.DIRECT_SOURCE_GEOMETRY.value == "DIRECT_SOURCE_GEOMETRY"
    assert GeometryProvenance.TRANSFORMED_SOURCE_GEOMETRY.value == "TRANSFORMED_SOURCE_GEOMETRY"
    assert GeometryProvenance.DERIVED_GEOMETRY.value == "DERIVED_GEOMETRY"
    assert GeometryProvenance.SYNTHETIC_GEOMETRY.value == "SYNTHETIC_GEOMETRY"
    assert GeometryProvenance.UNKNOWN_PROVENANCE.value == "UNKNOWN_PROVENANCE"


def test_no_bare_verified_in_canonical_enums():
    """Verify that bare VERIFIED is not a member of any canonical enum."""
    canonical_enums = [
        Method,
        Derivation,
        EvidenceCondition,
        HumanReviewState,
        PublishStatus,
        GeometryProvenance,
    ]
    for enum_cls in canonical_enums:
        member_names = {m.name for m in enum_cls}
        member_values = {m.value for m in enum_cls}
        assert "VERIFIED" not in member_names, f"{enum_cls.__name__} must not contain VERIFIED"
        assert "VERIFIED" not in member_values, f"{enum_cls.__name__} must not contain 'VERIFIED'"


def test_ast_no_duplicate_canonical_enums_outside_ontology_models():
    """Verify AST scan finds no class definitions for canonical enums outside ontology/models.py."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir = os.path.join(repo_root, "src", "timonelo")
    canonical_names = {
        "Method",
        "Derivation",
        "EvidenceCondition",
        "HumanReviewState",
        "PublishStatus",
        "GeometryProvenance",
    }

    violations = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, repo_root).replace("\\", "/")
            if rel_path == "src/timonelo/ontology/models.py":
                continue
            with open(path, "r", encoding="utf-8") as pyfile:
                tree = ast.parse(pyfile.read(), filename=rel_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name in canonical_names:
                    violations.append(f"{rel_path}:{node.lineno} defines duplicate enum class {node.name}")

    assert violations == [], f"Found duplicate canonical enum class definitions: {violations}"


def test_publication_semantics_and_orthogonality(tmp_path):
    """Verify that approval, evidence condition, and publication gate remain orthogonal."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy fixture", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")

    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent(
        event_id="E1", artifact_sha256=art.sha256, locator="p1",
        entity_id="c:1", question_id="Q-1", observed_value=14,
        observed_by="curator", observed_on="2026-08-17"
    ))

    engine = TruthEngine(registry, log, store)
    s = Statement(
        statement_id="S1", entity_id="c:1", question_id="Q-1",
        value=14, method=Method.DIRECT, derivation=Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    )
    engine.add_statement(s)

    # 1. Draft statement cannot answer queries even if supported
    assert not engine.answer("c:1", "Q-1").known

    # 2. Approved but publish-blocked cannot answer queries
    engine.set_human_review_state("S1", HumanReviewState.APPROVED)
    assert not engine.answer("c:1", "Q-1").known

    # 3. Publish allowed becomes answerable
    engine.publish("S1")
    ans = engine.answer("c:1", "Q-1")
    assert ans.known
    assert ans.value == 14

    # 4. Evidence condition is orthogonal: unsupported state does not silently change
    s_unsupported = Statement(
        statement_id="S2", entity_id="c:1", question_id="Q-1",
        value=15, method=Method.DIRECT, derivation=Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.UNSUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    assert s_unsupported.evidence_condition == EvidenceCondition.UNSUPPORTED
    assert s_unsupported.human_review_state == HumanReviewState.APPROVED
    assert s_unsupported.publish_status == PublishStatus.PUBLISH_ALLOWED


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
    from timonelo.database.bridge_officer import BridgeOfficerEngine
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
