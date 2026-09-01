"""
Guards the truth consumption boundary.

R3 established that `PublicationAuthority` invalidates truth against current
evidence in the primary Workspace truth path. It did not reach everywhere.
Several consumers went on deriving authoritative meaning straight from the
three persisted lifecycle axes -- the direct `evidence.engine.TruthEngine`, the
whole structured inspection API, document coverage, the passenger-facing
formatter, and the voyage aggregate. Each of them would answer "yes, known" for
a claim whose supporting evidence had already been withdrawn, because each was
reading a record of a grant rather than asking whether the grant still held.

Two matrices are pinned here.

The live-invalidation matrix (`TestLiveInvalidation`) establishes genuine
evidence, confirms the authoritative result, then withdraws the evidence
through the normal mechanism and asks *the same live objects* again. Nothing is
reconstructed: no new Workspace, no new editor, no new authority. A consumer
that has to be rebuilt to notice is a consumer that serves stale truth for the
lifetime of a process.

The fail-closed matrix (`TestMissingContext`) removes each part of the
validation context in turn. Every absence must produce non-authority. "Cannot
check" is never "allowed".
"""

from __future__ import annotations

import pathlib
from dataclasses import replace

import pytest

from timonelo.evidence.api import ArtifactInspectionAPI, StatementRegistryAPI
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.gatekeeper import (
    is_canonical_statement_admitted,
    lifecycle_axes_pass,
)
from timonelo.evidence.models import PublishStatus
from timonelo.evidence.publication import PublicationAuthority

from tests.test_statement_publication_admission import (  # noqa: F401
    ELIGIBLE_QUESTION,
    HELD_ARTIFACT,
    _draft,
    _supported,
    workspace,
)

ENTITY = "port:unlocode:FRMRS"
VALUE = "Port of Marseille"
EVENT = "EVT-TCB-0001"


@pytest.fixture
def backed(workspace):
    """One genuinely backed, genuinely published statement in a live workspace.

    The event observes this entity, this question and this value, against an
    artifact the workspace holds and can re-hash. Nothing here is asserted into
    place: remove the event and every consumer below must notice.
    """
    artifact = workspace.registry.get(HELD_ARTIFACT)
    stmt = _draft(workspace, entity=ENTITY, value=VALUE)
    workspace.events.append(EvidenceEvent(
        event_id=EVENT,
        artifact_sha256=artifact.sha256,
        locator="Test locator naming a real place in the document",
        entity_id=ENTITY,
        question_id=ELIGIBLE_QUESTION,
        observed_value=VALUE,
        observed_by="curator.one",
        observed_on="2026-08-31",
    ))
    published = _supported(
        replace(stmt, publish_status=PublishStatus.PUBLISH_ALLOWED),
        evidence_event_ids=(EVENT,),
    )
    workspace.editor._by_id[stmt.statement_id] = published
    return published


def _withdraw(ws, event_id=EVENT):
    """Withdraw the evidence through the normal log, touching no statement."""
    ws.events._events = [e for e in ws.events.all() if e.event_id != event_id]


def _withdraw_question(ws, artifact_id, question_id):
    """Withdraw every event backing a question on one artifact.

    Coverage counts questions, not statements, so a question stays answered
    while any statement still answers it -- `STM-0392` already answers Q-0024
    on this artifact. To watch coverage move, the whole question has to lose
    its support.
    """
    doomed = set()
    for statement in ws.statements_for_artifact(artifact_id):
        if statement.question_id == question_id:
            doomed.update(statement.evidence_event_ids)
    ws.events._events = [e for e in ws.events.all() if e.event_id not in doomed]


def _direct_engine(ws, statement):
    """A direct `evidence.engine.TruthEngine` over the same live evidence log."""
    from timonelo.evidence.engine import TruthEngine as WritingTruthEngine

    engine = WritingTruthEngine(ws.questions, ws.events, ws.registry)
    engine._statements[statement.statement_id] = statement
    return engine


class TestLiveInvalidation:
    """authoritative -> evidence invalidated -> immediately non-authoritative.

    Every case queries the same object across the transition.
    """

    def test_workspace_truth_engine(self, workspace, backed):
        assert workspace.engine.answer(ENTITY, ELIGIBLE_QUESTION).known is True
        _withdraw(workspace)
        assert workspace.engine.answer(ENTITY, ELIGIBLE_QUESTION).known is False

    def test_direct_engine(self, workspace, backed):
        """The writer-side engine keeps its own statements and its own answers.

        It had no authority at all: `answer` filtered on stored axes over
        `self._statements`, so anything added while its evidence was good
        stayed answerable for the life of the object.
        """
        engine = _direct_engine(workspace, backed)
        assert engine.answer(ENTITY, ELIGIBLE_QUESTION).known is True

        _withdraw(workspace)

        assert engine.answer(ENTITY, ELIGIBLE_QUESTION).known is False
        assert engine.authority.is_currently_authoritative(backed) is False

    def test_direct_engine_coverage(self, workspace, backed):
        engine = _direct_engine(workspace, backed)
        before = engine.coverage(ENTITY, "port")
        assert before["questions_answerable"] >= 1

        _withdraw(workspace)

        after = engine.coverage(ENTITY, "port")
        assert after["questions_answerable"] == before["questions_answerable"] - 1
        assert ELIGIBLE_QUESTION in after["unknown_question_ids"]

    def test_statement_registry_api_get(self, workspace, backed):
        api = StatementRegistryAPI(workspace)
        assert api.get(backed.statement_id).answerable is True
        _withdraw(workspace)
        assert api.get(backed.statement_id).answerable is False

    def test_statement_registry_api_answerable_only(self, workspace, backed):
        api = StatementRegistryAPI(workspace)
        found = api.query(entity_id=ENTITY, answerable_only=True)
        assert [s.statement_id for s in found] == [backed.statement_id]

        _withdraw(workspace)

        assert api.query(entity_id=ENTITY, answerable_only=True) == []
        # The statement itself is still there; only its answerability went.
        unfiltered = api.query(entity_id=ENTITY)
        assert [s.statement_id for s in unfiltered] == [backed.statement_id]
        assert unfiltered[0].answerable is False

    def test_passenger_formatter(self, workspace, backed):
        rendered = workspace.format_statement(backed.statement_id)
        assert "passenger sees  YES" in rendered

        _withdraw(workspace)

        rendered = workspace.format_statement(backed.statement_id)
        assert "passenger sees  YES" not in rendered
        assert "not answerable" in rendered
        # The review history line still reports the stored axis, because that
        # line is about what happened, not about what is true now.
        assert "workflow state  APPROVED" in rendered

    def test_document_coverage(self, workspace, backed):
        before = workspace.document_coverage(HELD_ARTIFACT)
        assert ELIGIBLE_QUESTION not in before["unknown_question_ids"]

        _withdraw_question(workspace, HELD_ARTIFACT, ELIGIBLE_QUESTION)

        after = workspace.document_coverage(HELD_ARTIFACT)
        assert after["questions_answered"] == before["questions_answered"] - 1
        # Which questions the class *could* answer is structural and unmoved.
        assert after["questions_supported"] == before["questions_supported"]
        assert ELIGIBLE_QUESTION in after["unknown_question_ids"]

    def test_canonical_predicate(self, workspace, backed):
        authority = workspace.editor.authority
        assert is_canonical_statement_admitted(backed, authority=authority)[0] is True

        _withdraw(workspace)

        admitted, reason = is_canonical_statement_admitted(
            backed, authority=authority)
        assert admitted is False
        assert "no longer admissible" in reason
        # The stored axes still agree. That is what made this dangerous.
        assert lifecycle_axes_pass(backed)[0] is True

    def test_artifact_inspection_summary(self, workspace, backed):
        """The derived consumer the brief names: axes -> coverage -> summary."""
        api = ArtifactInspectionAPI(workspace)
        before = api.inspect(HELD_ARTIFACT)
        assert any(s.answerable for s in before.statements)
        assert before.coverage["questions_answered"] >= 1

        _withdraw_question(workspace, HELD_ARTIFACT, ELIGIBLE_QUESTION)

        after = api.inspect(HELD_ARTIFACT)
        mine = [s for s in after.statements
                if s.statement_id == backed.statement_id]
        assert mine and mine[0].answerable is False
        assert after.coverage["questions_answered"] == (
            before.coverage["questions_answered"] - 1)

    def test_pending_review_queue_membership_is_unchanged(self, workspace, backed):
        """Queue membership is a review-state question and stays one.

        Only the projected `answerable` field moved to current authority. A
        DRAFT statement belongs in the curator queue because nobody has judged
        it, which has nothing to do with whether its evidence still stands.
        """
        api = StatementRegistryAPI(workspace)
        draft = _draft(workspace, entity=ENTITY, value="Another Reading")
        before = {s.statement_id for s in api.pending_review()}
        assert draft.statement_id in before
        assert backed.statement_id not in before

        _withdraw(workspace)

        assert {s.statement_id for s in api.pending_review()} == before

    def test_artifact_replacement_invalidates(self, workspace, backed):
        """Not only withdrawn events: replaced bytes must invalidate too."""
        api = StatementRegistryAPI(workspace)
        assert api.get(backed.statement_id).answerable is True

        path = workspace.registry.resolve_path(HELD_ARTIFACT)
        pathlib.Path(path).write_bytes(b"an entirely different document")

        assert api.get(backed.statement_id).answerable is False
        assert workspace.engine.answer(ENTITY, ELIGIBLE_QUESTION).known is False


class TestVoyageAggregate:
    """Aggregate publishability must derive from current constituents."""

    def test_aggregate_publishability_is_not_the_stored_axis(self, workspace):
        from timonelo.factory.voyage import VoyageKnowledgeFactory, is_admitted_truth

        factory = VoyageKnowledgeFactory(workspace)
        authority = factory._authority

        # The reference voyage statements still carry SUPPORTED and APPROVED,
        # and their stored publish_status was PUBLISH_ALLOWED on disk. None of
        # them is currently authoritative, so no aggregate built from them may
        # claim to be publishable.
        constituents = [workspace.editor.get(f"STM-{n:04d}")
                        for n in range(403, 411)]
        assert all(lifecycle_axes_pass(s)[0] is False
                   or is_admitted_truth(s, authority=authority) is False
                   for s in constituents)
        assert not any(is_admitted_truth(s, authority=authority)
                       for s in constituents)


class TestMissingContext:
    """Every missing capability must produce non-authority, never permission."""

    @pytest.mark.parametrize("missing", ["events", "registry", "questions", "statements"])
    def test_each_missing_piece_fails_closed(self, workspace, backed, missing):
        pieces = dict(
            events=workspace.events,
            registry=workspace.registry,
            questions=workspace.questions,
            statements=lambda: workspace.editor._by_id,
        )
        pieces[missing] = None
        authority = PublicationAuthority(**pieces)

        assert authority.has_context is False
        assert missing in authority.missing_context
        assert authority.is_currently_authoritative(backed) is False

    def test_a_complete_context_still_admits(self, workspace, backed):
        """The matrix above must be failing for the reason it claims."""
        authority = PublicationAuthority(
            events=workspace.events,
            registry=workspace.registry,
            questions=workspace.questions,
            statements=lambda: workspace.editor._by_id,
        )
        assert authority.has_context is True
        assert authority.is_currently_authoritative(backed) is True

    def test_summary_cannot_be_built_without_an_authority(self, workspace, backed):
        """`_summarise` takes its authority positionally so it cannot be forgotten."""
        from timonelo.evidence.api import _summarise

        with pytest.raises(TypeError):
            _summarise(backed)

    def test_missing_rule_resolver_denies_inferred_authority(self, workspace, backed):
        """No rule store, no authoritative inference. Fail closed, not open."""
        import hashlib

        from timonelo.evidence.models import Method

        child = _supported(replace(
            backed, statement_id="STM-TCB-INFERRED", method=Method.INFERRED,
            input_statement_ids=(backed.statement_id,),
            rule_hash=hashlib.sha256(b"unresolvable").hexdigest(),
            evidence_event_ids=(),
            publish_status=PublishStatus.PUBLISH_ALLOWED))
        workspace.editor._by_id[child.statement_id] = child

        api = StatementRegistryAPI(workspace)
        assert api.get(child.statement_id).answerable is False

    def test_canonical_predicate_without_authority_is_not_admission(self, workspace, backed):
        admitted, reason = is_canonical_statement_admitted(backed)
        assert admitted is False
        assert "was not checked" in reason
