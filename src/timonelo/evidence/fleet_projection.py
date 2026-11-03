"""Read-only passenger build projection. All truth decisions remain canonical."""
from __future__ import annotations

import re


def project_fleet(workspace, catalog, as_of: str):
    statements = workspace.editor.all()
    profiles = {}
    for ship in catalog:
        slug = ship['slug']
        # Whole entity segment, not a sister-ship or substring match.
        belongs = re.compile(r'(?:^|:)' + re.escape(slug) + r'(?=:|$)', re.I)
        candidates = [s for s in statements if belongs.search(s.entity_id)]
        facts = []
        sources = {}
        for s in candidates:
            if not workspace.editor.is_currently_authoritative(s):
                continue
            answer = workspace.engine.answer(s.entity_id, s.question_id, as_of=as_of)
            if not answer.known or answer.provenance.statement_id != s.statement_id or getattr(answer, 'contested', False):
                continue
            # Initial release only supports direct, re-verifiable public sources.
            # Inference provenance needs its own representation, never a guessed source.
            if not s.artifact_id:
                continue
            artifact = workspace.registry.get(s.artifact_id)
            if artifact.private_source or not workspace.registry.verify(s.artifact_id):
                continue
            events = {e.event_id: e for e in workspace.events.all()}
            if not s.evidence_event_ids or any(
                eid not in events or events[eid].artifact_sha256 != artifact.sha256
                for eid in s.evidence_event_ids
            ):
                # Never attribute an observed fact to a different legacy artifact_id.
                continue
            kind = s.statement_type.split('.', 1)[0]
            section = {'vessel': 'identity', 'deck': 'decks', 'venue': 'venues', 'cabin': 'cabins'}.get(kind)
            if not section:
                continue
            # deck.venue_present is venue knowledge, not admitted deck geometry.
            if s.statement_type == 'deck.venue_present':
                section = 'venues'
            facts.append({'statement_id': s.statement_id, 'entity_id': s.entity_id,
                          'question_id': s.question_id, 'statement_type': s.statement_type,
                          'section': section, 'value': s.value,
                          'publish_status': s.publish_status.value,
                          'artifact_id': s.artifact_id, 'page': s.page, 'locator': s.locator})
            edition = getattr(artifact, 'version', None)
            if isinstance(edition, str) and edition.strip():
                facts[-1]['source_edition'] = edition
            sources[s.artifact_id] = {'artifact_id': s.artifact_id,
                                     'sha256': artifact.sha256, 'filename': artifact.filename}
        sections = {f['section'] for f in facts}
        level = 0
        if 'identity' in sections:
            level = 1
            if {'decks', 'venues'} <= sections:
                level = 2
                if 'cabins' in sections:
                    level = 3
        profiles[slug] = {'candidate_count': len(candidates), 'facts': facts,
                          'sources': list(sources.values()), 'level': level}
    return {'schema': 'timonelo.fleet.v1', 'as_of': as_of, 'ships': profiles}
