"""
R2: one regression per independent-review finding.

The R1 boundary closed the write path and left the read path open. A statement
persisted as PUBLISH_ALLOWED citing an event that did not exist survived load,
satisfied the canonical predicate, and was served as truth. Alongside that the
review found forged state injectable through `add_statement`, a publication
permission check I had removed with no owner left behind, evidence that never
had to support the claim it backed, rule hashes checked only for truthiness,
unbounded recursion on deep inference graphs, and test fixtures that
manufactured their own support.

Each of those has a test here, named for what it protects rather than for the
finding number, and the shared helpers come from the R1 suite so both describe
the same system.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import replace

import pytest

from timonelo.evidence import authority
from timonelo.evidence.editor import EditorError
from timonelo.evidence.gatekeeper import (
    EvidenceGatekeeper,
    is_canonical_statement_admitted,
)
from timonelo.evidence.models import (
    EvidenceCondition,
    HumanReviewState,
    Method,
    PublishStatus,
)
from timonelo.evidence.publication import (
    PublicationRejection,
    evaluate_statement_publication_admission,
    is_valid_rule_hash,
)
from timonelo.evidence.workspace import Workspace

from tests.test_statement_publication_admission import (  # noqa: F401
    ELIGIBLE_QUESTION,
    ELIGIBLE_TYPE,
    HELD_ARTIFACT,
    _admission,
    _approve,
    _attach_real_event,
    _draft,
    _publish,
    _supported,
    workspace,
)

DIRECTORY_CLASS = "port_authority_official_directory"


def _write_statement(ws: Workspace, sid: str, **fields) -> pathlib.Path:
    """Persist a raw statement record, bypassing the editor entirely."""
    path = pathlib.Path(ws.editor.path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    record = {
        "statement_id": sid,
        "entity_id": "port:unlocode:ZZTEST",
        "question_id": ELIGIBLE_QUESTION,
        "statement_type": ELIGIBLE_TYPE,
        "value": "Persisted Claim",
        "artifact_id": HELD_ARTIFACT,
        "locator": "persisted",
        "read_by": "importer",
        "read_on": "2026-08-31",
        "method": "DIRECT",
        "derivation": "LOCAL",
        "evidence_event_ids": [],
        "evidence_condition": "SUPPORTED",
        "human_review_state": "APPROVED",
        "publish_status": "PUBLISH_ALLOWED",
    }
    record.update(fields)
    raw[sid] = record
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


# -- the read boundary -------------------------------------------------------

def test_persisted_publication_with_unresolvable_evidence_is_not_served(workspace):
    """The review's central finding: stored axes were trusted at read time."""
    path = _write_statement(workspace, "STM-GHOST",
                            evidence_event_ids=["EVT-DOES-NOT-EXIST"])
    reloaded = Workspace(str(path.parents[1]))

    ghost = reloaded.editor.get("STM-GHOST")
    assert ghost.publish_status is PublishStatus.PUBLISH_BLOCKED
    assert "STM-GHOST" in reloaded.editor.demoted_on_load
    assert is_canonical_statement_admitted(ghost)[0] is False
    assert reloaded.engine.answer("port:unlocode:ZZTEST", ELIGIBLE_QUESTION).known is False


def test_tampered_artifact_withdraws_publication_at_load(workspace):
    """Bytes that no longer match their digest cannot keep a claim published."""
    stmt = _draft(workspace)
    _attach_real_event(workspace, stmt.statement_id)
    _approve(workspace, stmt.statement_id)
    _publish(workspace, stmt.statement_id)

    root = pathlib.Path(workspace.editor.path).parents[1]
    assert Workspace(str(root)).editor.get(stmt.statement_id).publish_status \
        is PublishStatus.PUBLISH_ALLOWED

    pathlib.Path(workspace.registry.resolve_path(HELD_ARTIFACT)).write_bytes(b"substituted")

    assert Workspace(str(root)).editor.get(stmt.statement_id).publish_status \
        is PublishStatus.PUBLISH_BLOCKED


def test_legacy_published_string_cannot_restore_truth(workspace):
    path = _write_statement(workspace, "STM-LEGACY")
    raw = json.loads(path.read_text(encoding="utf-8"))
    del raw["STM-LEGACY"]["publish_status"]
    del raw["STM-LEGACY"]["human_review_state"]
    del raw["STM-LEGACY"]["evidence_condition"]
    raw["STM-LEGACY"]["review_state"] = "PUBLISHED"
    path.write_text(json.dumps(raw), encoding="utf-8")

    legacy = Workspace(str(path.parents[1])).editor.get("STM-LEGACY")
    assert legacy.human_review_state is HumanReviewState.APPROVED
    assert legacy.publish_status is PublishStatus.PUBLISH_BLOCKED


# -- the engine write boundary ----------------------------------------------

def _writing_engine(ws: Workspace):
    from timonelo.evidence.engine import TruthEngine as WritingTruthEngine

    return WritingTruthEngine(ws.questions, ws.events, ws.registry)


def test_add_statement_cannot_inject_forged_publication(workspace):
    from timonelo.evidence.engine import Statement as EStatement

    engine = _writing_engine(workspace)
    real_event = workspace.editor.get("STM-0392").evidence_event_ids[0]
    forged = EStatement(
        statement_id="S-FORGED", entity_id="port:unlocode:ZZINJ",
        question_id=ELIGIBLE_QUESTION, statement_type=ELIGIBLE_TYPE,
        value="Injected Truth", artifact_id=HELD_ARTIFACT, locator="x",
        read_by="x", read_on="2026-08-31", method=Method.DIRECT,
        evidence_event_ids=(real_event,),
        evidence_condition=EvidenceCondition.SUPPORTED,
        human_review_state=HumanReviewState.APPROVED,
        publish_status=PublishStatus.PUBLISH_ALLOWED,
    )
    with pytest.raises(ValueError, match="not admitted"):
        engine.add_statement(forged)
    assert "S-FORGED" not in engine._statements


def test_add_statement_still_accepts_non_authoritative_drafts(workspace):
    """Draft working data is allowed in; only authority is gated."""
    from timonelo.evidence.engine import Statement as EStatement

    engine = _writing_engine(workspace)
    real_event = workspace.editor.get("STM-0392").evidence_event_ids[0]
    engine.add_statement(EStatement(
        statement_id="S-DRAFT", entity_id="port:unlocode:ZZDRAFT",
        question_id=ELIGIBLE_QUESTION, statement_type=ELIGIBLE_TYPE,
        value="Draft", artifact_id=HELD_ARTIFACT, locator="x",
        read_by="x", read_on="2026-08-31", method=Method.DIRECT,
        evidence_event_ids=(real_event,),
    ))
    assert "S-DRAFT" in engine._statements


# -- publication permission --------------------------------------------------

def test_publication_permission_is_enforced(workspace):
    """R1 removed `authority.is_publishable` and left no owner on that path."""
    ok, _ = authority.is_publishable(ELIGIBLE_TYPE, DIRECTORY_CLASS)
    assert ok, "precondition: this type/class pair is normally publishable"

    stmt = _draft(workspace)
    _attach_real_event(workspace, stmt.statement_id)
    _approve(workspace, stmt.statement_id)

    saved = authority.DOCUMENT_CLASSES[DIRECTORY_CLASS]
    authority.DOCUMENT_CLASSES[DIRECTORY_CLASS] = replace(
        saved, use_permission=authority.UsePermission.INTERNAL_ONLY)
    try:
        with pytest.raises(EditorError, match="NOT_PUBLISHABLE_BY_PERMISSION"):
            _publish(workspace, stmt.statement_id)
    finally:
        authority.DOCUMENT_CLASSES[DIRECTORY_CLASS] = saved


def test_undeclared_document_class_cannot_be_shown_to_be_publishable(workspace):
    stmt = _draft(workspace)
    _attach_real_event(workspace, stmt.statement_id)
    saved = authority.DOCUMENT_CLASSES.pop(DIRECTORY_CLASS)
    try:
        codes = _admission(
            workspace, _supported(workspace.editor.get(stmt.statement_id))
        ).reason_codes
        assert PublicationRejection.NOT_PUBLISHABLE_BY_PERMISSION in codes
    finally:
        authority.DOCUMENT_CLASSES[DIRECTORY_CLASS] = saved


# -- evidence must support the claim ----------------------------------------

@pytest.mark.parametrize(
    "field,value",
    [("entity_id", "port:unlocode:JPTYO"),
     ("value", "Something Else Entirely"),
     ("question_id", "Q-0023")],
)
def test_evidence_must_correspond_to_the_claim(workspace, field, value):
    """A Barcelona observation cannot support an unrelated statement."""
    bcn = workspace.editor.get("STM-0392")
    mismatch = _supported(replace(bcn, statement_id="S-MISMATCH", **{field: value}))
    codes = _admission(workspace, mismatch).reason_codes
    assert PublicationRejection.EVIDENCE_DOES_NOT_SUPPORT_CLAIM in codes


def test_matching_evidence_still_admits(workspace):
    """The binding must not reject honest support."""
    assert _admission(workspace, workspace.editor.get("STM-0392")).admitted is True


def test_json_round_tripped_values_still_agree():
    """`14` and `"14"` are the same observation through a JSON store."""
    from timonelo.evidence.publication import _values_agree

    assert _values_agree(14, "14") is True
    assert _values_agree(" Tokyo ", "Tokyo") is True
    assert _values_agree("Tokyo", "Osaka") is False
    assert _values_agree(None, "Tokyo") is False


# -- rule hashes -------------------------------------------------------------

@pytest.mark.parametrize(
    "bad", ["", "x", "z" * 64, "a" * 63, "a" * 65, None, "0" * 64, 12345])
def test_invalid_rule_hashes_are_refused(workspace, bad):
    """Rules are content-addressed (ADR-0003 §3); truthiness is not a contract."""
    assert is_valid_rule_hash(bad) is False

    parent = workspace.editor.get("STM-0392")
    child = _supported(replace(
        parent, statement_id="S-RH", method=Method.INFERRED,
        input_statement_ids=(parent.statement_id,), rule_hash=bad,
        evidence_event_ids=()))
    assert PublicationRejection.INFERRED_INVALID_RULE_HASH in _admission(workspace, child).reason_codes


def test_valid_rule_hash_is_accepted(workspace):
    real = hashlib.sha256(b"timonelo.rules.test:v1").hexdigest()
    assert is_valid_rule_hash(real) is True
    assert is_valid_rule_hash(real.upper()) is True

    parent = workspace.editor.get("STM-0392")
    child = _supported(replace(
        parent, statement_id="S-RH-OK", method=Method.INFERRED,
        input_statement_ids=(parent.statement_id,), rule_hash=real,
        evidence_event_ids=()))
    assert _admission(workspace, child).admitted is True


# -- inference depth ---------------------------------------------------------

def test_deep_inference_chain_fails_with_a_verdict_not_a_crash(workspace):
    """2000 levels used to raise RecursionError instead of answering."""
    rule = hashlib.sha256(b"deep").hexdigest()
    base = workspace.editor.get("STM-0392")
    chain = {}
    previous = base.statement_id
    for index in range(2000):
        sid = f"S-DEEP-{index}"
        chain[sid] = _supported(replace(
            base, statement_id=sid, method=Method.INFERRED,
            input_statement_ids=(previous,), rule_hash=rule, evidence_event_ids=()))
        previous = sid

    everything = dict(workspace.editor._by_id)
    everything.update(chain)
    result = evaluate_statement_publication_admission(
        chain[previous], events=workspace.events, registry=workspace.registry,
        questions=workspace.questions, statements_by_id=everything)
    assert result.admitted is False
    assert PublicationRejection.INFERRED_CLOSURE_TOO_DEEP in result.reason_codes


def test_self_referential_inference_terminates(workspace):
    base = workspace.editor.get("STM-0392")
    looped = _supported(replace(
        base, statement_id="S-LOOP", method=Method.INFERRED,
        input_statement_ids=("S-LOOP",),
        rule_hash=hashlib.sha256(b"loop").hexdigest(), evidence_event_ids=()))
    everything = dict(workspace.editor._by_id)
    everything["S-LOOP"] = looped
    result = evaluate_statement_publication_admission(
        looped, events=workspace.events, registry=workspace.registry,
        questions=workspace.questions, statements_by_id=everything)
    assert result.admitted is False
    assert PublicationRejection.INFERRED_CIRCULAR_CLOSURE in result.reason_codes


def test_real_inferred_statements_in_the_store_remain_admitted(workspace):
    """The repository's own INFERRED voyage statements must survive."""
    by_id = dict(workspace.editor._by_id)
    for sid in ("STM-0406", "STM-0409"):
        statement = by_id[sid]
        assert statement.method is Method.INFERRED
        result = evaluate_statement_publication_admission(
            statement, events=workspace.events, registry=workspace.registry,
            questions=workspace.questions, statements_by_id=by_id)
        assert result.admitted is True, result.summary()


# -- private-source convergence ---------------------------------------------

def test_private_source_policy_matches_the_gatekeeper(workspace):
    """Both boundaries must reach the same verdict on the same statement."""
    statement = workspace.editor.get("STM-0403")
    admission = evaluate_statement_publication_admission(
        statement, events=workspace.events, registry=workspace.registry,
        questions=workspace.questions,
        statements_by_id=dict(workspace.editor._by_id))

    gate = EvidenceGatekeeper.from_workspace(workspace).evaluate_publish_gate()
    assert admission.admitted is True
    assert [r for r in gate.reasons if "PRIVATE" in r] == []


# -- the SUPPORTED axis and fixture integrity -------------------------------

def test_caller_set_supported_confers_no_truth(workspace):
    """SUPPORTED is still caller-settable; it just buys nothing."""
    stmt = _draft(workspace, entity="port:unlocode:ZZSUPP")
    workspace.editor.set_evidence_condition(
        stmt.statement_id, EvidenceCondition.SUPPORTED,
        actor="curator.one", occurred_on="2026-08-31")

    asserted = workspace.editor.get(stmt.statement_id)
    assert asserted.evidence_condition is EvidenceCondition.SUPPORTED
    assert asserted.publish_status is PublishStatus.PUBLISH_BLOCKED
    assert is_canonical_statement_admitted(asserted)[0] is False
    assert workspace.engine.answer("port:unlocode:ZZSUPP", ELIGIBLE_QUESTION).known is False
    assert _admission(workspace, asserted).admitted is False


def test_fixtures_cannot_manufacture_evidence_from_the_claim():
    """`back_with_evidence` must require the observation to be stated."""
    import inspect

    from tests import evidence_fixtures

    signature = inspect.signature(evidence_fixtures.back_with_evidence)
    for required in ("observed_value", "locator"):
        assert signature.parameters[required].default is inspect.Parameter.empty, (
            f"{required} must be explicit, never inferred from the claim")
    assert "observed_value=statement.value" not in inspect.getsource(evidence_fixtures)
