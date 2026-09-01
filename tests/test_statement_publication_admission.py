"""
Guards the statement publication boundary.

The defect: `StatementEditor.set_evidence_condition` accepts SUPPORTED as a
bare caller assertion, and `publish()` then checked only that the axes said
SUPPORTED and APPROVED. A statement with zero evidence could therefore be
published and persisted, while `EvidenceGatekeeper.evaluate_publish_gate`
refused the identical object with STATEMENT_ZERO_EVIDENCE_EVENTS. Two routes to
truth disagreed, and the weaker one wrote to disk.

These tests pin the convergence: unsupported claims must not become truth
through any route, and a genuinely backed statement must still publish.

Nothing here monkeypatches the gate. The positive fixture registers a real
evidence event against a real held artifact and publishes end to end.
"""

from __future__ import annotations

import json
import pathlib
import shutil

import pytest

from timonelo.evidence.editor import EditorError
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.gatekeeper import (
    EvidenceGatekeeper,
    is_canonical_statement_admitted,
)
from timonelo.evidence.models import (
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
    Statement,
)
from timonelo.evidence.publication import (
    PublicationRejection,
    StatementPublicationError,
    evaluate_statement_publication_admission,
    PublicationAuthority,
    require_statement_publication_admission,
)
from timonelo.evidence.workspace import Workspace

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
REAL_EVIDENCE = REPO_ROOT / "evidence"

#: A real, held, publicly re-verifiable artifact and a question it may answer.
HELD_ARTIFACT = "ART-0004"
ELIGIBLE_QUESTION = "Q-0024"
ELIGIBLE_TYPE = "port.official_name"
#: Registered, but its bytes are deliberately not held.
PRIVATE_ARTIFACT = "ART-0007"
PRIVATE_QUESTION = "Q-0030"
PRIVATE_TYPE = "voyage.vessel"


@pytest.fixture()
def workspace(tmp_path) -> Workspace:
    """An isolated copy of the real evidence store; never mutates the repo."""
    root = tmp_path / "evidence"
    shutil.copytree(REAL_EVIDENCE, root)
    return Workspace(str(root))


def _draft(ws: Workspace, *, entity: str = "port:unlocode:ESBCN", **overrides) -> Statement:
    kwargs = dict(
        entity_id=entity,
        question_id=ELIGIBLE_QUESTION,
        statement_type=ELIGIBLE_TYPE,
        value="Test Value",
        artifact_id=HELD_ARTIFACT,
        page=1,
        locator="Test locator naming a real place in the document",
        read_by="curator.one",
        read_on="2026-08-31",
    )
    kwargs.update(overrides)
    return ws.editor.create(**kwargs)


def _approve(ws: Workspace, statement_id: str) -> None:
    """Walk the real review workflow to SUPPORTED + APPROVED."""
    ws.editor.set_evidence_condition(
        statement_id, EvidenceCondition.SUPPORTED,
        actor="curator.one", occurred_on="2026-08-31",
    )
    ws.editor.transition(
        statement_id, HumanReviewState.UNDER_REVIEW,
        actor="curator.one", occurred_on="2026-08-31",
    )
    ws.editor.transition(
        statement_id, HumanReviewState.APPROVED,
        actor="curator.one", occurred_on="2026-08-31",
    )


def _publish(ws: Workspace, statement_id: str) -> Statement:
    return ws.editor.publish(
        statement_id, actor="curator.two", occurred_on="2026-08-31",
    )


def _attach_real_event(ws: Workspace, statement_id: str, *, event_id: str = "EVT-TEST-0001") -> Statement:
    """Record a genuine evidence event against a real held artifact."""
    artifact = ws.registry.get(HELD_ARTIFACT)
    ws.events.append(EvidenceEvent(
        event_id=event_id,
        artifact_sha256=artifact.sha256,
        locator="Official terminals directory, terminal name heading",
        entity_id="port:unlocode:ESBCN",
        question_id=ELIGIBLE_QUESTION,
        observed_value="Test Value",
        observed_by="curator.one",
        observed_on="2026-08-31",
    ))
    from dataclasses import replace
    current = ws.editor.get(statement_id)
    updated = replace(current, evidence_event_ids=(event_id,))
    ws.editor._by_id[statement_id] = updated
    return updated


# -- 1. the reproduced defect, now closed -----------------------------------

def test_zero_evidence_statement_cannot_be_published(workspace):
    """The exact defect: caller asserts SUPPORTED, nothing backs it."""
    stmt = _draft(workspace)
    assert stmt.evidence_event_ids == ()
    _approve(workspace, stmt.statement_id)

    # The axes now say SUPPORTED + APPROVED purely because a caller said so.
    staged = workspace.editor.get(stmt.statement_id)
    assert staged.evidence_condition is EvidenceCondition.SUPPORTED
    assert staged.human_review_state is HumanReviewState.APPROVED
    assert staged.evidence_event_ids == ()

    with pytest.raises(EditorError) as excinfo:
        _publish(workspace, stmt.statement_id)
    assert "ZERO_EVIDENCE_EVENTS" in str(excinfo.value)

    after = workspace.editor.get(stmt.statement_id)
    assert after.publish_status is PublishStatus.PUBLISH_BLOCKED


def test_refused_publication_is_not_persisted(workspace):
    """A refusal must leave no published record on disk."""
    stmt = _draft(workspace)
    _approve(workspace, stmt.statement_id)
    with pytest.raises(EditorError):
        _publish(workspace, stmt.statement_id)

    path = pathlib.Path(workspace.editor.path)
    persisted = json.loads(path.read_text(encoding="utf-8"))
    assert persisted[stmt.statement_id]["publish_status"] == "PUBLISH_BLOCKED"


# -- 12. Gatekeeper / publication convergence -------------------------------

def test_gatekeeper_and_publication_gate_agree_on_the_unsupported(workspace):
    """The two routes must not disagree about the same statement."""
    stmt = _draft(workspace)
    _approve(workspace, stmt.statement_id)
    staged = workspace.editor.get(stmt.statement_id)

    with pytest.raises(EditorError):
        _publish(workspace, stmt.statement_id)

    gatekeeper = EvidenceGatekeeper()
    gatekeeper.add_statement(staged)
    gate = gatekeeper.evaluate_publish_gate()
    assert gate.is_publishable is False
    assert any("ZERO_EVIDENCE" in r for r in gate.reasons)

    admission = evaluate_statement_publication_admission(
        staged, events=workspace.events, registry=workspace.registry,
        questions=workspace.questions,
        statements_by_id=dict(workspace.editor._by_id),
    )
    assert admission.admitted is False
    assert PublicationRejection.ZERO_EVIDENCE_EVENTS in admission.reason_codes

    # And the downstream reader predicate does not see it as truth either.
    assert is_canonical_statement_admitted(workspace.editor.get(stmt.statement_id))[0] is False


# -- 2..7 the evidence matrix ------------------------------------------------

def _admission(ws: Workspace, statement: Statement):
    return evaluate_statement_publication_admission(
        statement, events=ws.events, registry=ws.registry,
        questions=ws.questions, statements_by_id=dict(ws.editor._by_id),
    )


def _supported(statement: Statement, **overrides) -> Statement:
    from dataclasses import replace
    base = dict(
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
    )
    base.update(overrides)
    return replace(statement, **base)


def test_empty_evidence_collection_rejects(workspace):
    stmt = _supported(_draft(workspace), evidence_event_ids=())
    assert PublicationRejection.ZERO_EVIDENCE_EVENTS in _admission(workspace, stmt).reason_codes


def test_nonexistent_evidence_reference_rejects(workspace):
    stmt = _supported(_draft(workspace), evidence_event_ids=("EVT-DOES-NOT-EXIST",))
    assert PublicationRejection.UNKNOWN_EVIDENCE_EVENT in _admission(workspace, stmt).reason_codes


@pytest.mark.parametrize("bad", ["", "   ", None, 12345, object()])
def test_malformed_evidence_reference_rejects(workspace, bad):
    stmt = _supported(_draft(workspace), evidence_event_ids=(bad,))
    result = _admission(workspace, stmt)
    assert result.admitted is False
    assert result.reason_codes  # never an exception, always a verdict


def test_private_source_cannot_back_publication(workspace):
    """A registered private source does not back publication.

    R2 recorded the opposite, on the strength of a comparison it never made:
    it asked `EvidenceGatekeeper.from_workspace` for its private-source
    reasons, but `from_workspace` registers sources and events and no
    statements, so the gate had nothing to object to and its silence was read
    as agreement. Asked about the statement itself, the gate refuses it with
    PRIVATE_SOURCE_UNVERIFIED_FOR_PUBLICATION.

    The artifact is known and digest-recorded, which is enough to cite it and
    not enough to publish on it: nobody holds the bytes, so the claim can never
    be checked against its source again. Evidence that cannot be re-read is a
    promise, and this boundary does not publish promises.
    """
    assert workspace.registry.resolve_path(PRIVATE_ARTIFACT) is None
    artifact = workspace.registry.get(PRIVATE_ARTIFACT)
    workspace.events.append(EvidenceEvent(
        event_id="EVT-PRIVATE-0001",
        artifact_sha256=artifact.sha256,
        locator="Booking confirmation, voyage block",
        entity_id="voyage:msc-bellissima:20261004-shanghai-tokyo",
        question_id=PRIVATE_QUESTION,
        observed_value="MSC Bellissima",
        observed_by="curator.one",
        observed_on="2026-08-31",
    ))
    stmt = _supported(
        _draft(
            workspace,
            entity="voyage:msc-bellissima:20261004-shanghai-tokyo",
            question_id=PRIVATE_QUESTION,
            statement_type=PRIVATE_TYPE,
            artifact_id=PRIVATE_ARTIFACT,
            value="MSC Bellissima",   # matches what the event observed
        ),
        evidence_event_ids=("EVT-PRIVATE-0001",),
    )
    result = _admission(workspace, stmt)
    assert result.admitted is False
    assert (PublicationRejection.EVENT_PRIVATE_SOURCE_NOT_REVERIFIABLE
            in result.reason_codes)


def test_condition_not_supported_rejects(workspace):
    stmt = _supported(_draft(workspace), evidence_condition=EvidenceCondition.UNKNOWN)
    assert PublicationRejection.CONDITION_NOT_SUPPORTED in _admission(workspace, stmt).reason_codes


def test_review_not_approved_rejects(workspace):
    stmt = _supported(_draft(workspace), human_review_state=HumanReviewState.DRAFT)
    assert PublicationRejection.REVIEW_NOT_APPROVED in _admission(workspace, stmt).reason_codes


# -- 7. mixture must fail closed --------------------------------------------

def test_one_valid_and_one_invalid_event_rejects(workspace):
    """Adding evidence must never subtract scrutiny."""
    stmt = _draft(workspace)
    _attach_real_event(workspace, stmt.statement_id, event_id="EVT-TEST-GOOD")
    good = workspace.editor.get(stmt.statement_id)
    assert _admission(workspace, _supported(good)).admitted is True

    for order in (("EVT-TEST-GOOD", "EVT-MISSING"), ("EVT-MISSING", "EVT-TEST-GOOD")):
        mixed = _supported(good, evidence_event_ids=order)
        result = _admission(workspace, mixed)
        assert result.admitted is False
        assert PublicationRejection.UNKNOWN_EVIDENCE_EVENT in result.reason_codes


# -- INFERRED closure --------------------------------------------------------

def test_inferred_statement_needs_closure(workspace):
    stmt = _supported(
        _draft(workspace), method=Method.INFERRED,
        input_statement_ids=(), rule_hash=None, evidence_event_ids=(),
    )
    assert PublicationRejection.INFERRED_INCOMPLETE_CLOSURE in _admission(workspace, stmt).reason_codes


def test_inferred_statement_rejects_when_its_input_is_not_admitted(workspace):
    """Closure is only closure if it bottoms out in evidence."""
    parent = _draft(workspace, entity="port:unlocode:ESBCN")  # zero evidence
    child = _supported(
        _draft(workspace), method=Method.INFERRED,
        input_statement_ids=(parent.statement_id,),
        rule_hash="a" * 64, evidence_event_ids=(),
    )
    codes = _admission(workspace, child).reason_codes
    assert PublicationRejection.INFERRED_INPUT_NOT_ADMITTED in codes


def test_inferred_statement_rejects_a_nonexistent_input(workspace):
    child = _supported(
        _draft(workspace), method=Method.INFERRED,
        input_statement_ids=("STM-NOPE",), rule_hash="a" * 64,
        evidence_event_ids=(),
    )
    assert PublicationRejection.INFERRED_INPUT_NOT_ADMITTED in _admission(workspace, child).reason_codes


def test_derivation_cycles_terminate_and_reject(workspace):
    """A self-referential inference must not recurse forever."""
    from dataclasses import replace
    stmt = _draft(workspace)
    looped = _supported(
        stmt, method=Method.INFERRED,
        input_statement_ids=(stmt.statement_id,), rule_hash="a" * 64,
        evidence_event_ids=(),
    )
    workspace.editor._by_id[stmt.statement_id] = looped
    result = _admission(workspace, looped)
    assert result.admitted is False
    assert PublicationRejection.INFERRED_CIRCULAR_CLOSURE in result.reason_codes


# -- 4. the positive path ----------------------------------------------------

def test_genuinely_supported_statement_still_publishes(workspace):
    """Real artifact, real event, real workflow, real persistence."""
    stmt = _draft(workspace)
    _attach_real_event(workspace, stmt.statement_id)
    _approve(workspace, stmt.statement_id)

    published = _publish(workspace, stmt.statement_id)
    assert published.publish_status is PublishStatus.PUBLISH_ALLOWED

    # Reaches the real sink.
    persisted = json.loads(pathlib.Path(workspace.editor.path).read_text(encoding="utf-8"))
    assert persisted[stmt.statement_id]["publish_status"] == "PUBLISH_ALLOWED"

    # And the downstream reader agrees it is truth.
    assert is_canonical_statement_admitted(published)[0] is True


def test_the_positive_fixture_is_not_a_stub(workspace):
    """Each requirement is really exercised, against held bytes."""
    from timonelo.evidence.registry import sha256_of_file

    stmt = _draft(workspace)
    updated = _attach_real_event(workspace, stmt.statement_id)
    artifact = workspace.registry.get(HELD_ARTIFACT)
    path = workspace.registry.resolve_path(artifact.artifact_id)

    assert updated.evidence_event_ids                       # cites evidence
    assert path is not None                                 # bytes held
    assert sha256_of_file(path) == artifact.sha256          # digest re-verifies
    assert workspace.questions.get(ELIGIBLE_QUESTION).can_be_supported_by(
        artifact.document_class)                            # class eligible


# -- 8/9. direct writer attempts --------------------------------------------

def test_truth_engine_publish_is_gated_too(workspace):
    """The second writer must not define a weaker idea of publishable.

    `Workspace.engine` is the reader in `evidence.truth`; the publication
    writer is the `TruthEngine` in `evidence.engine`, which is what this pins.
    """
    from timonelo.evidence.engine import TruthEngine as WritingTruthEngine

    stmt = _draft(workspace)
    _approve(workspace, stmt.statement_id)

    engine = WritingTruthEngine(workspace.questions, workspace.events, workspace.registry)
    engine._statements = workspace.editor._by_id
    with pytest.raises(ValueError) as excinfo:
        engine.publish(stmt.statement_id)
    assert "ZERO_EVIDENCE_EVENTS" in str(excinfo.value)
    assert workspace.editor.get(stmt.statement_id).publish_status is PublishStatus.PUBLISH_BLOCKED


def test_truth_engine_reader_serves_no_unbacked_statement(workspace):
    """The reader consults only PUBLISH_ALLOWED, which the sink now protects."""
    # A fresh entity, so no previously published statement can answer for it.
    stmt = _draft(workspace, entity="port:unlocode:ZZTEST")
    _approve(workspace, stmt.statement_id)
    with pytest.raises(EditorError):
        _publish(workspace, stmt.statement_id)
    answer = workspace.engine.answer(stmt.entity_id, stmt.question_id)
    assert answer.known is False


def test_direct_status_mutation_does_not_survive_reload(workspace):
    """Bypassing the API in memory must not produce durable truth."""
    from dataclasses import replace
    stmt = _draft(workspace)
    _approve(workspace, stmt.statement_id)
    forged = replace(
        workspace.editor.get(stmt.statement_id),
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    workspace.editor._by_id[stmt.statement_id] = forged
    workspace.editor._flush()

    reloaded = Workspace(str(pathlib.Path(workspace.editor.path).parents[1]))
    assert reloaded.editor.get(stmt.statement_id).publish_status is PublishStatus.PUBLISH_BLOCKED
    assert stmt.statement_id in reloaded.editor.demoted_on_load


# -- 10. deserialization / import -------------------------------------------

def test_imported_statement_claiming_published_without_backing_is_demoted(workspace, tmp_path):
    """A stored status is not evidence."""
    path = pathlib.Path(workspace.editor.path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["STM-FORGED"] = {
        "statement_id": "STM-FORGED",
        "entity_id": "port:unlocode:ESBCN",
        "question_id": ELIGIBLE_QUESTION,
        "statement_type": ELIGIBLE_TYPE,
        "value": "Imported claim",
        "artifact_id": HELD_ARTIFACT,
        "locator": "imported",
        "read_by": "importer",
        "read_on": "2026-08-31",
        "method": "DIRECT",
        "derivation": "LOCAL",
        "evidence_event_ids": [],
        "evidence_condition": "SUPPORTED",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_ALLOWED",
    }
    path.write_text(json.dumps(raw), encoding="utf-8")

    reloaded = Workspace(str(path.parents[1]))
    forged = reloaded.editor.get("STM-FORGED")
    assert forged.publish_status is PublishStatus.PUBLISH_BLOCKED
    assert "STM-FORGED" in reloaded.editor.demoted_on_load
    assert is_canonical_statement_admitted(forged)[0] is False


def test_legacy_published_string_no_longer_confers_publication(workspace, tmp_path):
    """`review_state: "PUBLISHED"` used to upgrade straight to PUBLISH_ALLOWED."""
    path = pathlib.Path(workspace.editor.path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["STM-LEGACY"] = {
        "statement_id": "STM-LEGACY",
        "entity_id": "port:unlocode:ESBCN",
        "question_id": ELIGIBLE_QUESTION,
        "statement_type": ELIGIBLE_TYPE,
        "value": "Legacy claim",
        "artifact_id": HELD_ARTIFACT,
        "locator": "legacy",
        "read_by": "legacy",
        "read_on": "2026-08-17",
        "review_state": "PUBLISHED",
    }
    path.write_text(json.dumps(raw), encoding="utf-8")

    reloaded = Workspace(str(path.parents[1]))
    legacy = reloaded.editor.get("STM-LEGACY")
    assert legacy.human_review_state is HumanReviewState.APPROVED  # approval is remembered
    assert legacy.publish_status is PublishStatus.PUBLISH_BLOCKED  # publication is not


# -- structural backing helper ----------------------------------------------
#
# `has_structural_backing` and its test are gone. It answered "does this claim
# to rest on something", which a claim-mismatched statement answers correctly
# while resting on nothing, and R2 used it to keep publication alive on loads
# that could not check. A predicate whose only role was to approve what could
# not be verified had no honest caller left once authority became computed.


def test_require_form_raises_with_a_reason(workspace):
    stmt = _supported(_draft(workspace))
    with pytest.raises(StatementPublicationError) as excinfo:
        require_statement_publication_admission(
            stmt, events=workspace.events, registry=workspace.registry,
            questions=workspace.questions,
            statements_by_id=dict(workspace.editor._by_id),
        )
    assert "ZERO_EVIDENCE_EVENTS" in str(excinfo.value)


# -- the committed store ------------------------------------------------------

def test_no_committed_statement_claims_publication_without_backing():
    """Every PUBLISH_ALLOWED record in the repository must be backed."""
    raw = json.loads((REAL_EVIDENCE / "statements" / "statements.json").read_text(encoding="utf-8"))
    unbacked = [
        sid for sid, s in raw.items()
        if s.get("publish_status") == "PUBLISH_ALLOWED"
        and not s.get("evidence_event_ids")
        and not (s.get("input_statement_ids") and s.get("rule_hash"))
    ]
    assert unbacked == [], f"unbacked published statements: {unbacked}"


def test_committed_published_statements_survive_full_admission():
    """The repository's own published set passes the real gate."""
    ws = Workspace(str(REAL_EVIDENCE))
    by_id = {s.statement_id: s for s in ws.editor.all()}
    claiming = [s for s in by_id.values() if s.publish_status is not PublishStatus.PUBLISH_BLOCKED]
    assert claiming, "expected some published statements to verify"
    for statement in claiming:
        result = evaluate_statement_publication_admission(
            statement, events=ws.events, registry=ws.registry,
            questions=ws.questions, statements_by_id=by_id,
        )
        assert result.admitted, f"{statement.statement_id}: {result.summary()}"
