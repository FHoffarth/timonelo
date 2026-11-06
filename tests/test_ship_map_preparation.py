from copy import deepcopy
from types import SimpleNamespace

import pytest

from timonelo.factory.ship_map_preparation import bind_candidate, require_selected_claims


def claim():
    return {'id': 'GR-MAP-01', 'name': 'TEST LOUNGE', 'exact_claim': 'Research prose, not final approval',
            'value': [5], 'artifact_id': None, 'artifact_sha256': 'a' * 64,
            'target_vessel': 'IMO9803613', 'entity_id': 'venue:MSC-GRANDIOSA:test-lounge',
            'question_id': 'Q-0016', 'statement_type': 'deck.venue_present', 'source_version': None,
            'page': 4, 'locator': "Page 4, table 'Restaurants', row 'TEST LOUNGE', printed deck '5'",
            'observed_text': 'TEST LOUNGE 5', 'source_boxes': [[1, 2, 20, 8]],
            'scope': 'SOURCE_EDITION_VENUE_DECK_ONLY'}


def test_final_binding_uses_unknown_edition_and_exact_private_artifact():
    original = claim()
    a = SimpleNamespace(artifact_id='ART-0010', sha256='a' * 64, version=None, document_class='official_ship_map')
    final = bind_candidate(original, a, 'MSC Grandiosa', {'page': 2, 'decks': [5], 'label_key': 'TEST LOUNGE'})
    assert original['artifact_id'] is None
    assert final['artifact_id'] == 'ART-0010' and final['source_version'] is None
    assert final['source_revision']['artifact_sha256'] == 'a' * 64
    assert 'printed edition unknown' in final['exact_claim']
    assert '2026-11-05' not in final['exact_claim']
    assert final['source_index']['decks'] == [5]


@pytest.mark.parametrize('different', [False, True])
def test_normalized_duplicate_and_conflict_are_rejected(different):
    a, b = claim(), claim()
    b['id'] = 'GR-MAP-02'
    b['entity_id'] = b['entity_id'].lower()
    if different: b['value'] = [6]
    with pytest.raises(ValueError, match='CONTRADICTORY|DUPLICATE'):
        require_selected_claims([a, b])


def test_no_prose_or_source_drift_is_hidden_when_binding_changes():
    a = SimpleNamespace(artifact_id='ART-0010', sha256='b' * 64, version=None, document_class='official_ship_map')
    with pytest.raises(ValueError, match='ARTIFACT_SHA'):
        bind_candidate(claim(), a, 'MSC Grandiosa', {'page': 2, 'decks': [5], 'label_key': 'TEST LOUNGE'})
