"""Controlled offline apply: genuine gates, isolated Git repositories, no real approvals."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import shutil

import pytest

from timonelo.canonical import canonical_dump
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.questions import Question, QuestionRegistry
from timonelo.evidence.workspace import Workspace
from timonelo.factory.canonical_apply import (
    ApplyError, apply_candidate, prepare_candidate, recover_interrupted_apply,
    rollback_candidate, operation_binding, inspect_historical_manifest,
)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / 'checkout'
    root.mkdir()
    ws = Workspace(str(root / 'evidence'))
    source = root / 'source.txt'
    source.write_text('Synthetic fixture: Test venue Deck 5. Not real vessel evidence.')
    art = ws.registry.register(str(source), 'cruise_line_deck_plan', '2026-11-04',
                               'synthetic test fixture', subject_vessels=['IMO9760524'])
    questions = QuestionRegistry('test')
    questions.register(Question('Q-0016', 'venue', 'deck.venue_present'))
    questions.save(str(root / 'evidence/registry/questions.json'))
    canonical_dump({}, str(root / 'evidence/statements/statements.json'))
    canonical_dump([], str(root / 'evidence/events/events.json'))
    canonical_dump([], str(root / 'evidence/reviews/log.json'))
    canonical_dump({'conflicts': {}, 'history': [], 'detection_runs': []},
                   str(root / 'evidence/reviews/conflicts.json'))
    canonical_dump({'slug': 'msc-bellissima', 'imo_number': {'value': '9760524'}},
                   str(root / 'knowledge/ships/msc-bellissima/identity.json'))
    git(root, 'init', '-q')
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
        '-c', 'core.autocrlf=false', 'commit', '-qm', 'Synthetic test baseline')
    create = dict(entity_id='venue:MSC-BELLISSIMA:test', question_id='Q-0016',
                  statement_type='deck.venue_present', value=[5], artifact_id=art.artifact_id,
                  locator='Synthetic test line 1', page=1, read_by='Fixture reader',
                  read_on='2026-11-04', evidence_event_ids=['EVT-FIXTURE'])
    event = EvidenceEvent('EVT-FIXTURE', art.sha256, create['locator'], create['entity_id'],
                          'Q-0016', [5], 'Fixture reader', '2026-11-04').to_dict()
    op = {'statement_id': 'STM-0001', 'create': create, 'event': event,
          'target_slug': 'msc-bellissima', 'target_imo': 'IMO9760524'}
    op['decision'] = {'binding_sha256': operation_binding(op), 'decision': 'APPROVE',
                      'actor': 'Fixture independent reviewer', 'occurred_on': '2026-11-04',
                      'note': 'Synthetic fixture approval, not human authorization for production.'}
    return root, op


def prepare(root, op):
    return prepare_candidate(root, [op], baseline_commit=git(root, 'rev-parse', 'HEAD'))


def authorize(plan):
    return {'manifest_sha256': plan['manifest_sha256'], 'actor': 'Fixture operator',
            'occurred_on': '2026-11-04', 'instruction': 'Synthetic fixture offline apply.'}


def test_replay_is_deterministic_and_preserves_store(repository):
    root, op = repository
    before = digest(root / 'evidence/statements/statements.json')
    plan = prepare(root, op)
    assert prepare(root, op) == plan
    assert digest(root / 'evidence/statements/statements.json') == before
    with pytest.raises(ApplyError, match='OFFLINE'):
        apply_candidate(root, plan, authorize(plan))
    audit = apply_candidate(root, plan, authorize(plan), offline=True)
    ws = Workspace(str(root / 'evidence'))
    assert ws.editor.is_currently_authoritative(ws.editor.get('STM-0001'))
    assert (audit / 'manifest.json').is_file()
    assert (audit / 'authorization.json').is_file()
    assert not (root / '.canonical-apply.lock').exists()
    assert (root / '.canonical-generation').is_file()
    with pytest.raises(ApplyError, match='STALE'):
        apply_candidate(root, plan, authorize(plan), offline=True)


@pytest.mark.parametrize('kind', ['head', 'bytes', 'addition', 'lock', 'manifest', 'authorization'])
def test_stale_concurrent_and_tampered_inputs_refuse(repository, kind):
    root, op = repository
    plan = prepare(root, op)
    auth = authorize(plan)
    if kind == 'head':
        git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
            'commit', '--allow-empty', '-qm', 'concurrent change')
    elif kind == 'bytes':
        (root / 'source.txt').write_text('changed')
    elif kind == 'addition':
        (root / 'evidence/new-input.txt').write_text('new')
    elif kind == 'lock':
        (root / '.canonical-apply.lock').write_text('another transaction')
    elif kind == 'manifest':
        plan['operations'][0]['create']['value'] = [6]
    else:
        auth['manifest_sha256'] = 'bad'
    before = digest(root / 'evidence/statements/statements.json')
    with pytest.raises(ApplyError):
        apply_candidate(root, plan, auth, offline=True)
    assert digest(root / 'evidence/statements/statements.json') == before


def test_unbound_approval_and_global_collision_refuse(repository):
    root, op = repository
    changed = deepcopy(op)
    changed['create']['value'] = [6]
    with pytest.raises(ApplyError, match='DECISION_BINDING'):
        prepare(root, changed)
    with pytest.raises(ApplyError, match='COLLISION'):
        prepare_candidate(root, [op, op], baseline_commit=git(root, 'rev-parse', 'HEAD'))


@pytest.mark.parametrize('value', [[5], [6]])
@pytest.mark.parametrize('existing', [False, True, 'artifact_digest'])
def test_normalized_entity_question_collisions_refuse_before_replay_writes(repository, monkeypatch, value, existing):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    other = deepcopy(op)
    other['statement_id'] = 'STM-0002'
    other['create']['entity_id'] = op['create']['entity_id'].lower()
    other['create']['value'] = value
    other['create']['evidence_event_ids'] = ['EVT-SECOND']
    other['event'].update(event_id='EVT-SECOND', entity_id=other['create']['entity_id'], observed_value=value)
    other['decision']['binding_sha256'] = operation_binding(other)
    if existing:
        if existing == 'artifact_digest':
            op['create']['artifact_id'] = op['event']['artifact_sha256']
            op['decision']['binding_sha256'] = operation_binding(op)
        plan = prepare(root, op)
        apply_candidate(root, plan, authorize(plan), offline=True)
        operations = [other]
    else:
        operations = [op, other]
    before = {p: (root / p).read_bytes() for p in module.STORE_FILES}
    # A conflicting batch must fail before even its first private event write.
    def forbidden_append(*args, **kwargs):
        pytest.fail('preflight must reject before appending a private event')
    from timonelo.evidence.events import EvidenceEventLog
    monkeypatch.setattr(EvidenceEventLog, 'append', forbidden_append)
    with pytest.raises(ApplyError, match='NORMALIZED_CLAIM_'):
        prepare_candidate(root, operations, baseline_commit=git(root, 'rev-parse', 'HEAD'))
    assert all((root / p).read_bytes() == b for p, b in before.items())


@pytest.mark.parametrize('alias', ['  FIXTURE   READER ', '\uff26ixture reader', 'Fixture\u00a0reader'])
def test_reviewer_alias_cannot_approve_own_reading(repository, alias):
    root, op = repository
    op['decision']['actor'] = alias
    with pytest.raises(ApplyError, match='INDEPENDENT'):
        prepare(root, op)


def test_generation_change_during_preparation_refuses(repository, monkeypatch):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    replay = module._replay
    def racing_replay(*args):
        result = replay(*args)
        (root / '.canonical-generation').write_text('concurrent completed transaction')
        return result
    monkeypatch.setattr(module, '_replay', racing_replay)
    with pytest.raises(ApplyError, match='SOURCE_CHANGED'):
        prepare(root, op)


def test_failed_install_restores_exact_bytes_and_retains_decisions(repository, monkeypatch):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    before = {p: (root / p).read_bytes() for p in module.STORE_FILES}
    replace = module._replace_file
    calls = []
    def fail_second(path, data):
        calls.append(path)
        if len(calls) == 2:
            raise OSError('injected disk failure')
        replace(path, data)
    monkeypatch.setattr(module, '_replace_file', fail_second)
    with pytest.raises(OSError, match='disk failure'):
        apply_candidate(root, plan, authorize(plan), offline=True)
    assert all((root / p).read_bytes() == data for p, data in before.items())
    assert not (root / '.canonical-apply.lock').exists()
    assert list((root / '.canonical-apply-audit').rglob('authorization.json'))


def test_uncooperative_root_mutation_keeps_gate_closed_without_erasing_edit(repository, monkeypatch):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    replace = module._replace_file
    def mutate_root(path, data):
        replace(path, data)
        if path.name == 'events.json':
            (root / 'source.txt').write_text('foreign concurrent edit')
    monkeypatch.setattr(module, '_replace_file', mutate_root)
    with pytest.raises(ApplyError, match='RECOVERY_CONCURRENT_CHANGE'):
        apply_candidate(root, plan, authorize(plan), offline=True)
    assert (root / '.canonical-apply.lock').exists()
    assert (root / 'source.txt').read_text() == 'foreign concurrent edit'


def test_process_crash_requires_recovery_before_readers_return(repository, monkeypatch):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    before = {p: (root / p).read_bytes() for p in module.STORE_FILES}
    replace = module._replace_file
    calls = []
    def crash(path, data):
        calls.append(path)
        if len(calls) == 2:
            raise KeyboardInterrupt('simulated process death')
        replace(path, data)
    monkeypatch.setattr(module, '_replace_file', crash)
    with pytest.raises(KeyboardInterrupt):
        apply_candidate(root, plan, authorize(plan), offline=True)
    assert (root / '.canonical-apply.lock').exists()
    monkeypatch.setattr(module, '_replace_file', replace)
    recover_interrupted_apply(root, offline=True)
    assert all((root / p).read_bytes() == data for p, data in before.items())
    assert not (root / '.canonical-apply.lock').exists()


@pytest.mark.parametrize('competing', ['reentrant', 'stale'])
def test_recovery_claim_excludes_competing_recovery(repository, monkeypatch, competing):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    before = {p: (root / p).read_bytes() for p in module.STORE_FILES}
    replace = module._replace_file
    def crash(path, data):
        raise KeyboardInterrupt('fixture interrupted install')
    monkeypatch.setattr(module, '_replace_file', crash)
    with pytest.raises(KeyboardInterrupt):
        apply_candidate(root, plan, authorize(plan), offline=True)
    monkeypatch.setattr(module, '_replace_file', replace)
    if competing == 'stale':
        (root / '.canonical-apply-recovery.lock').write_text('stale claim')
        with pytest.raises(ApplyError, match='CONCURRENT_RECOVERY'):
            recover_interrupted_apply(root, offline=True)
        assert (root / module.LOCK).exists()
        assert (root / '.canonical-apply-recovery.lock').exists()
    else:
        calls = []
        def competing_recovery(path, data):
            if not calls:
                calls.append(path)
                with pytest.raises(ApplyError, match='CONCURRENT_RECOVERY'):
                    recover_interrupted_apply(root, offline=True)
                assert (root / module.LOCK).exists()
            replace(path, data)
        monkeypatch.setattr(module, '_replace_file', competing_recovery)
        recover_interrupted_apply(root, offline=True)
        assert calls
        assert not (root / module.LOCK).exists()
    assert all((root / p).read_bytes() == b for p, b in before.items())


def test_post_apply_rollback_quarantines_without_erasing_events_or_approval(repository):
    root, op = repository
    plan = prepare(root, op)
    audit = apply_candidate(root, plan, authorize(plan), offline=True)
    events = (root / 'evidence/events/events.json').read_bytes()
    rollback_candidate(root, audit, actor='Fixture operator', occurred_on='2026-11-04',
                       note='Synthetic fixture corrective withdrawal.', offline=True)
    assert (root / 'evidence/events/events.json').read_bytes() == events
    ws = Workspace(str(root / 'evidence'))
    stmt = ws.editor.get('STM-0001')
    assert not ws.editor.is_currently_authoritative(stmt)
    assert stmt.human_review_state.value == 'APPROVED'
    assert any(e.to_state == 'APPROVED' for e in ws.reviews.history('STM-0001'))
    assert ws.reviews.history('STM-0001')[-1].to_state == 'CONDITION:UNKNOWN'


@pytest.mark.parametrize('action', ['recover', 'rollback'])
@pytest.mark.parametrize('tamper', ['manifest', 'completion', 'after'])
def test_completed_journal_tampering_refuses(repository, action, tamper):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    audit = apply_candidate(root, plan, authorize(plan), offline=True)
    if tamper == 'manifest':
        changed = deepcopy(plan)
        changed['operations'] = []
        canonical_dump(changed, str(audit / 'manifest.json'))
    elif tamper == 'completion':
        canonical_dump({'manifest_sha256': 'altered'}, str(audit / 'complete.json'))
    else:
        (audit / 'after' / module.STORE_FILES[3]).write_text('{}')
    before = {p: (root / p).read_bytes() for p in module.STORE_FILES}
    if action == 'recover':
        canonical_dump({'transaction': audit.name}, str(root / module.LOCK))
        with pytest.raises(ApplyError, match='RECOVERY_'):
            recover_interrupted_apply(root, offline=True)
        assert (root / module.LOCK).exists()
    else:
        with pytest.raises(ApplyError, match='RECOVERY_'):
            rollback_candidate(root, audit, actor='Fixture operator', occurred_on='2026-11-04',
                               note='Fixture withdrawal', offline=True)
    assert all((root / p).read_bytes() == b for p, b in before.items())


def test_rollback_generation_change_during_preparation_refuses(repository, monkeypatch):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    audit = apply_candidate(root, plan, authorize(plan), offline=True)
    before = {p: (root / p).read_bytes() for p in module.STORE_FILES}
    states = module._states
    def concurrent_generation(ws):
        result = states(ws)
        (root / module.GENERATION).write_text('concurrent completed transaction')
        return result
    monkeypatch.setattr(module, '_states', concurrent_generation)
    with pytest.raises(ApplyError, match='STALE_BASELINE'):
        rollback_candidate(root, audit, actor='Fixture operator', occurred_on='2026-11-04',
                           note='Fixture withdrawal', offline=True)
    assert all((root / p).read_bytes() == b for p, b in before.items())


def test_untracked_bound_decision_change_refuses(repository):
    root, op = repository
    decision = root / 'untracked-owner-instruction.json'
    decision.write_text('Fixture-only explicit instruction.')
    plan = prepare_candidate(root, [op], baseline_commit=git(root, 'rev-parse', 'HEAD'),
                             bound_input_sha256={decision.name: digest(decision)})
    decision.write_text('different instruction')
    with pytest.raises(ApplyError, match='BOUND_INPUT'):
        apply_candidate(root, plan, authorize(plan), offline=True)


def test_preexisting_raw_statements_and_approvals_are_preserved(repository):
    root, op = repository
    # The legacy loader normalizes this deliberately unknown record in memory.
    # Apply must never write that normalization over its persisted original.
    old = deepcopy(op['create'])
    old.update(statement_id='STM-0001', entity_id='venue:MSC-BELLISSIMA:legacy',
               evidence_event_ids=[], review_state='DRAFT')
    canonical_dump({'STM-0001': old}, str(root / 'evidence/statements/statements.json'))
    op['statement_id'] = 'STM-0002'
    op['decision']['binding_sha256'] = operation_binding(op)
    plan = prepare(root, op)
    apply_candidate(root, plan, authorize(plan), offline=True)
    records = json.loads((root / 'evidence/statements/statements.json').read_bytes())
    assert records['STM-0001'] == old
    assert len(records) == 2


def test_crash_before_journal_ready_is_recoverable(repository, monkeypatch):
    import timonelo.factory.canonical_apply as module
    root, op = repository
    plan = prepare(root, op)
    record = module._record
    def crash(path, value):
        if path.name == 'authorization.json':
            raise KeyboardInterrupt('early crash')
        record(path, value)
    monkeypatch.setattr(module, '_record', crash)
    with pytest.raises(KeyboardInterrupt):
        apply_candidate(root, plan, authorize(plan), offline=True)
    monkeypatch.setattr(module, '_record', record)
    recover_interrupted_apply(root, offline=True)
    assert not (root / '.canonical-apply.lock').exists()
    assert json.loads((root / 'evidence/statements/statements.json').read_bytes()) == {}


def test_historical_inspection_reports_missing_private_output_honestly(tmp_path):
    historical = tmp_path / 'manifest.json'
    canonical_dump({'schema': 'timonelo.canonical-apply-candidate.v1',
                    'private_output': str(tmp_path / 'gone'), 'files': [],
                    'mode': 'REVIEW_ONLY_NOT_APPLIED'}, str(historical))
    report = inspect_historical_manifest(historical, expected_sha256=digest(historical))
    assert report['manifest_bytes_verified']
    assert not report['private_output_available']
    assert not report['frozen_candidate_bytes_recoverable']
    assert not report['historical_output_rebuilt_or_identical']


def test_real_418_statement_baseline_and_artifact_records_survive_isolated_apply(tmp_path):
    source = Path(__file__).resolve().parents[1]
    root = tmp_path / 'real-store-private-copy'
    for folder in ('evidence', 'knowledge'):
        shutil.copytree(source / folder, root / folder)
    old_statements = json.loads((root / 'evidence/statements/statements.json').read_bytes())
    assert len(old_statements) >= 418
    protected = {p.relative_to(root).as_posix(): digest(p)
                 for folder in ('evidence/artifacts', 'knowledge')
                 for p in (root / folder).rglob('*') if p.is_file()}
    old_reviews = json.loads((root / 'evidence/reviews/log.json').read_bytes())
    git(root, 'init', '-q')
    git(root, '-c', 'core.autocrlf=false', 'add', '.')
    git(root, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
        '-c', 'core.autocrlf=false', 'commit', '-qm', 'Isolated existing-store fixture')
    ws = Workspace(str(root / 'evidence'))
    art = ws.registry.get('ART-0001')
    sid = f"STM-{max(int(k.split('-')[1]) for k in old_statements) + 1:04d}"
    create = dict(entity_id='venue:MSC-BELLISSIMA:isolated-synthetic-test-only',
                  question_id='Q-0016', statement_type='deck.venue_present', value=[5],
                  artifact_id=art.artifact_id, locator='SYNTHETIC TEST ONLY, no production observation',
                  read_by='Synthetic test instrument', read_on='2026-11-04',
                  evidence_event_ids=['EVT-ISOLATED-SYNTHETIC-TEST'])
    event = EvidenceEvent('EVT-ISOLATED-SYNTHETIC-TEST', art.sha256, create['locator'],
        create['entity_id'], 'Q-0016', [5], create['read_by'], create['read_on']).to_dict()
    op = dict(statement_id=sid, create=create, event=event,
              target_slug='msc-bellissima', target_imo='IMO9760524')
    op['decision'] = dict(binding_sha256=operation_binding(op), decision='APPROVE',
                          actor='Synthetic independent fixture principal', occurred_on='2026-11-04',
                          note='Synthetic fixture only; never a real human decision.')
    plan = prepare(root, op)
    apply_candidate(root, plan, authorize(plan), offline=True)
    applied = json.loads((root / 'evidence/statements/statements.json').read_bytes())
    assert {sid: applied[sid] for sid in old_statements} == old_statements
    assert all(digest(root / rel) == expected for rel, expected in protected.items())
    assert json.loads((root / 'evidence/reviews/log.json').read_bytes())[:len(old_reviews)] == old_reviews
