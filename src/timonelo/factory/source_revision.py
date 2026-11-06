"""Document revision bindings, independent of acquisition time or authority.

An unknown printed edition is an absence of edition information, never an
absence of byte identity. This module grants no review or publication rights.
"""
import re

SCHEMA = 'timonelo.source-revision.v1'


def source_revision(artifact):
    digest = artifact.sha256
    version = artifact.version
    if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest) or digest == '0' * 64:
        raise ValueError('SOURCE_REVISION_INVALID_DIGEST')
    if version is not None and (not isinstance(version, str) or not version.strip()):
        raise ValueError('SOURCE_VERSION_MISMATCH')
    return {'schema': SCHEMA, 'artifact_sha256': digest, 'printed_edition': version,
            'edition_status': 'UNKNOWN' if version is None else 'PRINTED'}


def require_source_revision(artifact, claim):
    if artifact.sha256 != claim.get('artifact_sha256'):
        raise ValueError('ARTIFACT_SHA_MISMATCH')
    if artifact.version is None:
        if artifact.document_class != 'official_ship_map' or claim.get('source_version') is not None:
            raise ValueError('SOURCE_VERSION_MISMATCH')
        if claim.get('source_revision') != source_revision(artifact):
            raise ValueError('SOURCE_REVISION_MISMATCH')
    else:
        if not artifact.version or claim.get('source_version') != artifact.version:
            raise ValueError('SOURCE_VERSION_MISMATCH')
        if 'source_revision' in claim and claim['source_revision'] != source_revision(artifact):
            raise ValueError('SOURCE_REVISION_MISMATCH')
    return source_revision(artifact)
