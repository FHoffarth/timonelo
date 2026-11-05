"""Governed, append-only canonical additions in an explicitly offline checkout.

This is not a general store overlay. Every addition is replayed through the
editor and independently bound review record. Existing persisted records are
copied verbatim as JSON values, including legacy axes the editor normalizes.
Four-file replacement is NOT filesystem-atomic. The offline boundary and reader
gate exclude supported authority readers until all files and the epoch are
durable. Raw file consumers and uncooperative writers must be stopped by the
operator. A crash leaves the gate closed until explicit recovery.

Approval/authorization inputs record actual instructions supplied by a trusted
operator; hashes bind content, they do not authenticate a human identity.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

from timonelo.canonical import canonical_dumps
from timonelo.evidence.events import EvidenceEvent
from timonelo.evidence.workspace import Workspace
from timonelo.ontology.models import EvidenceCondition, HumanReviewState

STORE_FILES = (
    'evidence/events/events.json', 'evidence/reviews/conflicts.json',
    'evidence/reviews/log.json', 'evidence/statements/statements.json',
)
LOCK = '.canonical-apply.lock'
RECOVERY_LOCK = '.canonical-apply-recovery.lock'
GENERATION = '.canonical-generation'
AUDIT = '.canonical-apply-audit'


class ApplyError(ValueError):
    pass


def _bytes(value):
    # Reject non-finite numbers even though legacy canonical_dumps permits them.
    json.dumps(value, allow_nan=False)
    return (canonical_dumps(value) + '\n').encode('utf8')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def operation_binding(operation):
    """Bind the entire proposed observation/statement/target, excluding decision."""
    return _sha(_bytes({k: v for k, v in operation.items() if k != 'decision'}))


def _git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args],
                                   stderr=subprocess.PIPE).decode('utf8').strip()


def _path(root, relative):
    path = root / relative
    if not isinstance(relative, str) or path.resolve() != path.absolute():
        raise ApplyError('UNSAFE_PATH_OR_SYMLINK')
    if root not in path.resolve().parents:
        raise ApplyError('PATH_OUTSIDE_CHECKOUT')
    return path


def _inventory(root):
    tracked = _git(root, 'ls-files', '-z').split('\0')
    names = {p for p in tracked if p and not p.startswith(AUDIT + '/')
             and p not in (LOCK, RECOVERY_LOCK, GENERATION)}
    for folder in ('evidence', 'knowledge', 'src'):
        names.update(p.relative_to(root).as_posix() for p in (root / folder).rglob('*') if p.is_file())
    return {name: _sha(_path(root, name).read_bytes()) if _path(root, name).is_file() else None
            for name in sorted(names)}


def _load(root, rel):
    return json.loads(_path(root, rel).read_bytes())


def _states(ws):
    result = {}
    for statement in ws.editor.all():
        verdict = ws.editor.authority.evaluate(statement)
        result[statement.statement_id] = [statement.to_dict(), verdict.admitted,
                                         [r.value for r in verdict.reason_codes]]
    return result


def _extend(before, after):
    """Keep immutable existing values, accept only appended members."""
    if isinstance(before, list) and isinstance(after, list):
        if after[:len(before)] != before:
            raise ApplyError('APPEND_ONLY_VIOLATION')
    elif isinstance(before, dict) and isinstance(after, dict):
        if any(k not in after or before[k] != after[k] for k in before):
            raise ApplyError('PRESERVED_RECORD_CHANGED')
    else:
        raise ApplyError('STORE_SHAPE_CHANGED')
    return after


def _replay(root, operations):
    from timonelo.evidence.vessel_ownership import validate_ownership, normalized_principal, entity_key
    from timonelo.evidence.conflicts import values_disagree, validity_overlaps

    with tempfile.TemporaryDirectory(prefix='timonelo-governed-replay-') as temporary:
        private = Path(temporary)
        shutil.copytree(root / 'evidence', private / 'evidence')
        if (root / 'knowledge').exists():
            shutil.copytree(root / 'knowledge', private / 'knowledge')
        # A private copy has no canonical reader lock; all gates still run.
        ws = Workspace(str(private / 'evidence'))
        original = _states(ws)
        old = {rel: _load(root, rel) for rel in STORE_FILES}
        ids = set(old[STORE_FILES[3]])
        if any(key != value.get('statement_id') for key, value in old[STORE_FILES[3]].items()):
            raise ApplyError('PREEXISTING_STATEMENT_ID_COLLISION')
        event_ids = {e['event_id'] for e in old[STORE_FILES[0]]}
        if len(event_ids) != len(old[STORE_FILES[0]]):
            raise ApplyError('PREEXISTING_EVENT_ID_COLLISION')
        # Validate the complete batch before any private event/editor write.
        # Case aliases must not create a second claim or evade conflict review.
        seen_ids, seen_events = set(ids), set(event_ids)
        for op in operations:
            if op['statement_id'] in seen_ids or op['event']['event_id'] in seen_events:
                raise ApplyError('GLOBAL_ID_COLLISION')
            seen_ids.add(op['statement_id'])
            seen_events.add(op['event']['event_id'])
        claims = {}
        for op in operations:
            create = op['create']
            key = (entity_key(create['entity_id']), create['question_id'])
            if key in claims:
                reason = 'CONFLICT' if values_disagree(claims[key]['value'], create['value']) else 'DUPLICATE'
                raise ApplyError('NORMALIZED_CLAIM_' + reason)
            claims[key] = create
            for sid in original:
                existing = ws.editor.get(sid)
                if (entity_key(existing.entity_id), existing.question_id) != key:
                    continue
                if not validity_overlaps(existing.valid_from, existing.valid_until,
                                         create.get('valid_from'), create.get('valid_until')):
                    continue
                if values_disagree(existing.value, create['value']):
                    raise ApplyError('NORMALIZED_CLAIM_CONFLICT')
                if (ws.registry.get(existing.artifact_id).sha256 ==
                        ws.registry.get(create['artifact_id']).sha256):
                    raise ApplyError('NORMALIZED_CLAIM_DUPLICATE')
        for op in operations:
            sid, event, create, decision = (op['statement_id'], op['event'], op['create'], op['decision'])
            if sid in ids or event['event_id'] in event_ids:
                raise ApplyError('GLOBAL_ID_COLLISION')
            ids.add(sid)
            event_ids.add(event['event_id'])
            if decision.get('binding_sha256') != operation_binding(op):
                raise ApplyError('DECISION_BINDING_MISMATCH')
            if (decision.get('decision') != 'APPROVE' or
                    not all(isinstance(decision.get(k), str) and decision[k].strip()
                            for k in ('actor', 'occurred_on', 'note')) or
                    normalized_principal(decision['actor']) in
                    (normalized_principal(create['read_by']), normalized_principal(event['observed_by']))):
                raise ApplyError('EXPLICIT_INDEPENDENT_REVIEW_REQUIRED')
            validate_ownership(create['entity_id'], ws.registry.get(create['artifact_id']),
                               target_slug=op['target_slug'], target_imo=op['target_imo'], root=private)
            ws.events.append(EvidenceEvent.from_dict(event))
            stmt = ws.editor.create(**create)
            if stmt.statement_id != sid:
                raise ApplyError('GLOBAL_ID_COLLISION_OR_ALLOCATION_DRIFT')
            ws.editor.set_evidence_condition(sid, EvidenceCondition.SUPPORTED,
                actor=create['read_by'], occurred_on=create['read_on'], note='Bound event admission required at publication.')
            ws.editor.transition(sid, HumanReviewState.UNDER_REVIEW, actor=create['read_by'],
                                 occurred_on=create['read_on'], note='Submit recorded decision.')
            ws.editor.transition(sid, HumanReviewState.APPROVED, actor=decision['actor'],
                                 occurred_on=decision['occurred_on'], note=decision['note'])
            ws.editor.publish(sid, actor=decision['actor'], occurred_on=decision['occurred_on'],
                              note=decision['note'])
            if not ws.editor.authority.evaluate(ws.editor.get(sid)).admitted:
                raise ApplyError('NEW_STATEMENT_NOT_ADMITTED')
        current = _states(ws)
        if {sid: current[sid] for sid in original} != original:
            raise ApplyError('EXISTING_AUTHORITY_CHANGED')
        # Keep every original raw statement. Never export normalized full-store
        # editor serialization back over legacy canonical records.
        additions = {sid: ws.editor.get(sid).to_dict() for sid in ids - set(original)}
        output = {STORE_FILES[3]: {**old[STORE_FILES[3]], **additions}}
        output[STORE_FILES[0]] = _extend(old[STORE_FILES[0]], _load(private, STORE_FILES[0]))
        output[STORE_FILES[2]] = _extend(old[STORE_FILES[2]], _load(private, STORE_FILES[2]))
        conflicts = _load(private, STORE_FILES[1])
        for key in ('conflicts', 'history', 'detection_runs'):
            _extend(old[STORE_FILES[1]][key], conflicts[key])
        # Newly discovered disputes require a separate human resolution flow.
        if conflicts['conflicts'] != old[STORE_FILES[1]]['conflicts']:
            raise ApplyError('NEW_CONFLICT_REQUIRES_REVIEW')
        output[STORE_FILES[1]] = conflicts
        # Re-open the exact proposed on-disk store, not only the private editor.
        for rel, value in output.items():
            _path(private, rel).write_bytes(_bytes(value))
        reopened = Workspace(str(private / 'evidence'))
        if _states(reopened) != current:
            raise ApplyError('EXACT_STORE_AUTHORITY_REPLAY_MISMATCH')
        return {rel: _bytes(value) for rel, value in output.items()}, current


def prepare_candidate(root, operations, *, baseline_commit, bound_input_sha256=None):
    """Read-only deterministic replay; caller must supply the exact Git baseline."""
    root = Path(root).resolve()
    if (root / LOCK).exists():
        raise ApplyError('CONCURRENT_APPLY')
    if _git(root, 'rev-parse', 'HEAD') != baseline_commit:
        raise ApplyError('STALE_GIT_BASELINE')
    if not operations or not isinstance(operations, list):
        raise ApplyError('EMPTY_OR_INVALID_OPERATIONS')
    generation = (root / GENERATION).read_text() if (root / GENERATION).exists() else None
    before = _inventory(root)
    for rel, digest in (bound_input_sha256 or {}).items():
        if _sha(_path(root, rel).read_bytes()) != digest:
            raise ApplyError('BOUND_INPUT_HASH_MISMATCH')
    output, states = _replay(root, operations)
    after_generation = (root / GENERATION).read_text() if (root / GENERATION).exists() else None
    if (_inventory(root) != before or _git(root, 'rev-parse', 'HEAD') != baseline_commit
            or (root / LOCK).exists() or generation != after_generation):
        raise ApplyError('SOURCE_CHANGED_DURING_REPLAY')
    plan = dict(schema='timonelo.governed-canonical-apply.v1', baseline_commit=baseline_commit,
                baseline_sha256=before, operations=deepcopy(operations),
                bound_input_sha256=deepcopy(bound_input_sha256 or {}),
                generation=generation,
                output_sha256={p: _sha(data) for p, data in output.items()},
                authority_sha256=_sha(_bytes(states)),
                read_boundary='OFFLINE_EXCLUSIVE_CHECKOUT_WITH_AUTHORITY_READER_GATE')
    plan['manifest_sha256'] = _sha(_bytes(plan))
    return plan


def _replace_file(path, data):
    """One atomic file replacement. Multi-file consistency is provided by gate."""
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('xb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _record(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())


def _epoch(root):
    _replace_file(root / GENERATION, (uuid.uuid4().hex + '\n').encode('ascii'))


def _check_plan(root, plan):
    expected = plan.get('manifest_sha256')
    if expected != _sha(_bytes({k: v for k, v in plan.items() if k != 'manifest_sha256'})):
        raise ApplyError('MANIFEST_HASH_MISMATCH')
    for rel, expected_hash in plan.get('bound_input_sha256', {}).items():
        path = _path(root, rel)
        if not path.is_file() or _sha(path.read_bytes()) != expected_hash:
            raise ApplyError('BOUND_INPUT_HASH_MISMATCH')
    generation = (root / GENERATION).read_text() if (root / GENERATION).exists() else None
    if (_git(root, 'rev-parse', 'HEAD') != plan['baseline_commit'] or
            _inventory(root) != plan['baseline_sha256'] or generation != plan['generation']):
        raise ApplyError('STALE_BASELINE')


def _offline(offline):
    if offline is not True:
        raise ApplyError('OFFLINE_EXCLUSIVE_CHECKOUT_REQUIRED: stop raw readers and uncooperative writers')


def _transaction(root, plan, authorization, output):
    transaction = uuid.uuid4().hex
    audit = root / AUDIT / transaction
    if (root / RECOVERY_LOCK).exists():
        raise ApplyError('CONCURRENT_RECOVERY: inspect a stale recovery claim offline')
    # Exclusive creation refuses another cooperative writer, including recovery.
    try:
        _record(root / LOCK, {'transaction': transaction})
    except FileExistsError as exc:
        raise ApplyError('CONCURRENT_APPLY') from exc
    started = False
    try:
        _check_plan(root, plan)
        audit.mkdir(parents=True)
        _record(audit / 'manifest.json', plan)
        _record(audit / 'authorization.json', authorization)
        for rel in STORE_FILES:
            for folder, data in [('before', _path(root, rel).read_bytes()), ('after', output[rel])]:
                path = audit / folder / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
        # Journal is complete before any replacement. Crash recovery accepts
        # only bytes matching these before/after hashes.
        _record(audit / 'ready.json', {'output_sha256': {p: _sha(b) for p, b in output.items()}})
        _check_plan(root, plan)
        started = True
        for rel in STORE_FILES:
            _replace_file(_path(root, rel), output[rel])
        # Revalidate complete state on private copy while the live gate stays closed.
        with tempfile.TemporaryDirectory(prefix='timonelo-apply-verify-') as tmp:
            private = Path(tmp)
            shutil.copytree(root / 'evidence', private / 'evidence')
            if (root / 'knowledge').exists():
                shutil.copytree(root / 'knowledge', private / 'knowledge')
            states = _states(Workspace(str(private / 'evidence')))
            if _sha(_bytes(states)) != plan['authority_sha256']:
                raise ApplyError('POST_INSTALL_AUTHORITY_CHANGED')
        expected = {**plan['baseline_sha256'], **{p: _sha(b) for p, b in output.items()}}
        if _inventory(root) != expected:
            raise ApplyError('CONCURRENT_CHANGE_DURING_INSTALL')
        _epoch(root)
        _record(audit / 'complete.json', {'manifest_sha256': plan['manifest_sha256']})
        (root / LOCK).unlink()
        return audit
    except Exception:
        if (audit / 'complete.json').exists():
            # Completion is durable: a lock-removal failure must not turn a
            # committed installation into a silent preimage restoration.
            raise
        if started:
            _restore(root, audit)
        else:
            # Even unsuccessful exclusion invalidates retained authority instances.
            _epoch(root)
            (root / LOCK).unlink()
        raise
    # BaseException intentionally leaves lock+journal for explicit recovery.


def apply_candidate(root, plan, authorization, *, offline=False):
    """Apply only the exact replayed and separately authorized manifest."""
    _offline(offline)
    root = Path(root).resolve()
    _check_plan(root, plan)
    if (authorization.get('manifest_sha256') != plan['manifest_sha256'] or
            not all(isinstance(authorization.get(k), str) and authorization[k].strip()
                    for k in ('actor', 'occurred_on', 'instruction'))):
        raise ApplyError('EXPLICIT_MANIFEST_AUTHORIZATION_REQUIRED')
    output, states = _replay(root, plan['operations'])
    if ({p: _sha(b) for p, b in output.items()} != plan['output_sha256'] or
            _sha(_bytes(states)) != plan['authority_sha256']):
        raise ApplyError('DETERMINISTIC_REPLAY_MISMATCH')
    return _transaction(root, plan, authorization, output)


def _journal_plan(audit, *, completed=False):
    """Validate retained bindings before using a journal to change live state."""
    plan = json.loads((audit / 'manifest.json').read_bytes())
    if plan.get('manifest_sha256') != _sha(_bytes({k: v for k, v in plan.items() if k != 'manifest_sha256'})):
        raise ApplyError('RECOVERY_MANIFEST_HASH_MISMATCH')
    ready = json.loads((audit / 'ready.json').read_bytes())
    if set(plan['output_sha256']) != set(STORE_FILES) or ready['output_sha256'] != plan['output_sha256']:
        raise ApplyError('RECOVERY_OUTPUT_HASH_MISMATCH')
    if completed:
        completion = json.loads((audit / 'complete.json').read_bytes())
        if completion.get('manifest_sha256') != plan['manifest_sha256']:
            raise ApplyError('RECOVERY_COMPLETION_HASH_MISMATCH')
    for rel in STORE_FILES:
        if _sha((audit / 'after' / rel).read_bytes()) != plan['output_sha256'][rel]:
            raise ApplyError('RECOVERY_OUTPUT_HASH_MISMATCH')
    return plan


def _restore(root, audit):
    plan = _journal_plan(audit)
    # Check EVERYTHING before restoring ANYTHING. A foreign edit leaves the
    # gate closed for manual investigation rather than overwriting that edit.
    backups = {}
    current = _inventory(root)
    if (_git(root, 'rev-parse', 'HEAD') != plan['baseline_commit'] or
            {p: h for p, h in current.items() if p not in STORE_FILES} !=
            {p: h for p, h in plan['baseline_sha256'].items() if p not in STORE_FILES}):
        raise ApplyError('RECOVERY_CONCURRENT_CHANGE: gate remains closed')
    for rel in STORE_FILES:
        before = (audit / 'before' / rel).read_bytes()
        if _sha(before) != plan['baseline_sha256'][rel]:
            raise ApplyError('RECOVERY_BACKUP_HASH_MISMATCH')
        if _sha(_path(root, rel).read_bytes()) not in (_sha(before), plan['output_sha256'][rel]):
            raise ApplyError('RECOVERY_CONCURRENT_CHANGE: gate remains closed')
        backups[rel] = before
    for rel, before in backups.items():
        _replace_file(_path(root, rel), before)
    _epoch(root)
    _record(audit / ('recovered-' + uuid.uuid4().hex + '.json'), {'result': 'RESTORED_PRE_TRANSACTION_BYTES'})
    (root / LOCK).unlink()


def recover_interrupted_apply(root, *, offline=False):
    """Restore interrupted, uncompleted installation; never erase its audit."""
    _offline(offline)
    root = Path(root).resolve()
    try:
        _record(root / RECOVERY_LOCK, {'recovery': uuid.uuid4().hex})
    except FileExistsError as exc:
        raise ApplyError('CONCURRENT_RECOVERY: inspect a stale recovery claim offline') from exc
    try:
        return _recover_interrupted_apply(root)
    finally:
        (root / RECOVERY_LOCK).unlink()


def _recover_interrupted_apply(root):
    lock = json.loads((root / LOCK).read_bytes())
    transaction = lock['transaction']
    if not isinstance(transaction, str) or len(transaction) != 32 or any(c not in '0123456789abcdef' for c in transaction):
        raise ApplyError('INVALID_RECOVERY_TRANSACTION')
    audit = root / AUDIT / transaction
    if (audit / 'complete.json').exists():
        # Completion + durable epoch preceded lock removal. Keep the installed
        # store; completed approvals must be withdrawn by corrective rollback.
        plan = _journal_plan(audit, completed=True)
        if (_git(root, 'rev-parse', 'HEAD') != plan['baseline_commit'] or
                _inventory(root) != {**plan['baseline_sha256'], **plan['output_sha256']}):
            raise ApplyError('COMPLETED_STORE_CHANGED: gate remains closed')
        _epoch(root)
        (root / LOCK).unlink()
    elif (audit / 'ready.json').exists():
        _restore(root, audit)
    else:
        # No replacement can begin before ready.json is durable. An early
        # process crash may leave only the lock or a partial journal.
        _epoch(root)
        _record(audit / ('recovered-' + uuid.uuid4().hex + '.json'), {'result': 'NO_INSTALL_STARTED'})
        (root / LOCK).unlink()
    return audit


def rollback_candidate(root, audit, *, actor, occurred_on, note, offline=False):
    """Corrective withdrawal: preserve observations and approvals, append audit."""
    _offline(offline)
    root, audit = Path(root).resolve(), Path(audit).resolve()
    if audit.parent != root / AUDIT or not (audit / 'complete.json').is_file():
        raise ApplyError('COMPLETED_LOCAL_APPLY_REQUIRED')
    if not all(isinstance(v, str) and v.strip() for v in (actor, occurred_on, note)):
        raise ApplyError('EXPLICIT_CORRECTIVE_INSTRUCTION_REQUIRED')
    applied = _journal_plan(audit, completed=True)
    if (root / LOCK).exists():
        raise ApplyError('CONCURRENT_APPLY')
    generation = (root / GENERATION).read_text() if (root / GENERATION).exists() else None
    baseline_commit = _git(root, 'rev-parse', 'HEAD')
    baseline = _inventory(root)
    with tempfile.TemporaryDirectory(prefix='timonelo-withdraw-') as tmp:
        private = Path(tmp)
        shutil.copytree(root / 'evidence', private / 'evidence')
        if (root / 'knowledge').exists():
            shutil.copytree(root / 'knowledge', private / 'knowledge')
        ws = Workspace(str(private / 'evidence'))
        raw = _load(root, STORE_FILES[3])
        for op in applied['operations']:
            sid = op['statement_id']
            expected = _load(audit / 'after', STORE_FILES[3])[sid]
            if raw.get(sid) != expected:
                raise ApplyError('WITHDRAWAL_TARGET_CHANGED')
            ws.editor.set_evidence_condition(sid, EvidenceCondition.UNKNOWN,
                                             actor=actor, occurred_on=occurred_on, note=note)
            raw[sid] = ws.editor.get(sid).to_dict()
        _path(private, STORE_FILES[3]).write_bytes(_bytes(raw))
        output = {p: _path(private, p).read_bytes() for p in STORE_FILES}
        states = _states(Workspace(str(private / 'evidence')))
    plan = dict(schema='timonelo.governed-canonical-withdrawal.v1',
                baseline_commit=baseline_commit, baseline_sha256=baseline,
                generation=generation,
                operations=applied['operations'], withdraws=applied['manifest_sha256'],
                output_sha256={p: _sha(b) for p, b in output.items()}, authority_sha256=_sha(_bytes(states)))
    plan['manifest_sha256'] = _sha(_bytes(plan))
    return _transaction(root, plan, dict(actor=actor, occurred_on=occurred_on, instruction=note), output)


def inspect_historical_manifest(path, *, expected_sha256):
    """Inspect a frozen review artifact; never reconstruct or apply its outputs."""
    path = Path(path).resolve()
    physical = path.read_bytes()
    if _sha(physical) != expected_sha256:
        raise ApplyError('HISTORICAL_MANIFEST_HASH_MISMATCH')
    manifest = json.loads(physical)
    private = manifest.get('private_output')
    candidates = []
    for record in manifest.get('files', []):
        for kind in ('before', 'after'):
            candidate = _path(path.parent, record[kind + '_candidate'])
            expected = record[kind + '_sha256']
            candidates.append(dict(path=record[kind + '_candidate'], expected_sha256=expected,
                bytes_match=bool(candidate.is_file() and _sha(candidate.read_bytes()) == expected)))
    return dict(manifest_sha256=_sha(physical), manifest_bytes_verified=True,
                schema=manifest.get('schema'), mode=manifest.get('mode'),
                base_commit=manifest.get('base_commit'),
                private_output_available=bool(private and Path(private).is_dir()),
                candidate_files=candidates,
                frozen_candidate_bytes_recoverable=bool(candidates and all(c['bytes_match'] for c in candidates)),
                historical_output_rebuilt_or_identical=False,
                recovery_requirement='Original frozen output bytes and hashes, or a newly reviewed current-baseline replay manifest.')
