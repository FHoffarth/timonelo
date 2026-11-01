from datetime import datetime, timezone, timedelta
import hashlib
import json
from timonelo.evidence.publication_snapshot import make_snapshot, revision_input


def test_contract_is_bounded_and_integrity_binds_metadata_and_payload():
    now = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)
    data = {'schema': 'timonelo.fleet.v1', 'as_of': '2026-11-01', 'ships': {}}
    snapshot = make_snapshot(data, now=now)
    assert snapshot['generated_at'] == '2026-11-01T10:00:00.000Z'
    assert snapshot['expires_at'] == '2026-11-01T10:10:00.000Z'
    assert snapshot['blocked'] is False
    assert json.loads(snapshot['payload']) == data
    assert snapshot['revision'] == hashlib.sha256(revision_input(snapshot)).hexdigest()
    changed = dict(snapshot, expires_at='2026-11-01T11:10:00.000Z')
    assert hashlib.sha256(revision_input(changed)).hexdigest() != snapshot['revision']


def test_blocked_snapshot_cannot_carry_public_facts_and_does_not_mutate_input():
    data = {'schema': 'timonelo.fleet.v1', 'as_of': '2026-11-01', 'ships': {
        'msc-bellissima': {'level': 1, 'candidate_count': 1, 'facts': [{'test': True}], 'sources': [{'test': True}]}}}
    snapshot = make_snapshot(data, blocked=True)
    profile = json.loads(snapshot['payload'])['ships']['msc-bellissima']
    assert snapshot['blocked'] is True
    assert profile['facts'] == [] and profile['sources'] == [] and profile['level'] == 0
    assert data['ships']['msc-bellissima']['facts'] == [{'test': True}]
