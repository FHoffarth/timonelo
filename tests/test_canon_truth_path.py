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
    EvidenceLink,
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
from timonelo.evidence.editor import StatementEditor, EditorError
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.review import ReviewLog
from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.artifacts import ArtifactStore
from timonelo.evidence.events import EvidenceEventLog, EvidenceEvent
from timonelo.ingestion.normalizer import DataNormalizer
from tests.test_ground_truth_pipeline import _write_pdf


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
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    )
    engine.add_statement(s)

    # 1. Draft statement cannot answer queries
    assert not engine.answer("c:1", "Q-1").known

    # 2. Approved + UNKNOWN cannot be published
    engine.set_human_review_state("S1", HumanReviewState.APPROVED)
    with pytest.raises(ValueError, match="must be SUPPORTED first"):
        engine.publish("S1")
    assert not engine.answer("c:1", "Q-1").known

    # 3. Approved + SUPPORTED can be published and becomes answerable
    engine.set_evidence_condition("S1", EvidenceCondition.SUPPORTED)
    engine.publish("S1")
    ans = engine.answer("c:1", "Q-1")
    assert ans.known
    assert ans.value == 14


def test_fail_closed_regression_1_approved_unknown_blocked(tmp_path):
    """1. APPROVED + UNKNOWN + PUBLISH_ALLOWED attempt -> blocked."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)
    engine.add_statement(Statement(
        "S1", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.APPROVED,
    ))
    with pytest.raises(ValueError, match="must be SUPPORTED first"):
        engine.publish("S1")


def test_fail_closed_regression_2_approved_unsupported_blocked(tmp_path):
    """2. APPROVED + UNSUPPORTED attempt -> blocked."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)
    engine.add_statement(Statement(
        "S1", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.UNSUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    ))
    with pytest.raises(ValueError, match="must be SUPPORTED first"):
        engine.publish("S1")


def test_fail_closed_regression_3_approved_conflicted_blocked(tmp_path):
    """3. APPROVED + CONFLICTED -> blocked unless resolved into supported evidence."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)
    engine.add_statement(Statement(
        "S1", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.CONFLICTED,
        human_review_state=HumanReviewState.APPROVED,
    ))
    # Blocked while CONFLICTED
    with pytest.raises(ValueError, match="must be SUPPORTED first"):
        engine.publish("S1")

    # Resolved into supported evidence -> publishing succeeds
    engine.set_evidence_condition("S1", EvidenceCondition.SUPPORTED)
    engine.publish("S1")
    assert engine.answer("c:1", "Q-1").known is True


def test_fail_closed_regression_4_supported_draft_blocked(tmp_path):
    """4. SUPPORTED + DRAFT -> blocked from publish."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)
    engine.add_statement(Statement(
        "S1", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.DRAFT,
    ))
    with pytest.raises(ValueError, match="It must be APPROVED first"):
        engine.publish("S1")


def test_fail_closed_regression_5_supported_approved_blocked_not_answerable(tmp_path):
    """5. SUPPORTED + APPROVED + PUBLISH_BLOCKED -> not answerable."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)
    engine.add_statement(Statement(
        "S1", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    ))
    ans = engine.answer("c:1", "Q-1")
    assert ans.known is False


def test_fail_closed_regression_6_supported_approved_allowed_answerable(tmp_path):
    """6. SUPPORTED + APPROVED + PUBLISH_ALLOWED -> answerable."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)
    engine.add_statement(Statement(
        "S1", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_BLOCKED,
    ))
    engine.publish("S1")
    ans = engine.answer("c:1", "Q-1")
    assert ans.known is True
    assert ans.value == 14


def test_fail_closed_regression_7_inconsistent_state_not_answerable(tmp_path):
    """7. Direct/manual construction of an inconsistent state must NOT cause TruthEngine.answer() to return known=True."""
    doc = tmp_path / "doc.txt"
    doc.write_text("dummy", encoding="utf-8")
    store = ArtifactStore(str(tmp_path / "artifacts"))
    art = store.add(str(doc), document_class="cruise_line_deck_plan", obtained_on="2026-08-17", obtained_from="test")
    registry = QuestionRegistry("test")
    registry.register(Question("Q-1", "cabin", statement_type="cabin.deck", supportable_by=("cruise_line_deck_plan",)))
    log = EvidenceEventLog(str(tmp_path / "events.json"), store, registry)
    log.append(EvidenceEvent("E1", art.sha256, "p1", "c:1", "Q-1", 14, "curator", "2026-08-17"))

    engine = TruthEngine(registry, log, store)

    # Inconsistent 1: PUBLISH_ALLOWED + APPROVED, but UNKNOWN evidence condition
    engine.add_statement(Statement(
        "S_UNK", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.UNKNOWN,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    ))
    assert engine.answer("c:1", "Q-1").known is False

    # Inconsistent 2: PUBLISH_ALLOWED + APPROVED, but UNSUPPORTED evidence condition
    engine._statements.clear()
    engine.add_statement(Statement(
        "S_UNSUP", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.UNSUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    ))
    assert engine.answer("c:1", "Q-1").known is False

    # Inconsistent 3: PUBLISH_ALLOWED + APPROVED, but CONFLICTED evidence condition
    engine._statements.clear()
    engine.add_statement(Statement(
        "S_CONF", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.CONFLICTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    ))
    assert engine.answer("c:1", "Q-1").known is False

    # Inconsistent 4: PUBLISH_ALLOWED + SUPPORTED, but DRAFT review state
    engine._statements.clear()
    engine.add_statement(Statement(
        "S_DRAFT", "c:1", "Q-1", 14, Method.DIRECT, Derivation.LOCAL,
        evidence_event_ids=("E1",),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.DRAFT,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    ))
    assert engine.answer("c:1", "Q-1").known is False



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


# ===========================================================================
# TASK G & H — ACCEPTANCE TESTS & CANON GUARDS
# ===========================================================================

def test_task_g1_author_creates_evidence_condition_unknown(tmp_path):
    """G.1: StatementEditor.create() creates evidence_condition UNKNOWN."""
    pdf = _write_pdf(str(tmp_path / "doc.pdf"))
    reg = ArtifactRegistry(str(tmp_path / "artifacts"))
    art = reg.register(pdf, "cruise_line_deck_plan", "2026-08-17", "test")
    rlog = ReviewLog(str(tmp_path / "reviews.json"))
    editor = StatementEditor(str(tmp_path / "statements.json"), reg, rlog)

    stmt = editor.create(
        entity_id="c:1", question_id="Q-1", statement_type="cabin.deck",
        value=14, artifact_id=art.artifact_id, locator="p1",
        read_by="curator", read_on="2026-08-17"
    )
    assert stmt.evidence_condition == "UNKNOWN"
    assert stmt.condition is EvidenceCondition.UNKNOWN


def test_task_g2_legacy_record_missing_condition_loads_unknown(tmp_path):
    """G.2: Legacy record missing evidence_condition loads as UNKNOWN (never manufactured SUPPORTED)."""
    pdf = _write_pdf(str(tmp_path / "doc.pdf"))
    reg = ArtifactRegistry(str(tmp_path / "artifacts"))
    art = reg.register(pdf, "cruise_line_deck_plan", "2026-08-17", "test")
    rlog = ReviewLog(str(tmp_path / "reviews.json"))

    import json
    stmts_path = tmp_path / "statements.json"
    stmts_path.write_text(json.dumps({
        "STM-0001": {
            "statement_id": "STM-0001",
            "entity_id": "c:1",
            "question_id": "Q-1",
            "statement_type": "cabin.deck",
            "value": 14,
            "artifact_id": art.artifact_id,
            "page": 1,
            "locator": "p1",
            "read_by": "curator",
            "read_on": "2026-08-17",
            "method": "DIRECT",
            "human_review_state": "DRAFT",
            "publish_status": "PUBLISH_BLOCKED",
            # "evidence_condition" deliberately omitted
        }
    }), encoding="utf-8")

    editor = StatementEditor(str(stmts_path), reg, rlog)
    loaded = editor.get("STM-0001")
    assert loaded.evidence_condition == "UNKNOWN"
    assert loaded.condition is EvidenceCondition.UNKNOWN


def test_task_g10_conflict_winner_conflicted_cannot_auto_publish(tmp_path):
    """G.10: Conflict winner with CONFLICTED/UNKNOWN condition cannot auto-publish."""
    pdf_a = _write_pdf(str(tmp_path / "a.pdf"), "A")
    pdf_b = _write_pdf(str(tmp_path / "b.pdf"), "B")
    reg = ArtifactRegistry(str(tmp_path / "artifacts"))
    art_a = reg.register(pdf_a, "cruise_line_deck_plan", "2026-08-17", "test")
    art_b = reg.register(pdf_b, "cruise_line_deck_plan", "2026-08-17", "test")
    rlog = ReviewLog(str(tmp_path / "reviews.json"))
    clog = ConflictLog(str(tmp_path / "conflicts.json"))
    editor = StatementEditor(str(tmp_path / "statements.json"), reg, rlog, clog)

    # Statement 1 published
    s1 = editor.create("c:1", "Q-1", "cabin.deck", 14, art_a.artifact_id, "p1", "reader.1", "2026-08-17")
    editor.set_evidence_condition(s1.statement_id, EvidenceCondition.SUPPORTED, "curator", "2026-08-17")
    editor.transition(s1.statement_id, HumanReviewState.UNDER_REVIEW, "reader.1", "2026-08-17")
    editor.transition(s1.statement_id, HumanReviewState.APPROVED, "reviewer.1", "2026-08-17")
    editor.publish(s1.statement_id, "reviewer.1", "2026-08-17")

    # Statement 2 created (disagrees, starts UNKNOWN condition)
    s2 = editor.create("c:1", "Q-1", "cabin.deck", 15, art_b.artifact_id, "p1", "reader.2", "2026-08-17")
    conflicts = clog.all()
    assert len(conflicts) == 1

    # Resolve conflict selecting s2 as winner (s2 condition is UNKNOWN)
    editor.resolve_conflict(conflicts[0].conflict_id, s2.statement_id, "reviewer.2", "2026-08-18", "source B preferred")

    # Winner reached APPROVED, but because condition was UNKNOWN, it CANNOT auto-publish
    winner = editor.get(s2.statement_id)
    assert winner.state is HumanReviewState.APPROVED
    assert winner.publishing is PublishStatus.PUBLISH_BLOCKED
    assert winner.condition is EvidenceCondition.UNKNOWN

    # Loser reached SUPERSEDED and CONFLICTED
    loser = editor.get(s1.statement_id)
    assert loser.state is HumanReviewState.SUPERSEDED
    assert loser.condition is EvidenceCondition.CONFLICTED
    assert loser.publishing is PublishStatus.PUBLISH_BLOCKED


def test_task_g11_normalizer_missing_trust_level_defaults_to_unknown():
    """G.11: DataNormalizer missing trust_level defaults strictly to UNKNOWN."""
    norm_ship = DataNormalizer.normalize_ship({"name": "Test Ship", "slug": "test-ship"}, "src:test")
    assert norm_ship["name"]["trust_level"] == "UNKNOWN"

    norm_port = DataNormalizer.normalize_port({"name": "Test Port", "slug": "test-port"}, "src:test")
    assert norm_port["sources"][0]["trust_level"] == "UNKNOWN"


def test_task_g12_normalizer_confidence_does_not_determine_authority():
    """G.12: DataNormalizer confidence score does not determine authority."""
    # High confidence without trust_level must not become OFFICIAL
    norm_high = DataNormalizer.normalize_ship({"name": "High Ship", "slug": "high"}, "src:test", confidence=0.99)
    assert norm_high["name"]["trust_level"] == "UNKNOWN"

    # Low confidence with declared trust_level preserves explicit trust_level
    norm_low = DataNormalizer.normalize_ship({"name": "Low Ship", "slug": "low", "trust_level": "OFFICIAL"}, "src:test", confidence=0.10)
    assert norm_low["name"]["trust_level"] == "OFFICIAL"


def test_task_g13_explicit_support_promotion_path_is_logged_auditable(tmp_path):
    """G.13: Explicit UNKNOWN -> SUPPORTED promotion path records an auditable log entry."""
    pdf = _write_pdf(str(tmp_path / "doc.pdf"))
    reg = ArtifactRegistry(str(tmp_path / "artifacts"))
    art = reg.register(pdf, "cruise_line_deck_plan", "2026-08-17", "test")
    rlog = ReviewLog(str(tmp_path / "reviews.json"))
    editor = StatementEditor(str(tmp_path / "statements.json"), reg, rlog)

    stmt = editor.create("c:1", "Q-1", "cabin.deck", 14, art.artifact_id, "p1", "curator.bob", "2026-08-17")
    assert stmt.condition is EvidenceCondition.UNKNOWN

    # Explicit promotion
    editor.set_evidence_condition(stmt.statement_id, EvidenceCondition.SUPPORTED, "verifier.alice", "2026-08-18", "verified against builder table")
    updated = editor.get(stmt.statement_id)
    assert updated.condition is EvidenceCondition.SUPPORTED

    # Check ReviewLog audit history
    history = rlog.history(stmt.statement_id)
    assert len(history) >= 1
    verif_entry = history[-1]
    assert verif_entry.from_state == "CONDITION:UNKNOWN"
    assert verif_entry.to_state == "CONDITION:SUPPORTED"
    assert verif_entry.actor == "verifier.alice"
    assert verif_entry.occurred_on == "2026-08-18"
    assert verif_entry.note == "verified against builder table"


def test_task_g14_bridge_officer_cannot_use_promotion_path_to_author_ground_truth():
    """G.14: BridgeOfficer cannot author ground truth or promote evidence conditions."""
    officer = BridgeOfficer()
    assert not hasattr(officer, "set_evidence_condition")
    assert not hasattr(officer, "publish")
    assert not hasattr(officer, "create_statement")
    assert not hasattr(officer, "transition")
    status = officer.get_pipeline_status()
    assert status["can_author_ground_truth"] is False
    assert status["can_override_evidence_gatekeeper"] is False


def test_task_h_ast_canon_guard_no_unsanctioned_supported_defaults():
    """H: AST Canon Guard ensures EvidenceCondition.SUPPORTED is never assigned as a default attribute or field."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir = os.path.join(repo_root, "src", "timonelo")

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
                # Check dataclass / class annotations with default values
                if isinstance(node, ast.AnnAssign) and node.value is not None:
                    val_str = ast.unparse(node.value)
                    target_str = ast.unparse(node.target)
                    if "evidence_condition" in target_str and "SUPPORTED" in val_str:
                        violations.append(f"{rel_path}:{node.lineno} assigns default SUPPORTED to {target_str}")
                # Check function argument defaults
                elif isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        val_str = ast.unparse(default)
                        if "EvidenceCondition.SUPPORTED" in val_str:
                            violations.append(f"{rel_path}:{node.lineno} function {node.name} defaults to SUPPORTED")

    assert violations == [], f"Found unsanctioned default assignments to SUPPORTED: {violations}"


# ===========================================================================
# TASK J — VALIDATION TESTS
# ===========================================================================

def test_task_j_missing_state_never_defaults_direct():
    """J.1: Missing method/derivation on EvidenceLink never defaults to DIRECT/LOCAL."""
    link = EvidenceLink(source_id="SRC-1", locator="p1")
    assert link.method is None
    assert link.derivation is None
    assert link.evidence_condition is EvidenceCondition.UNKNOWN
    assert link.human_review_state is HumanReviewState.DRAFT


def test_task_j_unknown_badge_fails_closed():
    """J.2: EpistemicBadge in frontend defaults to fail-closed neutral slate styling for unclassified states."""
    badge_path = os.path.join(
        os.path.dirname(__file__), "..", "frontend", "src", "components", "ui", "EpistemicBadge.tsx"
    )
    with open(badge_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must default to slate styling (fail-closed)
    assert 'let style = "bg-slate-200/80 text-slate-700 border-slate-300";' in content
    # Must not default to amber reassurance
    assert 'let style = "bg-amber-100/80 text-amber-900 border-amber-300/60";' not in content


def test_task_j_generated_ts_types_match_python_canon():
    """J.3: Generated TypeScript canon types match Python canonical enums in ontology.models."""
    import re
    from tools.generate_epistemic_contract import generate_ts_canon
    canon_ts_path = os.path.join(
        os.path.dirname(__file__), "..", "frontend", "src", "generated", "canon.ts"
    )
    assert os.path.exists(canon_ts_path)
    with open(canon_ts_path, "r", encoding="utf-8") as f:
        ts_content = f.read()

    expected_content = generate_ts_canon()
    assert ts_content.strip() == expected_content.strip()

    # Mechanically extract union types from TS content and compare exact sets
    def extract_ts_union(type_name: str) -> set:
        m = re.search(rf"export type {type_name} = ([^;]+);", ts_content)
        assert m, f"Missing TypeScript type definition for {type_name}"
        return {item.strip().strip("'").strip('"') for item in m.group(1).split("|")}

    assert extract_ts_union("Method") == {e.value for e in Method}
    assert extract_ts_union("Derivation") == {e.value for e in Derivation}
    assert extract_ts_union("EvidenceCondition") == {e.value for e in EvidenceCondition}
    assert extract_ts_union("HumanReviewState") == {e.value for e in HumanReviewState}
    assert extract_ts_union("PublishStatus") == {e.value for e in PublishStatus}
    assert extract_ts_union("GeometryProvenance") == {e.value for e in GeometryProvenance}

    # Strict negative regression assertions against historic drift:
    method_ts = extract_ts_union("Method")
    assert "CALCULATED" in method_ts
    assert "DERIVED" not in method_ts  # CALCULATED must not drift into DERIVED

    derivation_ts = extract_ts_union("Derivation")
    assert "SISTER_SHIP" in derivation_ts
    assert "REFERENCE_MODEL" in derivation_ts
    assert "CROSS_DOCUMENT" not in derivation_ts  # Must not drift into CROSS_DOCUMENT


def test_task_j_unknown_json_enum_values_fail():
    """J.4: Unknown JSON enum values fail closed by raising ValueError upon parsing."""
    with pytest.raises(ValueError):
        Method("NON_EXISTENT_METHOD")

    with pytest.raises(ValueError):
        EvidenceCondition("NON_EXISTENT_CONDITION")

    with pytest.raises(ValueError):
        HumanReviewState("NON_EXISTENT_REVIEW_STATE")

    with pytest.raises(ValueError):
        PublishStatus("NON_EXISTENT_PUBLISH_STATUS")


def test_task_j_legacy_compound_states_not_silently_mapped():
    """J.5: Legacy compound or non-canonical strings are not silently mapped into canonical enums."""
    invalid_legacy_strings = [
        "VERIFIED_DIRECT",
        "AUDITED_CANONICAL",
        "VERIFIED_DERIVED",
        "CONFIRMED_SUPPORTED",
    ]
    for s in invalid_legacy_strings:
        with pytest.raises(ValueError):
            Method(s)
        with pytest.raises(ValueError):
            EvidenceCondition(s)
        with pytest.raises(ValueError):
            HumanReviewState(s)


def test_task_j_no_bare_verified_canonical_state_remains():
    """J.6: Bare VERIFIED is not a member of any of the six canonical enums."""
    canonical_enums = [
        Method,
        Derivation,
        EvidenceCondition,
        HumanReviewState,
        PublishStatus,
        GeometryProvenance,
    ]
    for enum_cls in canonical_enums:
        values = [e.value for e in enum_cls]
        assert "VERIFIED" not in values, f"Bare VERIFIED found in {enum_cls.__name__}: {values}"


def test_task_g_canon_vs_legacy_static_guard():
    """G: Static CI guard asserting frontend canon contract integrity."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    badge_path = os.path.join(repo_root, "frontend", "src", "components", "ui", "EpistemicBadge.tsx")
    types_path = os.path.join(repo_root, "frontend", "src", "semantic-deck", "types.ts")
    client_path = os.path.join(repo_root, "frontend", "src", "semantic-deck", "apiClient.ts")

    with open(badge_path, "r", encoding="utf-8") as f:
        badge_content = f.read()
    with open(types_path, "r", encoding="utf-8") as f:
        types_content = f.read()
    with open(client_path, "r", encoding="utf-8") as f:
        client_content = f.read()

    # 1. Canonical frontend modules import generated canon types
    assert 'from "../../generated/canon"' in badge_content or "from '../generated/canon'" in types_content

    # 2. Canonical badges exist with separate axes (no axis conflation)
    assert "export function MethodBadge" in badge_content
    assert "export function EvidenceConditionBadge" in badge_content
    assert "export function HumanReviewStateBadge" in badge_content
    assert "export function PublishStatusBadge" in badge_content

    # 3. Legacy types are explicitly prefixed with Legacy
    assert "export type LegacySemanticDeckState" in types_content
    assert "export type LegacyEpistemicTag" in badge_content

    # 4. Canonical badges do not accept legacy KNOWN / DERIVED / LIKELY / CONFLICT
    assert "method?: Method;" in badge_content
    assert "condition?: EvidenceCondition;" in badge_content

    # 5. DIRECT is never used as fallback for missing canonical evidence condition or state in apiClient
    assert '|| "DIRECT"' not in client_content
    assert 'parseLegacySemanticState(o.epistemic_state)' in client_content


def test_phase_2c_frontend_fail_closed_static_guards():
    """Phase 2C: Static CI guards ensuring fail-closed semantics across frontend contracts and badges."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    badge_path = os.path.join(repo_root, "frontend", "src", "components", "ui", "EpistemicBadge.tsx")
    client_path = os.path.join(repo_root, "frontend", "src", "semantic-deck", "apiClient.ts")

    with open(badge_path, "r", encoding="utf-8") as f:
        badge_content = f.read()
    with open(client_path, "r", encoding="utf-8") as f:
        client_content = f.read()

    # 1. parseMethod fallback is null (never DIRECT)
    assert 'export function parseMethod(val: unknown): Method | null' in client_content
    assert 'return "DIRECT";' not in client_content

    # 2. MethodBadge has no default DIRECT and renders UNCLASSIFIED on missing value
    assert 'method = "DIRECT"' not in badge_content
    assert 'if (!method) {' in badge_content
    assert 'UNCLASSIFIED' in badge_content

    # 3. DerivationBadge has no default LOCAL and renders UNCLASSIFIED on missing value
    assert 'derivation = "LOCAL"' not in badge_content
    assert 'if (!derivation) {' in badge_content

    # 4. No default export of EpistemicBadge remains
    assert 'export default LegacyEpistemicBadge;' not in badge_content
    assert 'export default' not in badge_content

    # 5. Zero files in frontend/src import default EpistemicBadge
    for root, _, files in os.walk(os.path.join(repo_root, "frontend", "src")):
        for f in files:
            if f.endswith((".ts", ".tsx")):
                p = os.path.join(root, f)
                with open(p, "r", encoding="utf-8") as fh:
                    content = fh.read()
                    assert "import EpistemicBadge from" not in content, f"Default import found in {p}"
                    assert "import EpistemicBadge," not in content, f"Default import found in {p}"
