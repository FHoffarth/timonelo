"""Adversarial controls against actual batch and publication boundaries."""
from copy import deepcopy
from dataclasses import replace
import json
import shutil

import pytest

from tests.test_evidence_factory_batch import pre_apply_root, inputs, ROOT
from timonelo.factory.evidence_batch import inspect_batch
from timonelo.evidence.workspace import Workspace


def test_foreign_entity_cannot_hide_bellissima_in_another_segment(pre_apply_root, inputs):
    batch, decisions = inputs
    claim = batch['claims'][0]
    claim['entity_id'] = 'venue:msc-grandiosa:msc-bellissima'
    decisions['decisions'][0]['binding'] = deepcopy(claim)
    row = inspect_batch(pre_apply_root, batch, decisions)['claims'][0]
    assert row['status'] == 'BLOCKED'
    assert any('VESSEL' in r or 'ENTITY' in r for r in row['reasons'])


def test_publication_rejects_cross_vessel_artifact_even_with_matching_event(tmp_path):
    shutil.copytree(ROOT / 'evidence', tmp_path / 'evidence')
    ws = Workspace(str(tmp_path / 'evidence'))
    statement = ws.editor.get('STM-0411')
    entity = 'venue:msc-grandiosa:reception-guest-service'
    bad = replace(statement, entity_id=entity)
    ws.events._events = [replace(e, entity_id=entity) if e.event_id in bad.evidence_event_ids else e
                         for e in ws.events.all()]
    verdict = ws.editor.authority.evaluate(bad)
    assert not verdict.admitted
    assert any('VESSEL' in r.value for r in verdict.reason_codes)


def test_prose_cannot_disagree_with_structured_value(pre_apply_root, inputs):
    batch, decisions = inputs
    claim = batch['claims'][0]
    claim['exact_claim'] = claim['exact_claim'].replace('deck(s) 5', 'deck(s) 9')
    decisions['decisions'][0]['binding'] = deepcopy(claim)
    row = inspect_batch(pre_apply_root, batch, decisions)['claims'][0]
    assert row['status'] == 'BLOCKED'
    assert 'CLAIM_TEXT_VALUE_MISMATCH' in row['reasons']


def test_case_variant_selection_is_duplicate(pre_apply_root, inputs):
    batch, decisions = inputs
    batch['claims'] = [deepcopy(batch['claims'][0]), deepcopy(batch['claims'][0])]
    batch['claims'][1]['id'] = 'NEGATIVE-CASE'
    batch['claims'][1]['entity_id'] = batch['claims'][1]['entity_id'].lower()
    plan = inspect_batch(pre_apply_root, batch, decisions)
    assert all(r['status'] == 'BLOCKED' for r in plan['claims'])
    assert all('DUPLICATE_SELECTED_CLAIM' in r['reasons'] for r in plan['claims'])


def test_batch_contradiction_blocks_both_sides(pre_apply_root, inputs):
    batch, decisions = inputs
    batch['claims'] = [deepcopy(batch['claims'][0]), deepcopy(batch['claims'][0])]
    batch['claims'][1]['id'] = 'NEGATIVE-CONFLICT'
    batch['claims'][1]['value'] = [6]
    plan = inspect_batch(pre_apply_root, batch, decisions)
    assert all('CONTRADICTORY_SELECTED_CLAIM' in r['reasons'] for r in plan['claims'])
    assert all(r['status'] == 'BLOCKED' for r in plan['claims'])


def test_reader_case_alias_is_not_a_second_human(pre_apply_root, inputs):
    from timonelo.factory.evidence_batch import READER
    batch, decisions = inputs
    decisions['reviewer'] = '  ' + READER.upper() + '  '
    plan = inspect_batch(pre_apply_root, batch, decisions)
    assert all('REVIEWER_EQUALS_SOURCE_READER' in r['reasons'] for r in plan['claims'])


def test_forged_owner_decision_cannot_authorize_new_binding(pre_apply_root, inputs):
    batch, decisions = inputs
    claim = batch['claims'][0]
    claim['name'] = 'Invented Guest Service Alias'
    claim['exact_claim'] = claim['exact_claim'].replace('Guest Service', claim['name'])
    decisions['decisions'][0]['binding'] = deepcopy(claim)
    row = inspect_batch(pre_apply_root, batch, decisions)['claims'][0]
    assert row['status'] == 'BLOCKED'
    assert 'UNREGISTERED_HUMAN_APPROVAL' in row['reasons']


def test_retained_authority_refuses_transaction_and_stays_stale_after_commit(tmp_path):
    shutil.copytree(ROOT / 'evidence', tmp_path / 'evidence')
    ws = Workspace(str(tmp_path / 'evidence'))
    statement = ws.editor.get('STM-0411')
    assert ws.editor.authority.evaluate(statement).admitted
    lock = tmp_path / '.canonical-apply.lock'
    lock.mkdir()
    assert not ws.editor.authority.evaluate(statement).admitted
    with pytest.raises(ValueError, match='CANONICAL'):
        Workspace(str(tmp_path / 'evidence'))
    (tmp_path / '.canonical-generation').write_text('next-revision', encoding='utf8')
    lock.rmdir()
    assert not ws.editor.authority.evaluate(statement).admitted
    assert Workspace(str(tmp_path / 'evidence')).editor.authority.evaluate(statement).admitted


def test_missing_identity_quarantine_policy_fails_closed(tmp_path, monkeypatch):
    from timonelo.evidence import vessel_ownership
    monkeypatch.setattr(vessel_ownership, '__file__', str(tmp_path / 'vessel_ownership.py'))
    with pytest.raises(ValueError, match='IDENTITY_POLICY'):
        vessel_ownership.canonical_vessel('msc-meraviglia')


@pytest.mark.parametrize('stale', [False, True])
def test_direct_publish_and_canonical_writers_cannot_bypass_reader_gate(tmp_path, stale):
    from timonelo.evidence.models import EvidenceCondition
    from timonelo.evidence.publication import evaluate_statement_publication_admission
    shutil.copytree(ROOT / 'evidence', tmp_path / 'evidence')
    ws = Workspace(str(tmp_path / 'evidence'))
    files = ['statements/statements.json', 'events/events.json', 'reviews/log.json', 'reviews/conflicts.json']
    before = {p: (tmp_path / 'evidence' / p).read_bytes() for p in files}
    if stale:
        (tmp_path / '.canonical-generation').write_text('changed', encoding='utf8')
    else:
        (tmp_path / '.canonical-apply.lock').mkdir()
    s = ws.editor.get('STM-0411')
    assert not evaluate_statement_publication_admission(s, events=ws.events, registry=ws.registry,
        questions=ws.questions, statements_by_id={x.statement_id: x for x in ws.editor.all()}).admitted
    with pytest.raises(ValueError, match='CANONICAL'):
        ws.editor.publish(s.statement_id, actor='Independent test operator', occurred_on='2026-11-05')
    with pytest.raises(ValueError, match='CANONICAL'):
        ws.editor.set_evidence_condition(s.statement_id, EvidenceCondition.UNKNOWN,
                                       actor='Test operator', occurred_on='2026-11-05')
    for writer in [ws.events, ws.reviews, ws.conflicts, ws.editor]:
        with pytest.raises(ValueError, match='CANONICAL'):
            writer._flush()
    assert {p: (tmp_path / 'evidence' / p).read_bytes() for p in files} == before


def test_digest_store_attribution_is_explicit_and_cannot_be_reassigned(tmp_path):
    from timonelo.evidence.artifacts import ArtifactStore
    p = tmp_path / 'fixture.txt'
    p.write_text('Synthetic test source; not production evidence', encoding='utf8')
    store = ArtifactStore(str(tmp_path / 'artifacts'))
    artifact = store.add(str(p), 'cruise_line_deck_plan', '2026-11-05', 'test fixture',
                         subject_vessels=['IMO9760524'])
    assert artifact.establishes_vessel('IMO9760524')
    assert not artifact.establishes_vessel('IMO9803613')
    with pytest.raises(ValueError, match='attribution'):
        store.add(str(p), 'cruise_line_deck_plan', '2026-11-05', 'test fixture',
                  subject_vessels=['IMO9803613'])


def test_direct_publisher_cannot_impersonate_an_independent_reader_alias(tmp_path):
    shutil.copytree(ROOT / 'evidence', tmp_path / 'evidence')
    ws = Workspace(str(tmp_path / 'evidence'))
    s = ws.editor.get('STM-0411')
    with pytest.raises(ValueError, match='cannot also publish|cannot also|cannot.*publish'):
        ws.editor.publish(s.statement_id, actor='  ' + s.read_by.upper() + '  ', occurred_on='2026-11-05')


def test_structured_deck_must_match_the_held_source_column(pre_apply_root, inputs):
    batch, decisions = inputs
    c = batch['claims'][0]
    c['value'] = [6]
    c['exact_claim'] = c['exact_claim'].replace('deck(s) 5', 'deck(s) 6')
    decisions['decisions'][0]['binding'] = deepcopy(c)  # adversarial fixture, not an owner approval
    row = inspect_batch(pre_apply_root, batch, decisions)['claims'][0]
    assert row['status'] == 'BLOCKED'
    assert 'SOURCE_DECK_COLUMN_MISMATCH' in row['reasons']


def test_owner_approval_cannot_erase_recorded_source_origin_limits(pre_apply_root, inputs):
    batch, decisions = inputs
    batch['origin_limit'] = 'Independently verified historical download'  # false adversarial input
    plan = inspect_batch(pre_apply_root, batch, decisions)
    assert all(r['status'] == 'BLOCKED' for r in plan['claims'])
    assert all('SOURCE_ORIGIN_LIMITATION_MISMATCH' in r['reasons'] for r in plan['claims'])
