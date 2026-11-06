"""Unknown printed editions never stand in for exact document identity."""
from types import SimpleNamespace

import pytest

from timonelo.factory.source_revision import source_revision, require_source_revision


def artifact(version=None, digest='a' * 64, cls='official_ship_map'):
    return SimpleNamespace(version=version, sha256=digest, document_class=cls)


def test_unknown_edition_is_explicit_and_digest_bound():
    a = artifact()
    revision = source_revision(a)
    assert revision == {'schema': 'timonelo.source-revision.v1', 'artifact_sha256': 'a' * 64,
                        'printed_edition': None, 'edition_status': 'UNKNOWN'}
    require_source_revision(a, {'artifact_sha256': a.sha256, 'source_version': None,
                               'source_revision': revision})
    assert a.version is None


@pytest.mark.parametrize('mutation', ['missing', 'changed_bytes', 'invented_edition', 'unknown_downgrade', 'retrieval_as_edition'])
def test_source_revision_mismatches_refuse(mutation):
    a = artifact()
    claim = {'artifact_sha256': a.sha256, 'source_version': None, 'source_revision': source_revision(a)}
    if mutation == 'missing': claim.pop('source_revision')
    if mutation == 'changed_bytes': a.sha256 = 'b' * 64
    if mutation == 'invented_edition': claim['source_version'] = '11.2026'
    if mutation == 'unknown_downgrade': a.version = '11.2025 DEU'
    if mutation == 'retrieval_as_edition': claim['source_revision']['printed_edition'] = '2026-11-05'
    with pytest.raises(ValueError, match='SOURCE_VERSION|SOURCE_REVISION|ARTIFACT_SHA'):
        require_source_revision(a, claim)


def test_dated_document_legacy_contract_is_unchanged():
    a = artifact('11.2025 DEU', cls='cruise_line_deck_plan')
    require_source_revision(a, {'artifact_sha256': a.sha256, 'source_version': '11.2025 DEU'})
    for wrong in (None, '', 'UNKNOWN', '2026-11-05', '11.2026 DEU'):
        with pytest.raises(ValueError, match='SOURCE_VERSION_MISMATCH'):
            require_source_revision(a, {'artifact_sha256': a.sha256, 'source_version': wrong})


def test_unknown_mode_does_not_apply_to_other_source_classes():
    a = artifact(cls='cruise_line_deck_plan')
    with pytest.raises(ValueError, match='SOURCE_VERSION_MISMATCH'):
        require_source_revision(a, {'artifact_sha256': a.sha256, 'source_version': None,
                                   'source_revision': source_revision(a)})
