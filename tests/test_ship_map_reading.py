"""Map table and deck-index observations require independent source agreement."""
import copy
import hashlib

import fitz
import pytest


def held_map(tmp_path, *, index_decks=(5, 6), second_token=None, token='5-6', title='MSC EURIBIA SHIP MAP'):
    path = tmp_path / 'held.pdf'
    doc = fitz.open()
    cover = doc.new_page()
    cover.insert_text((30, 40), title, fontsize=14)
    page = doc.new_page()
    for i, deck in enumerate((5, 6, 7, 8, 9, 10)):
        y = 40 + 110 * i
        page.insert_text((20, y), f'DECK {deck}', fontname='hebo', fontsize=8)
        if deck in index_decks:
            page.insert_text((30, y + 18), 'BLUE ROOM', fontsize=8)
    def table(token):
        page = doc.new_page()
        page.insert_text((50, 50), 'Restaurants', fontname='hebo', fontsize=8)
        page.insert_text((240, 50), 'Deck', fontname='hebo', fontsize=8)
        page.insert_text((50, 80), 'BLUE ROOM', fontsize=8)
        page.insert_text((page.search_for('Deck')[0].x1 - fitz.get_text_length(token, fontsize=8), 80), token, fontsize=8)
        name = page.search_for('BLUE ROOM')[0]
        number = page.search_for(token)[0]
        return [round(v, 2) for v in (name.x0, min(name.y0, number.y0)+2.6, number.x1, max(name.y1, number.y1)-2.6)]
    box = table(token)
    if second_token:
        table(second_token)
    doc.save(path)
    doc.close()
    with fitz.open(path) as doc:
        text = doc[2].get_textbox(fitz.Rect(box)+(-2,-2,2,2)).strip()
    claim = {'name': 'BLUE ROOM', 'entity_id': 'venue:MSC-EURIBIA:blue-room',
             'artifact_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
             'source_layout': 'OFFICIAL_SHIP_MAP_TABLE_INDEX', 'page': 3,
             'source_boxes': [box], 'observed_text': text, 'value': [5,6],
             'locator': "Page 3, table 'Restaurants', row 'BLUE ROOM', printed deck '5-6'",
             'source_index': {'page': 2, 'decks': [5,6], 'label_key': 'BLUE ROOM'}}
    return path, claim


def verify(path, claim):
    from timonelo.factory.ship_map_reading import verify_map_reading
    return verify_map_reading(path, claim)


def test_real_pdf_table_and_independent_index_agree(tmp_path):
    path, claim = held_map(tmp_path)
    assert verify(path, claim) == 'BLUE ROOM\n5-6'


@pytest.mark.parametrize('change', ['bytes','owner','suffix','name','value','unsorted','bool', 'text','box','nan_box','wrong_box','index_page','index_decks','index_key','layout','locator'])
def test_bound_source_fields_cannot_be_substituted(tmp_path, change):
    path, original = held_map(tmp_path)
    claim = copy.deepcopy(original)
    if change == 'bytes': path.write_bytes(path.read_bytes() + b'\nchanged')
    if change == 'owner': claim['entity_id'] = 'venue:MSC-VIRTUOSA:blue-room'
    if change == 'suffix': claim['entity_id'] = 'venue:MSC-EURIBIA:red-room'
    if change == 'name': claim['name'] = 'BLUE'
    if change == 'value': claim['value'] = [5]
    if change == 'unsorted': claim['value'] = [6,5]
    if change == 'bool': claim['value'] = [True,6]
    if change == 'text': claim['observed_text'] = 'BLUE ROOM 5'
    if change == 'box': claim['source_boxes'] = [[0,0,0,0]]
    if change == 'nan_box': claim['source_boxes'][0][0] = float('nan')
    if change == 'wrong_box': claim['source_boxes'][0][0] -= 1
    if change == 'index_page': claim['source_index']['page'] = 3
    if change == 'index_decks': claim['source_index']['decks'] = [5]
    if change == 'index_key': claim['source_index']['label_key'] = 'RED ROOM'
    if change == 'layout': claim['source_layout'] = 'DECK_PLAN'
    if change == 'locator': claim['locator'] = claim['locator'].replace('Restaurants','Bars')
    with pytest.raises(ValueError):
        verify(path, claim)


@pytest.mark.parametrize('kwargs', [{'second_token':'5'}, {'index_decks':(5,)}, {'title':'MSC VIRTUOSA SHIP MAP'}])
def test_source_conflicts_and_wrong_cover_refuse_even_when_selected_row_matches(tmp_path, kwargs):
    path, claim = held_map(tmp_path, **kwargs)
    with pytest.raises(ValueError):
        verify(path, claim)




def test_printed_range_uses_index_decks_without_filling_gap(tmp_path):
    path, claim = held_map(tmp_path, index_decks=(5,7), token='5-7')
    claim['value'] = [5,7]
    claim['source_index']['decks'] = [5,7]
    claim['locator'] = claim['locator'].replace('5-6', '5-7')
    assert verify(path, claim) == 'BLUE ROOM\n5-7'
    claim['value'] = [5,6,7]
    with pytest.raises(ValueError, match='SOURCE_MAP_TABLE_INDEX_CONFLICT'):
        verify(path, claim)


def test_matching_digest_does_not_make_invalid_pdf_readable(tmp_path):
    path, claim = held_map(tmp_path)
    path.write_bytes(b'not a PDF')
    claim['artifact_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match='SOURCE_MAP_DOCUMENT_INVALID'):
        verify(path, claim)
