"""Reproduce a ship-map table observation and its independent deck-index reading.

This reader establishes source support only. Identity quarantine, source revision,
review, admission and publication remain the responsibility of existing callers.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata

from timonelo.evidence.vessel_ownership import REPOSITORY, canonical_entity
from timonelo.factory.ship_map_extract import key, reconcile

LAYOUT = 'OFFICIAL_SHIP_MAP_TABLE_INDEX'


def venue_suffix(label):
    """The report builder's label-to-entity suffix rule, without importing it."""
    text = re.sub(r'\s*\(.*?\)\*?', '', label).replace('&', ' and ').replace('’', '').replace("'", '')
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def verify_map_reading(path, claim, root=None):
    """Return reproduced table text, refusing unsupported or conflicting readings."""
    import fitz

    def require(ok, reason):
        if not ok:
            raise ValueError(reason)

    require(isinstance(claim, dict) and claim.get('source_layout') == LAYOUT, 'SOURCE_LAYOUT_MISMATCH')
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == claim.get('artifact_sha256'), 'ARTIFACT_SHA_MISMATCH')
    kind, owner, suffix = canonical_entity(claim.get('entity_id'))
    name = claim.get('name')
    require(kind == 'venue' and isinstance(name, str) and bool(name) and suffix == venue_suffix(name),
            'SOURCE_VENUE_ENTITY_MISMATCH')
    try:
        identity = json.loads((Path(root or REPOSITORY) / 'knowledge/ships' / owner / 'identity.json').read_text(encoding='utf8'))
        require(identity['slug'] == owner, 'SOURCE_VESSEL_IDENTITY_MISMATCH')
        expected_cover = identity['name']['value'].upper() + ' SHIP MAP'
    except (OSError, KeyError, TypeError) as exc:
        raise ValueError('SOURCE_VESSEL_IDENTITY_UNAVAILABLE') from exc
    value = claim.get('value')
    require(isinstance(value, list) and bool(value) and all(type(v) is int for v in value)
            and sorted(set(value)) == value, 'NON_CANONICAL_DECK_VALUE')
    try:
        opened = fitz.open(stream=raw, filetype='pdf')
    except (fitz.FileDataError, fitz.EmptyFileError) as exc:
        raise ValueError('SOURCE_MAP_DOCUMENT_INVALID') from exc
    with opened as doc:
        cover = ' '.join(doc[0].get_text().replace('\x08', ' ').split())
        require(cover == expected_cover, 'SOURCE_MAP_VESSEL_TITLE_MISMATCH')
        fresh = reconcile(doc)
        group = next((v for v in fresh['venues'] if v['key'] == key(name)), None)
        require(group is not None and name in group['labels'], 'SOURCE_MAP_LABEL_MISMATCH')
        require(not group['issues'] and group['value'] == value, 'SOURCE_MAP_TABLE_INDEX_CONFLICT')
        index = claim.get('source_index')
        require(isinstance(index, dict) and set(index) == {'page', 'decks', 'label_key'}
                and type(index.get('page')) is int and index['page'] in fresh['index_pages']
                and index.get('label_key') == key(name)
                and isinstance(index.get('decks'), list) and all(type(v) is int for v in index['decks'])
                and index['decks'] == value, 'SOURCE_MAP_INDEX_MISMATCH')
        # Bind the supplied page as well as the reconciled cross-page index values.
        from timonelo.factory.ship_map_extract import read_index
        listed = sorted({deck for deck, label, _ in read_index(doc).get(index['page'], []) if key(label) == key(name)})
        require(listed == value, 'SOURCE_MAP_INDEX_MISMATCH')
        page = claim.get('page')
        require(type(page) is int and 1 <= page <= len(doc), 'SOURCE_PAGE_INVALID')
        boxes = claim.get('source_boxes')
        require(isinstance(boxes, list) and len(boxes) == 1, 'SOURCE_BOXES_INVALID')
        box = boxes[0]
        require(isinstance(box, list) and len(box) == 4
                and all(type(v) in (int, float) and math.isfinite(v) for v in box), 'SOURCE_BOXES_INVALID')
        rect = fitz.Rect(box)
        require(not rect.is_empty and doc[page-1].rect.contains(rect), 'SOURCE_BOXES_INVALID')
        actual = doc[page-1].get_textbox(rect + (-2,-2,2,2)).strip()
        require(isinstance(claim.get('observed_text'), str)
                and ' '.join(actual.split()) == ' '.join(claim['observed_text'].split()), 'SOURCE_OBSERVATION_CHANGED')
        selected = []
        for row in group['rows']:
            expected_box = [round(v, 2) for v in (row['box'][0], row['box'][1]+2.6, row['box'][2], row['box'][3]-2.6)]
            locator = f"Page {row['page']}, table {row['section']!r}, row {row['label']!r}, printed deck {row['token']!r}"
            if (row['page'] == page and row['label'] == name and box == expected_box
                    and claim.get('locator') == locator
                    and ' '.join(actual.split()) == ' '.join((name + ' ' + row['token']).split())):
                selected.append(row)
        require(bool(selected), 'SOURCE_MAP_TABLE_ROW_MISMATCH')
        return actual
