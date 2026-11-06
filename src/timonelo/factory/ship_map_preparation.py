"""Private official-map intake and one review packet. No canonical apply mode.

Sources and proposed artifact IDs exist only in an externally located copy.
No observation becomes an EvidenceEvent, approved statement or publication here.
"""
from copy import deepcopy
from datetime import datetime
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

from timonelo.factory.evidence_batch import (
    _files, _hash, _states, inspect_batch, process_private_batch, render_claim,
)
from timonelo.factory.source_revision import source_revision, require_source_revision
from timonelo.evidence.vessel_ownership import canonical_entity, canonical_vessel
from timonelo.evidence.workspace import Workspace
from timonelo.factory.ship_map_extract import key, read_map
from timonelo.factory.ship_map_reading import verify_map_reading

INPUT = '983d97e18210a184290b16845985f19c3a62c306'
REPORT = 'reports/fleet-evidence-expansion/ship-maps'


def require_selected_claims(claims):
    ids, groups = set(), {}
    for c in claims:
        if c['id'] in ids:
            raise ValueError('DUPLICATE_CLAIM_ID')
        ids.add(c['id'])
        owner = canonical_entity(c['entity_id'])
        identity = (owner, c['question_id'])
        if identity in groups:
            if groups[identity] != c['value']:
                raise ValueError('CONTRADICTORY_SELECTED_CLAIM')
            raise ValueError('DUPLICATE_SELECTED_CLAIM')
        groups[identity] = c['value']


def bind_candidate(original, artifact, vessel_name, source_index):
    claim = deepcopy(original)
    claim.update(artifact_id=artifact.artifact_id,
                 source_revision=source_revision(artifact),
                 source_layout='OFFICIAL_SHIP_MAP_TABLE_INDEX',
                 source_index=deepcopy(source_index))
    require_source_revision(artifact, claim)
    claim['exact_claim'] = render_claim(claim, vessel_name)
    return claim


def _dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf8')


def prepare_private(root, receipts_path, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists() or output == root or root in output.parents:
        raise ValueError('OUTPUT_EXISTS_OR_INSIDE_SOURCE')
    if any((p / '.git').exists() for p in [output, *output.parents]):
        raise ValueError('OUTPUT_INSIDE_GIT_CHECKOUT')
    research = root / REPORT
    # Preserve the handoff bytes, rather than rewriting the research to match us.
    expected_files = subprocess.check_output(
        ['git', '-C', str(root), 'ls-tree', '-r', '--name-only', INPUT, '--', REPORT], text=True).splitlines()
    if len(expected_files) != 14:
        raise ValueError('HANDOFF_SCOPE_CHANGED')
    for rel in expected_files:
        expected = subprocess.check_output(['git', '-C', str(root), 'show', INPUT + ':' + rel])
        if (root / rel).read_bytes() != expected:
            raise ValueError('HANDOFF_FILE_CHANGED: ' + rel)
    protected = {n: _files(root / n) for n in ('evidence', 'knowledge')}
    registry_hash = hashlib.sha256((root / 'evidence/artifacts/index.json').read_bytes()).hexdigest()
    descriptors = json.loads((research / 'source-register.json').read_bytes())['documents']
    receipts = json.loads(Path(receipts_path).read_bytes())
    by_slug = {r['slug']: r for r in receipts}
    if len(descriptors) != 7 or len(by_slug) != 7 or len(receipts) != 7:
        raise ValueError('EXPECTED_SEVEN_UNIQUE_SOURCES')
    # Validate ALL held sources and origin receipts before any private registration.
    packages, held = {}, {}
    for d in descriptors:
        r = by_slug[d['slug']]
        p = Path(r['private_path'])
        url = urlsplit(d['url'])
        if (url.scheme != 'https' or url.hostname != 'service.msccruises.com' or
                r['requested_url'] != d['url'] or r['final_url'] != d['url'] or
                r['http_status'] != 200 or r['status'] != 'EXACT_MATCH'):
            raise ValueError('SOURCE_ORIGIN_RECEIPT_MISMATCH')
        acquired = datetime.fromisoformat(r['retrieved_at'])
        if acquired.tzinfo is None:
            raise ValueError('RETRIEVAL_TIMEZONE_REQUIRED')
        data = p.read_bytes()
        if (hashlib.sha256(data).hexdigest() != d['sha256'] or r['sha256'] != d['sha256'] or
                len(data) != d['bytes'] or not data.startswith(b'%PDF-')):
            raise ValueError('SOURCE_DIGEST_OR_SIZE_MISMATCH')
        if d['version'] is not None or d['version_status'] != 'UNKNOWN_NOT_PRINTED':
            raise ValueError('UNEXPECTED_SOURCE_EDITION')
        held[d['slug']] = p
        packages[d['slug']] = json.loads((research / 'observations' / (d['slug'] + '.json')).read_bytes())
    selected = [c for p in packages.values() for c in p['first_review_batch']]
    require_selected_claims(selected)
    if len(selected) != 56:
        raise ValueError('EXPECTED_56_SELECTED_CLAIMS')

    output.mkdir(parents=True)
    private = output / 'private-source-root'
    for n in ('evidence', 'knowledge'):
        shutil.copytree(root / n, private / n)
    catalog = Path('frontend/src/passenger/fleetCatalog.json')
    (private / catalog).parent.mkdir(parents=True)
    shutil.copyfile(root / catalog, private / catalog)
    ws = Workspace(str(private / 'evidence'))
    initial = _states(ws)
    proposals, review, exceptions, per_ship = [], [], [], []
    for d in descriptors:
        slug, receipt = d['slug'], by_slug[d['slug']]
        package = packages[slug]
        identity = json.loads((root / 'knowledge/ships' / slug / 'identity.json').read_bytes())
        name = identity['name']['value']
        data = read_map(held[slug])
        if data['cover'] != d['cover_title'] or data['pages'] != d['pages']:
            raise ValueError('DOCUMENT_IDENTITY_CHANGED')
        try:
            imo = canonical_vessel(slug, root=root)
            blocked = False
        except ValueError as exc:
            if 'QUARANTINED' not in str(exc):
                raise
            imo, blocked = package['vessel']['verified_imo'], True
        if any(c['target_vessel'] != imo for c in package['first_review_batch']):
            raise ValueError('CLAIM_VESSEL_MISMATCH')
        # Private holding only for disputed identities; never attribute to a
        # known conflicting stored IMO or silently adopt a candidate identifier.
        staged = output / 'private-intake-inputs' / urlsplit(d['url']).path.rsplit('/', 1)[1]
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(held[slug], staged)
        artifact = ws.import_artifact(str(staged), document_class='official_ship_map',
            acquired_on=datetime.fromisoformat(receipt['retrieved_at']).date().isoformat(),
            acquisition_method='direct official HTTPS retrieval; exact recorded SHA-256 comparison',
            publisher='MSC Cruises', version=None, language='en-GB',
            notes=f"Official source {d['url']}; printed edition unknown; cite-only, no artwork redistribution. "
                  f"Retrieval receipt SHA-256 {_hash(receipt)}; title establishes name, PDF prints no IMO. "
                  + ('Vessel attribution pending canonical identity resolution.' if blocked else 'Existing canonical vessel identity matched.'),
            subject_vessels=[] if blocked else [imo],
            source_identity_pages=None if blocked else {imo: 1})
        proposals.append({'slug': slug, 'proposed_artifact': artifact.to_dict(),
            'status': 'BLOCKED_IDENTITY_UNATTRIBUTED_PRIVATE_HOLDING' if blocked else 'PENDING_SOURCE_ADMISSION',
            'canonical_imo': identity['imo_number']['value'],
            'candidate_imo_as_reported': package['vessel']['verified_imo'],
            'source_revision': source_revision(artifact), 'retrieval': receipt,
            'rights': 'CITE_ONLY; artwork redistribution not authorized'})
        claims = []
        for original in package['first_review_batch']:
            index = {'page': data['index_pages'][0], 'decks': original['value'], 'label_key': key(original['name'])}
            c = bind_candidate(original, artifact, name, index)
            verify_map_reading(held[slug], c)
            claims.append(c)
            review.append({'claim': c, 'binding_sha256': _hash(c), 'research_claim': original,
                'machine_source_reading': 'TABLE_AND_INDEX_MATCH',
                'admission_state': 'BLOCKED_CANONICAL_IDENTITY' if blocked else 'PENDING_HUMAN_REVIEW',
                'recommended_disposition': 'DEFER_ADMISSION_UNTIL_IDENTITY_RESOLUTION' if blocked else 'REVIEW_SOURCE_AND_CLAIM',
                'decision': None, 'reviewer': None, 'review_date': None, 'decision_reason': None})
        batch = {'schema': 'timonelo.evidence-batch.v1', 'source_route': 'REGISTERED_LOCAL_ARTIFACT',
            'vessel_slug': slug, 'vessel_imo': imo,
            'origin_limit': 'New permitted HTTPS acquisition from official MSC host; exact byte identity verified. '
                            'No independent historical acquisition verification or artwork redistribution rights.',
            'claims': claims}
        _dump(output / 'batches' / (slug + '.json'), batch)
        try:
            result = process_private_batch(private, batch, {'decisions': []}, output / 'dry-runs' / slug)
            if blocked or result['counts'] != {'admitted': 0, 'blocked': 0, 'pending': 8, 'rejected': 0}:
                raise ValueError('UNEXPECTED_PRIVATE_BATCH_AUTHORITY')
            per_ship.append({'slug': slug, 'source_readings_verified': 8, 'pending': 8, 'identity_blocked': 0,
                             'human_decisions_recorded': result['human_approvals_recorded'], 'new_admitted': 0})
        except ValueError as exc:
            if not blocked or 'QUARANTINED' not in str(exc):
                raise
            per_ship.append({'slug': slug, 'source_readings_verified': 8, 'pending': 0, 'identity_blocked': 8,
                             'actual_factory_refusal': str(exc), 'human_decisions_recorded': 0, 'new_admitted': 0})
        chosen = {c['entity_id'] for c in claims}
        for o in package['observations']:
            if o['entity_id'] not in chosen:
                exceptions.append(deepcopy(o))
    if _states(ws) != initial or len(ws.editor.all()) != 418:
        raise ValueError('ORIGINAL_AUTHORITY_CHANGED')
    if protected != {n: _files(root / n) for n in protected}:
        raise ValueError('SOURCE_CHECKOUT_CHANGED')
    _dump(output / 'source-registration-proposal.json', {'canonical_registry_sha256': registry_hash,
        'precondition': 'Proposed IDs are NOT reserved. Rebind and re-review if the canonical index changes.',
        'canonical_registration_performed': False, 'sources': proposals})
    _dump(output / 'review-candidates.json', {'schema': 'timonelo.ship-map-review.v1', 'records': review})
    _dump(output / 'excluded-observations.json', exceptions)
    result = {'input_commit': INPUT, 'implementation_base': '885e8a5dcd9eef1f910c35764fd988528801762d',
        'sources_exact_hash_match': 7, 'source_observations_verified': len(review),
        'human_review_pending': 40, 'identity_blocked': 16, 'new_admitted': 0, 'new_human_decisions': 0,
        'original_statements_preserved': 418, 'original_authority_preserved': True,
        'canonical_registration_performed': False, 'canonical_files_changed': False,
        'excluded_observations': len(exceptions), 'ships': per_ship}
    _dump(output / 'result.json', result)
    lines = ['# Consolidated Ship Maps owner review', '',
        'PRIVATE PREPARATION ONLY. No source admission, claim approval or public publication.',
        'Proposed artifact IDs are conditional on the source Registry precondition hash. '
        'An ID, source revision, entity, value or locator change requires a new binding and review.',
        'Edition UNKNOWN means no printed edition is established; retrieval and PDF production dates are not editions.',
        'Choose APPROVE / REJECT / DEFER per observation, with actual reviewer/date/reason. '
        'An unanswered or skipped item remains PENDING. Approval is not publication authority.', '']
    for d in descriptors:
        slug = d['slug']
        lines += [f"## {d['vessel']}", '', f"Source: [{d['url']}]({d['url']})",
            f"Full SHA-256: `{d['sha256']}`. Printed edition: **UNKNOWN**. Rights: **CITE_ONLY**.",
            'Source title identifies a vessel name; this PDF prints no IMO.', '']
        for row in [r for r in review if canonical_entity(r['claim']['entity_id'])[1] == slug]:
            c = row['claim']
            lines += [f"### {c['id']} — {c['name']}", c['exact_claim'],
                f"Entity `{c['entity_id']}`; target `{c['target_vessel']}`; value `{c['value']}`; proposed `{c['artifact_id']}`.",
                f"Table: {c['locator']}. Index: page {c['source_index']['page']}, `{c['source_index']['label_key']}`, decks {c['source_index']['decks']}.",
                f"State: **{row['admission_state']}**. Binding SHA-256: `{row['binding_sha256']}`.",
                'Decision: PENDING — APPROVE / REJECT / DEFER; reviewer/date/reason: not supplied.', '']
    (output / 'HUMAN_REVIEW.md').write_text('\n'.join(lines), encoding='utf8')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--receipts', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prepare_private(a.root, a.receipts, a.output), indent=2))


if __name__ == '__main__':
    main()
