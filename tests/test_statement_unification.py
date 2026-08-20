"""Focused invariants for the canonical Statement representation."""

from __future__ import annotations

import ast
from pathlib import Path

from timonelo.evidence import authority
from timonelo.evidence.editor import Statement as EditorStatement
from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.engine import Statement as EngineStatement
from timonelo.evidence.gatekeeper import EvidenceGatekeeper
from timonelo.evidence.models import Statement
from timonelo.evidence.registry import ArtifactRegistry
from timonelo.evidence.review import ReviewLog
from timonelo.ontology.models import EvidenceCondition, Method


def test_all_production_paths_share_one_statement_type():
    assert EditorStatement is Statement
    assert EngineStatement is Statement


def test_editor_preserves_explicit_evidence_event_identity(tmp_path, monkeypatch):
    document_class = "statement_unification_fixture"
    statement_type = "fixture.statement"
    monkeypatch.setitem(
        authority.DOCUMENT_CLASSES,
        document_class,
        authority.DocumentClass(
            document_class,
            "Statement unification fixture",
            0.8,
            authority.ValidityScope.STRUCTURAL,
            authority.Acquisition.PUBLIC,
            authority.UsePermission.CITE_AND_STORE,
        ),
    )
    monkeypatch.setitem(authority.AUTHORITY, statement_type, (document_class,))

    source = tmp_path / "source.pdf"
    source.write_bytes(b"canonical statement fixture")
    registry = ArtifactRegistry(str(tmp_path / "registry"))
    artifact = registry.register(
        path=str(source),
        document_class=document_class,
        acquired_on="2026-08-20",
        acquisition_method="test",
    )
    editor = StatementEditor(
        str(tmp_path / "statements.json"),
        registry,
        ReviewLog(str(tmp_path / "reviews.json")),
    )

    statement = editor.create(
        entity_id="fixture:1",
        question_id="Q-FIXTURE",
        statement_type=statement_type,
        value="observed",
        artifact_id=artifact.artifact_id,
        locator="page:1",
        read_by="fixture-reader",
        read_on="2026-08-20",
        method=Method.DIRECT,
        evidence_event_ids=("EVT-EXPLICIT",),
    )

    assert type(statement) is Statement
    assert statement.evidence_event_ids == ("EVT-EXPLICIT",)
    assert statement.to_dict()["evidence_event_ids"] == ["EVT-EXPLICIT"]
    assert editor.get(statement.statement_id) is statement


def test_gatekeeper_retains_the_same_statement_object():
    statement = Statement(
        statement_id="STM-IDENTITY",
        entity_id="fixture:1",
        question_id="Q-FIXTURE",
        value="observed",
        evidence_event_ids=("EVT-1",),
        evidence_condition=EvidenceCondition.SUPPORTED,
    )
    gatekeeper = EvidenceGatekeeper()

    gatekeeper.add_statement(statement)

    assert gatekeeper._statements[0] is statement


def test_canonical_statement_round_trips_serialized_types():
    original = Statement(
        statement_id="STM-ROUNDTRIP",
        entity_id="fixture:1",
        question_id="Q-FIXTURE",
        value={"deck": 14},
        evidence_event_ids=("EVT-1", "EVT-2"),
        input_statement_ids=("STM-INPUT",),
        evidence_condition=EvidenceCondition.SUPPORTED,
    )

    restored = Statement(**original.to_dict())

    assert restored == original
    assert restored.method is Method.DIRECT
    assert restored.evidence_condition is EvidenceCondition.SUPPORTED


def test_canonical_statement_validity_window_is_preserved():
    statement = Statement(
        statement_id="STM-VALIDITY",
        entity_id="fixture:1",
        question_id="Q-FIXTURE",
        value="observed",
        valid_from="2026-08-01",
        valid_until="2026-08-31",
    )

    assert not statement.is_valid_at("2026-07-31")
    assert statement.is_valid_at("2026-08-01")
    assert statement.is_valid_at("2026-08-31")
    assert not statement.is_valid_at("2026-09-01")
    assert statement.is_valid_at(None)


def test_duplicate_models_and_positional_meraviglia_linkage_cannot_return():
    repository_root = Path(__file__).parents[1]
    evidence_root = repository_root / "src" / "timonelo" / "evidence"
    for module_name in ("editor.py", "engine.py"):
        tree = ast.parse((evidence_root / module_name).read_text(encoding="utf-8"))
        local_statement_classes = [
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "Statement"
        ]
        assert local_statement_classes == []

    ingestion_source = (
        repository_root / "scripts" / "reingest_msc_meraviglia_official_deckplan.py"
    ).read_text(encoding="utf-8")
    assert "EngineStatement" not in ingestion_source
    assert "zip(statements, events)" not in ingestion_source
