"""
Guards current publication authority.

P1 made a statement earn PUBLISH_ALLOWED against real evidence. R2 tightened
what "real" meant. Neither made a statement *keep* it. `publish_status` is
written to disk; evidence is not frozen alongside it; and nothing asked the
question again. So an event could be superseded, an artifact replaced, a rule
edited, and the stored axes would go on reading as truth to every consumer that
looked at them -- which was all of them.

The distinction these tests pin is between two things that had been conflated:

  * lifecycle state, which records that publication was granted once, and
  * authority, which is whether that grant still holds against the evidence
    the repository has right now.

The first is stored and is audit. The second is computed, per question, by
`PublicationAuthority`, and no truth-bearing consumer may answer canonical,
known, answerable or authoritative without it. Being unable to check is not
permission to skip the check: an authority missing any part of its validation
context refuses everything and says which part is missing.
"""

from __future__ import annotations

import hashlib
import pathlib
from dataclasses import replace

from timonelo.evidence.editor import StatementEditor
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.gatekeeper import is_canonical_statement_admitted
from timonelo.evidence.models import Method, PublishStatus
from timonelo.evidence.publication import (
    NO_AUTHORITY,
    PublicationRejection,
)
from timonelo.evidence.review import ReviewLog
from timonelo.spatial.review import (
    VenueAssociationState,
    match_venue_statement,
)
from timonelo.evidence.workspace import Workspace
from timonelo.factory.voyage import is_admitted_truth

from tests.test_statement_publication_admission import (  # noqa: F401
    ELIGIBLE_QUESTION,
    HELD_ARTIFACT,
    _draft,
    _supported,
    workspace,
)


def _backed(ws, *, value="Port of Marseille", event_id="EVT-R3-0001", **overrides):
    """A statement genuinely backed by an event that observed its claim."""
    artifact = ws.registry.get(HELD_ARTIFACT)
    stmt = _draft(ws, entity="port:unlocode:FRMRS", value=value, **overrides)
    ws.events.append(EvidenceEvent(
        event_id=event_id,
        artifact_sha256=artifact.sha256,
        locator="Test locator naming a real place in the document",
        entity_id=stmt.entity_id,
        question_id=stmt.question_id,
        observed_value=value,
        observed_by="curator.one",
        observed_on="2026-08-31",
    ))
    published = _supported(
        replace(stmt, publish_status=PublishStatus.PUBLISH_ALLOWED),
        evidence_event_ids=(event_id,),
    )
    ws.editor._by_id[stmt.statement_id] = published
    return published


def _drop_event(ws, event_id):
    ws.events._events = [e for e in ws.events.all() if e.event_id != event_id]


# -- 1. an editor that cannot check must not confirm --------------------------

def test_editor_without_evidence_context_confers_no_authority(workspace, tmp_path):
    """The structural fallback approved exactly what it could not verify.

    R2 demoted on load using full admission where events and questions were
    available, and `has_structural_backing` where they were not. That fallback
    asked whether a statement *claimed* to rest on something -- a question a
    claim-mismatched statement answers perfectly well. So an editor opened
    without evidence context confirmed the statements it was least equipped to
    judge, and handed them back with PUBLISH_ALLOWED intact.
    """
    artifact = workspace.registry.get(HELD_ARTIFACT)
    workspace.events.append(EvidenceEvent(
        event_id="EVT-R3-MISMATCH",
        artifact_sha256=artifact.sha256,
        locator="Test locator naming a real place in the document",
        entity_id="port:unlocode:FRMRS",
        question_id=ELIGIBLE_QUESTION,
        observed_value="Something Else Entirely",
        observed_by="curator.one",
        observed_on="2026-08-31",
    ))
    stmt = _draft(workspace, entity="port:unlocode:FRMRS", value="Port of Marseille")
    workspace.editor._by_id[stmt.statement_id] = _supported(
        replace(stmt, publish_status=PublishStatus.PUBLISH_ALLOWED),
        evidence_event_ids=("EVT-R3-MISMATCH",),
    )
    workspace.editor._flush()

    bare = StatementEditor(
        workspace.editor.path,
        workspace.registry,
        ReviewLog(str(tmp_path / "r3-reviews.json")),
    )
    loaded = bare.get(stmt.statement_id)

    # The stored grant survives, because an editor with no evidence context has
    # no standing to withdraw it either -- but it confers nothing.
    assert loaded.publish_status is PublishStatus.PUBLISH_ALLOWED
    assert bare.demoted_on_load == []
    assert bare.is_currently_authoritative(loaded) is False
    assert bare.authority.missing_context == ("events", "questions")

    # The wired editor, which can check, refuses on the merits.
    verdict = workspace.editor.authority.evaluate(loaded)
    assert PublicationRejection.EVIDENCE_DOES_NOT_SUPPORT_CLAIM in verdict.reason_codes


def test_missing_context_names_what_is_missing(workspace):
    assert NO_AUTHORITY.has_context is False
    assert NO_AUTHORITY.missing_context == (
        "events", "registry", "questions", "statements")
    assert workspace.editor.authority.has_context is True

    stmt = _backed(workspace)
    assert NO_AUTHORITY.is_currently_authoritative(stmt) is False
    assert (PublicationRejection.NO_VALIDATION_CONTEXT
            in NO_AUTHORITY.evaluate(stmt).reason_codes)


# -- 2. evidence that moves after the grant -----------------------------------

def test_authority_is_withdrawn_when_evidence_changes_after_load(workspace):
    """The whole defect in one test: nothing here touches the statement.

    The grant was earned honestly and the record is never rewritten. Only the
    evidence moves -- the event it rests on stops resolving -- and the stored
    axes cannot notice, because they were written before it happened. A
    consumer reading lifecycle state answers `known=True` for a claim whose
    support no longer exists.
    """
    stmt = _backed(workspace)
    assert workspace.engine.answer(stmt.entity_id, stmt.question_id).known is True
    assert workspace.editor.is_currently_authoritative(stmt) is True

    _drop_event(workspace, "EVT-R3-0001")

    unchanged = workspace.editor.get(stmt.statement_id)
    assert unchanged.publish_status is PublishStatus.PUBLISH_ALLOWED

    assert workspace.editor.is_currently_authoritative(unchanged) is False
    assert workspace.engine.answer(stmt.entity_id, stmt.question_id).known is False
    assert (PublicationRejection.UNKNOWN_EVIDENCE_EVENT
            in workspace.editor.authority.evaluate(unchanged).reason_codes)


def test_authority_is_withdrawn_when_the_artifact_changes(workspace):
    """A replaced artifact invalidates the claims read out of it."""
    stmt = _backed(workspace, event_id="EVT-R3-ART")
    assert workspace.editor.is_currently_authoritative(stmt) is True

    path = workspace.registry.resolve_path(HELD_ARTIFACT)
    pathlib.Path(path).write_bytes(b"a different document entirely")

    assert workspace.editor.authority.evaluate(stmt).admitted is False


# -- 3. rule provenance -------------------------------------------------------

def test_inference_fails_closed_without_a_resolvable_rule(workspace):
    """A well-formed hash pointing at nothing is not provenance.

    ADR-0003 section 3 requires a derived statement to cite the hash of the
    rule version it consumed, so that editing a rule invalidates its closure.
    This repository has no rule store and no resolver, so nothing can say what
    any hash names -- and a fabricated 64-hex string is indistinguishable from
    a real citation. The ADR names this exact costume.
    """
    parent = _backed(workspace, event_id="EVT-R3-RULE")
    fabricated = hashlib.sha256(b"a rule that was never written").hexdigest()
    child = _supported(replace(
        parent, statement_id="STM-R3-INFERRED", method=Method.INFERRED,
        input_statement_ids=(parent.statement_id,), rule_hash=fabricated,
        evidence_event_ids=()))
    workspace.editor._by_id[child.statement_id] = child

    verdict = workspace.editor.authority.evaluate(child)
    assert verdict.admitted is False
    assert (PublicationRejection.INFERRED_RULE_PROVENANCE_UNRESOLVABLE
            in verdict.reason_codes)


def test_inference_admits_once_the_rule_resolves(workspace, rule_store):
    """The refusal is about resolvability, not about INFERRED."""
    parent = _backed(workspace, event_id="EVT-R3-RULE-OK")
    digest = rule_store.add(b"timonelo.rules.r3:v1")
    child = _supported(replace(
        parent, statement_id="STM-R3-OK", method=Method.INFERRED,
        input_statement_ids=(parent.statement_id,), rule_hash=digest,
        evidence_event_ids=(),
        publish_status=PublishStatus.PUBLISH_ALLOWED))
    workspace.editor._by_id[child.statement_id] = child

    assert workspace.editor.is_currently_authoritative(child) is True

    # Editing the rule produces a new hash, and the closure falls with it.
    rule_store.remove(digest)
    assert workspace.editor.is_currently_authoritative(child) is False


def test_closure_follows_the_present_not_a_snapshot(workspace, rule_store):
    """An inference is re-checked against its inputs as they stand now."""
    parent = _backed(workspace, event_id="EVT-R3-CLOSURE")
    digest = rule_store.add(b"timonelo.rules.r3.closure:v1")
    child = _supported(replace(
        parent, statement_id="STM-R3-CLOSURE", method=Method.INFERRED,
        input_statement_ids=(parent.statement_id,), rule_hash=digest,
        evidence_event_ids=(),
        publish_status=PublishStatus.PUBLISH_ALLOWED))
    workspace.editor._by_id[child.statement_id] = child
    assert workspace.editor.is_currently_authoritative(child) is True

    # The input loses its support. The inference must fall with it.
    workspace.editor._by_id[parent.statement_id] = replace(
        parent, evidence_event_ids=())

    verdict = workspace.editor.authority.evaluate(child)
    assert verdict.admitted is False
    assert PublicationRejection.INFERRED_INPUT_NOT_ADMITTED in verdict.reason_codes


# -- 4. capability is not permission -----------------------------------------

def test_unresolvable_question_is_not_permission(workspace):
    """An unknown question cannot establish that a document class may answer it.

    R2 skipped the document-class check when the question could not be
    resolved, so a statement citing a question that does not exist sailed past
    the one gate meant to establish eligibility. Absence of metadata read as
    permission.
    """
    stmt = _backed(workspace, event_id="EVT-R3-QUESTION")
    unknown = replace(stmt, question_id="Q-DOES-NOT-EXIST")

    verdict = workspace.editor.authority.evaluate(unknown)
    assert verdict.admitted is False
    assert PublicationRejection.QUESTION_METADATA_UNRESOLVABLE in verdict.reason_codes


# -- 5. every truth-bearing consumer -----------------------------------------

def test_voyage_selector_refuses_without_an_authority(workspace):
    """`is_admitted_truth` gates ship identity and port resolution.

    Its default is the refusing authority: a caller supplying no evidence
    context gets False rather than the axes verdict, because the axes cannot
    tell it what it needs to know.
    """
    stmt = _backed(workspace, event_id="EVT-R3-VOYAGE")
    assert is_admitted_truth(stmt) is False
    assert is_admitted_truth(stmt, authority=workspace.editor.authority) is True

    _drop_event(workspace, "EVT-R3-VOYAGE")
    assert is_admitted_truth(stmt, authority=workspace.editor.authority) is False


def test_canonical_predicate_separates_axes_from_authority(workspace):
    """The shared predicate must not present a lifecycle pass as a verdict."""
    stmt = _backed(workspace, event_id="EVT-R3-CANON")

    admitted, reason = is_canonical_statement_admitted(stmt)
    assert admitted is True
    assert "current publication authority was not checked" in reason

    admitted, reason = is_canonical_statement_admitted(
        stmt, authority=workspace.editor.authority)
    assert admitted is True
    assert "against current evidence" in reason

    _drop_event(workspace, "EVT-R3-CANON")
    admitted, reason = is_canonical_statement_admitted(
        stmt, authority=workspace.editor.authority)
    assert admitted is False
    assert "no longer admissible" in reason


def test_decoded_records_cannot_establish_authority(workspace):
    """A statement dict read out of a compiled pack has no link to evidence."""
    stmt = _backed(workspace, event_id="EVT-R3-DICT")
    as_dict = {
        "statement_id": stmt.statement_id,
        "evidence_condition": "SUPPORTED",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_ALLOWED",
    }
    admitted, reason = is_canonical_statement_admitted(
        as_dict, authority=workspace.editor.authority)
    assert admitted is False
    assert "carries no link to current evidence" in reason


# -- 6. the production store --------------------------------------------------

def test_private_source_statements_lose_authority_in_the_real_store(workspace):
    """STM-0403..STM-0410 rest on a booking confirmation nobody holds."""
    assert workspace.editor.demoted_on_load == [
        f"STM-{n:04d}" for n in range(403, 411)
    ]
    for n in range(403, 411):
        stored = workspace.editor.get(f"STM-{n:04d}")
        assert stored.publish_status is PublishStatus.PUBLISH_BLOCKED


def test_load_time_demotion_does_not_write_to_the_store(workspace):
    """Withdrawing authority in memory must not rewrite the evidence file."""
    path = pathlib.Path(workspace.editor.path)
    before = path.read_bytes()
    reloaded = Workspace(str(path.parent.parent))
    assert reloaded.editor.demoted_on_load  # it did demote
    assert path.read_bytes() == before


def test_values_agree_does_not_conflate_numbers_with_booleans():
    """`1` is not `True`: a thing counted once is not a thing confirmed."""
    from timonelo.evidence.publication import _values_agree

    assert _values_agree(1, True) is False
    assert _values_agree(True, 1) is False
    assert _values_agree(0, False) is False
    assert _values_agree(True, True) is True
    assert _values_agree(14, "14") is True


# -- 7. the spatial promotion path -------------------------------------------

def test_venue_association_will_not_promote_on_decoded_axes_alone(workspace):
    """Geometry reached passenger publication on three stored values.

    `match_venue_statement` is handed decoded statement records -- axes and no
    link to evidence -- and a True verdict there set
    PROMOTED_TO_PASSENGER_PUBLISH. So a venue could be published to passengers
    on the strength of a PUBLISH_ALLOWED written months earlier, against
    evidence nobody rechecked. The axes result is still reported, under a name
    that says what it is; admission requires an authority.
    """
    stmt = _backed(workspace, event_id="EVT-R3-VENUE")
    label = "Test Venue R3"
    record = {
        "statement_id": stmt.statement_id,
        "statement_type": "deck.venue_present",
        "target_entity": label.upper(),
        "deck_number": 5,
        "value": [5],
        "locator": f'"{label.upper()}"',
        "evidence_condition": "SUPPORTED",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_ALLOWED",
    }
    statements = {stmt.statement_id: record}

    assoc = match_venue_statement(label, 5, statements)
    assert assoc.state is VenueAssociationState.MATCHED
    assert assoc.lifecycle_axes_pass is True
    assert assoc.is_canonical_admitted is False
    assert "current publication authority cannot be established" in assoc.reason

    # An authority is supplied, and a decoded record still cannot prove itself.
    assoc = match_venue_statement(
        label, 5, statements, authority=workspace.editor.authority)
    assert assoc.is_canonical_admitted is False
    assert "carries no link to current evidence" in assoc.reason
