"""Integrity/freshness envelope for an already canonically evaluated projection.

This module grants no publication authority. Policy: docs/PUBLIC_RELEASE_SAFETY.md.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

POLICY = json.loads((Path(__file__).resolve().parents[3] /
                    'frontend/src/passenger/publicationPolicy.json').read_text(encoding='utf8'))
SCHEMA = 'timonelo.fleet.snapshot.v1'


def revision_input(snapshot):
    """Exact UTF-8 framing, shared with the browser; includes ALL authority metadata."""
    return '\n'.join([snapshot['schema'], snapshot['generated_at'], snapshot['expires_at'],
                      'blocked' if snapshot['blocked'] else 'active', snapshot['payload']]).encode('utf8')


def make_snapshot(data, *, blocked=False, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('Snapshot generation needs an explicit timezone')
    now = now.astimezone(timezone.utc)
    data = deepcopy(data)
    if blocked:
        for ship in data['ships'].values():
            ship.update(facts=[], sources=[], level=0)
    stamp = lambda date: date.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    snapshot = {'schema': SCHEMA, 'generated_at': stamp(now),
                'expires_at': stamp(now + timedelta(seconds=POLICY['max_age_seconds'])),
                'blocked': bool(blocked),
                'payload': json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))}
    snapshot['revision'] = hashlib.sha256(revision_input(snapshot)).hexdigest()
    return snapshot
