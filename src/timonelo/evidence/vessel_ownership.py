"""Exact vessel ownership, shared by preparation, apply and authority readers.

An entity has one owner segment. A ship name elsewhere is never ownership.
Identity provenance quarantine is separate from a valid IMO check digit.
"""
from pathlib import Path
import json
import re
import unicodedata

from timonelo.evidence.registry import normalize_vessel_imo

REPOSITORY = Path(__file__).resolve().parents[3]
VESSEL_KINDS = frozenset({'vessel', 'ship', 'deck', 'venue', 'cabin', 'voyage'})


def canonical_entity(entity_id):
    if not isinstance(entity_id, str) or entity_id != entity_id.strip() or not entity_id.isascii():
        raise ValueError('MALFORMED_VESSEL_ENTITY')
    parts = entity_id.casefold().split(':')
    if (len(parts) not in (2, 3) or parts[0] not in VESSEL_KINDS or
            not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', parts[1]) or
            (len(parts) == 2 and parts[0] not in {'ship', 'vessel'}) or
            (len(parts) == 3 and not re.fullmatch(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', parts[2]))):
        raise ValueError('MALFORMED_VESSEL_ENTITY')
    return parts[0], parts[1], parts[2] if len(parts) == 3 else ''


def identity_restrictions(slug):
    path = Path(__file__).with_name('vessel_identity_quarantine.json')
    try:
        config = json.loads(path.read_text(encoding='utf8'))
        rows = config['identities']
        if (config.get('schema') != 'timonelo.vessel-identity-quarantine.v1' or
                not isinstance(rows, list) or
                any(not isinstance(r, dict) or type(r.get('canonical_admission')) is not bool
                    or not isinstance(r.get('slug'), str) for r in rows) or
                len({r['slug'] for r in rows}) != len(rows)):
            raise ValueError('VESSEL_IDENTITY_POLICY_INVALID')
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError('VESSEL_IDENTITY_POLICY_UNAVAILABLE_OR_INVALID') from exc
    return next((r for r in rows if r.get('slug') == slug), {})


def canonical_vessel(slug, root=None, allow_quarantined=False):
    if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('INVALID_VESSEL_SLUG')
    root = Path(root) if root is not None else REPOSITORY
    try:
        identity = json.loads((root / 'knowledge/ships' / slug / 'identity.json').read_text(encoding='utf8'))
        if identity.get('slug') != slug:
            raise ValueError('CANONICAL_VESSEL_IDENTITY_MISMATCH')
        imo = normalize_vessel_imo(identity['imo_number']['value'])
    except (OSError, KeyError, TypeError) as exc:
        raise ValueError('CANONICAL_VESSEL_IDENTITY_UNAVAILABLE') from exc
    if not allow_quarantined and identity_restrictions(slug).get('canonical_admission') is False:
        raise ValueError('VESSEL_IDENTITY_QUARANTINED')
    return imo


def validate_ownership(entity_id, artifact, target_slug=None, target_imo=None, root=None,
                       statement_type=None):
    _, slug, _ = canonical_entity(entity_id)
    if target_slug is not None and slug != target_slug:
        raise ValueError('ENTITY_TARGET_VESSEL_MISMATCH')
    imo = canonical_vessel(slug, root=root)
    if target_imo is not None and imo != normalize_vessel_imo(target_imo):
        raise ValueError('CANONICAL_VESSEL_IDENTITY_MISMATCH')
    if statement_type and 'mmsi' in statement_type.casefold() and identity_restrictions(slug).get('mmsi_admission') is False:
        raise ValueError('VESSEL_MMSI_QUARANTINED')
    establishes = getattr(artifact, 'establishes_vessel', None)
    if not callable(establishes) or not establishes(imo):
        raise ValueError('ARTIFACT_NOT_ATTRIBUTED_TO_VESSEL')
    return imo


def normalized_principal(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('INVALID_REVIEWER_IDENTITY')
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def entity_key(entity_id):
    """Compare vessel entities consistently without rewriting historical IDs."""
    if isinstance(entity_id, str) and entity_id.split(':', 1)[0].casefold() in VESSEL_KINDS:
        return entity_id.casefold()
    return entity_id
