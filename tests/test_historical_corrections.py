"""P0-B Slice B correction-history and gatekeeper behavior."""

import json
import pytest

from timonelo.evidence.conflicts import ConflictLog
from timonelo.evidence.corrections import (
    CorrectionKind,
    HistoricalCorrectionLog,
    HistoricalCorrectionRecord,
    PriorRepresentation,
    ReferenceIntegrity,
)
from timonelo.evidence.gatekeeper import EvidenceGatekeeper
from timonelo.evidence.models import Statement
from timonelo.ontology.models import (
    EvidenceCondition,
    HumanReviewState,
    PublishStatus,
)


def test_historical_correction_records_statement_identity_without_live_conflict(tmp_path):
    corrections = HistoricalCorrectionLog(str(tmp_path / "corrections.json"))
    conflicts = ConflictLog(str(tmp_path / "conflicts.json"))
    statements = (
        Statement(
            statement_id="STM-0001",
            entity_id="ship:1",
            question_id="Q-CABINS",
            value=2244,
            evidence_condition=EvidenceCondition.UNKNOWN,
            human_review_state=HumanReviewState.DRAFT,
            publish_status=PublishStatus.PUBLISH_BLOCKED,
        ),
        Statement(
            statement_id="STM-0002",
            entity_id="ship:1",
            question_id="Q-CABINS",
            value=2214,
            evidence_condition=EvidenceCondition.SUPPORTED,
            human_review_state=HumanReviewState.APPROVED,
            publish_status=PublishStatus.PUBLISH_ALLOWED,
        ),
    )
    lifecycle_axes_before = [
        (statement.condition, statement.state, statement.publishing)
        for statement in statements
    ]

    record = corrections.record(
        entity_id="ship:1",
        question_id="Q-CABINS",
        prior_representation=PriorRepresentation.STATEMENT,
        prior_statement_id="STM-0001",
        replacement_statement_id="STM-0002",
        correction_kind=CorrectionKind.VALUE_CORRECTED,
        basis="Previous extraction error corrected from the source table.",
        evidence_event_ids=("EVT-0002",),
        recorded_at="2026-08-20T12:00:00Z",
        recorded_by="curator.alice",
    )

    assert record.prior_statement_id == "STM-0001"
    assert record.replacement_statement_id == "STM-0002"
    assert record.reference_integrity is ReferenceIntegrity.UNVALIDATED
    assert record.prior_representation is PriorRepresentation.STATEMENT
    assert len(corrections) == 1
    assert len(conflicts) == 0
    assert len(statements) == 2  # recording did not fabricate an incumbent Statement
    assert [
        (statement.condition, statement.state, statement.publishing)
        for statement in statements
    ] == lifecycle_axes_before


def test_correction_history_round_trips_as_auditable_json(tmp_path):
    path = tmp_path / "corrections.json"
    log = HistoricalCorrectionLog(str(path))
    expected = log.record(
        entity_id="ship:1",
        question_id="Q-NAME",
        correction_kind=CorrectionKind.VALUE_CORRECTED,
        basis="Source spelling corrected.",
        evidence_event_ids=("EVT-1",),
        prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
        replacement_statement_id="STM-NEW",
        recorded_at="2026-08-20T12:00:00Z",
        note="Historical representation only.",
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    restored = HistoricalCorrectionLog(str(path)).get(expected.correction_id)

    assert payload["corrections"][expected.correction_id] == expected.to_dict()
    assert restored == expected
    assert restored.reference_integrity is ReferenceIntegrity.UNVALIDATED


def test_validated_correction_state_persists_across_reload(tmp_path):
    path = tmp_path / "corrections.json"
    log = HistoricalCorrectionLog(str(path))
    record = log.record(
        entity_id="ship:1",
        question_id="Q-1",
        correction_kind=CorrectionKind.VALUE_CORRECTED,
        basis="Held source corrected the representation.",
        evidence_event_ids=("EVT-REAL",),
        prior_representation=PriorRepresentation.STATEMENT,
        prior_statement_id="STM-OLD",
        replacement_statement_id="STM-NEW",
        recorded_at="2026-08-20",
        known_statement_ids={"STM-OLD", "STM-NEW"},
        known_evidence_event_ids={"EVT-REAL"},
    )

    assert record.reference_integrity is ReferenceIntegrity.VALIDATED
    restored = HistoricalCorrectionLog(str(path)).get(record.correction_id)
    assert restored.reference_integrity is ReferenceIntegrity.VALIDATED
    assert restored.to_dict()["reference_integrity"] == "VALIDATED"
    assert "references_validated" not in restored.to_dict()


def test_partial_reference_validation_remains_explicitly_unvalidated(tmp_path):
    path = tmp_path / "corrections.json"
    record = HistoricalCorrectionLog(str(path)).record(
        entity_id="ship:1",
        question_id="Q-1",
        correction_kind=CorrectionKind.VALUE_CORRECTED,
        basis="Correction with only one reference category checked.",
        evidence_event_ids=("EVT-UNCHECKED",),
        prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
        replacement_statement_id="STM-REAL",
        recorded_at="2026-08-20",
        known_statement_ids={"STM-REAL"},
    )

    assert record.reference_integrity is ReferenceIntegrity.UNVALIDATED
    assert HistoricalCorrectionLog(str(path)).get(
        record.correction_id
    ).reference_integrity is ReferenceIntegrity.UNVALIDATED


def test_gatekeeper_preserves_not_run_for_fresh_empty_conflict_log(tmp_path):
    gatekeeper = EvidenceGatekeeper()
    not_run = gatekeeper.evaluate_publish_gate()
    assert not_run.conflict_gate.executed is False
    assert "CONFLICT_DETECTION_NOT_EXECUTED" in not_run.reasons

    conflict_log = ConflictLog(str(tmp_path / "conflicts.json"))
    gatekeeper.use_conflict_log(conflict_log)
    still_not_run = gatekeeper.evaluate_publish_gate()
    assert still_not_run.conflict_gate.executed is False


def test_correction_reference_validation_rejects_dangling_ids(tmp_path):
    corrections = HistoricalCorrectionLog(str(tmp_path / "corrections.json"))
    with pytest.raises(ValueError, match="unknown Statement IDs"):
        corrections.record(
            entity_id="ship:1",
            question_id="Q-1",
            correction_kind=CorrectionKind.VALUE_CORRECTED,
            basis="Correction from held source.",
            evidence_event_ids=("EVT-MISSING",),
            prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
            replacement_statement_id="STM-MISSING",
            recorded_at="2026-08-20",
            known_statement_ids={"STM-REAL"},
            known_evidence_event_ids={"EVT-REAL"},
        )

    with pytest.raises(ValueError, match="unknown EvidenceEvent IDs"):
        corrections.record(
            entity_id="ship:1",
            question_id="Q-1",
            correction_kind=CorrectionKind.VALUE_CORRECTED,
            basis="Correction from held source.",
            evidence_event_ids=("EVT-MISSING",),
            prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
            replacement_statement_id="STM-REAL",
            recorded_at="2026-08-20",
            known_statement_ids={"STM-REAL"},
            known_evidence_event_ids={"EVT-REAL"},
        )

    with pytest.raises(ValueError, match="unknown Statement IDs"):
        corrections.record(
            entity_id="ship:1",
            question_id="Q-1",
            correction_kind=CorrectionKind.VALUE_CORRECTED,
            basis="Correction from held source.",
            evidence_event_ids=("EVT-REAL",),
            prior_representation=PriorRepresentation.STATEMENT,
            prior_statement_id="STM-PRIOR-MISSING",
            replacement_statement_id="STM-REAL",
            recorded_at="2026-08-20",
            known_statement_ids={"STM-REAL"},
            known_evidence_event_ids={"EVT-REAL"},
        )


def test_value_corrected_requires_a_replacement_statement(tmp_path):
    """A corrected value that no Statement carries is not answerable knowledge."""
    corrections = HistoricalCorrectionLog(str(tmp_path / "corrections.json"))
    with pytest.raises(ValueError, match="requires replacement_statement_id"):
        corrections.record(
            entity_id="ship:1",
            question_id="Q-1",
            correction_kind=CorrectionKind.VALUE_CORRECTED,
            basis="Corrected from the held source.",
            evidence_event_ids=("EVT-1",),
            prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
            recorded_at="2026-08-20",
        )


def test_prior_representation_must_match_prior_statement_id(tmp_path):
    """The null prior must be declared, never merely omitted."""
    corrections = HistoricalCorrectionLog(str(tmp_path / "corrections.json"))
    common = dict(
        entity_id="ship:1",
        question_id="Q-1",
        correction_kind=CorrectionKind.VALUE_CORRECTED,
        basis="Corrected from the held source.",
        evidence_event_ids=("EVT-1",),
        replacement_statement_id="STM-NEW",
        recorded_at="2026-08-20",
    )
    with pytest.raises(ValueError, match="requires prior_statement_id"):
        corrections.record(prior_representation=PriorRepresentation.STATEMENT, **common)
    with pytest.raises(ValueError, match="forbids prior_statement_id"):
        corrections.record(
            prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
            prior_statement_id="STM-OLD",
            **common,
        )


def test_nothing_to_validate_is_distinct_from_validated(tmp_path):
    """The state the old boolean collapsed: checking requested, nothing to check.

    Unreachable for VALUE_CORRECTED, which always carries a replacement, so it is
    exercised directly on the record to keep the distinction honest and visible.
    """
    record = HistoricalCorrectionRecord(
        correction_id="COR-9999",
        entity_id="ship:1",
        question_id="Q-1",
        correction_kind=CorrectionKind.VALUE_CORRECTED,
        basis="b",
        evidence_event_ids=(),
        recorded_at="2026-08-20",
        prior_representation=PriorRepresentation.LEGACY_NON_STATEMENT,
        reference_integrity=ReferenceIntegrity.NOTHING_TO_VALIDATE,
    )
    assert record.reference_integrity is not ReferenceIntegrity.VALIDATED
    assert record.to_dict()["reference_integrity"] == "NOTHING_TO_VALIDATE"


def test_superseded_boolean_shape_is_refused_not_guessed(tmp_path):
    """`references_validated: true` is untranslatable, so loading fails closed."""
    path = tmp_path / "corrections.json"
    path.write_text(json.dumps({"corrections": {"COR-0001": {
        "correction_id": "COR-0001", "entity_id": "ship:1", "question_id": "Q-1",
        "prior_statement_id": None, "replacement_statement_id": "STM-NEW",
        "correction_kind": "VALUE_CORRECTED", "basis": "b",
        "evidence_event_ids": [], "note": "", "recorded_at": "2026-08-20",
        "recorded_by": None, "references_validated": True,
    }}}), encoding="utf-8")
    with pytest.raises(ValueError, match="superseded 'references_validated' boolean"):
        HistoricalCorrectionLog(str(path))
