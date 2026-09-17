/**
 * P0 — Bellissima Deck 14 human adjudication path.
 *
 * Pins four governance properties of the review workspace:
 *   1. An unsupported deck fails closed. It never renders another deck's proof.
 *   2. Deck 14 resolves its own governed proof and its own page-5 source raster,
 *      never the page-3 raster used by Decks 5/6/7.
 *   3. Cabin identity is admitted through a cabin path, not the venue path, and
 *      a geometry ACCEPT on an unadmitted cabin identity stays PUBLISH_BLOCKED.
 *   4. Finalization produces a STAGED review record. Nothing is persisted and
 *      nothing claims to be.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { renderToStaticMarkup } from 'react-dom/server';

import DeckReviewWorkspace from './DeckReviewWorkspace';
import {
  UnsupportedDeckReviewError,
  SUPPORTED_REVIEW_DECKS,
  buildDeckReviewWorkspaceViewModel,
  finalizeReviewedDecisions,
  matchCabinIdentityStatement,
  matchVenueStatement,
  resolveDeckReviewSource,
} from './adapter';
import page3Raster from './assets/art0001_page3.png';
import deck14Proof from '../../../geometry/proofs/bellissima/deck14/deck14.proof.json';
import deck14UnderlayProvenance from '../../public/data/deck14.page5.provenance.json';
import { isAdmittedPassengerEntity } from '../ship-overview/adapter';
import { isPassengerEntityAdmitted } from '../semantic-deck/passengerAdmission';

const CABIN_14122 = 'bellissima-deck14-cabin-14122';
const ART_0001_SHA = '085d363b2ea6b4d1187fefa3125c861b104d33ec1c062732659a5ed8d2e2f5c0';
const PAGE5_RASTER_SHA = 'ea218d18464f9223c28680028e09c87c76bec3f84f962f86834e279e1c6e97ff';

const canonicalCabinExists = (overrides: Record<string, unknown> = {}) => ({
  artifact_id: 'ART-0001',
  entity_id: 'cabin:MSC-BELLISSIMA:14122',
  statement_type: 'cabin.exists',
  value: 'true',
  method: 'DIRECT',
  derivation: 'LOCAL',
  evidence_event_ids: ['EVT-SYNTHETIC-0001'],
  evidence_condition: 'SUPPORTED',
  human_review_state: 'APPROVED',
  publish_status: 'PUBLISH_ALLOWED',
  ...overrides,
});
const canonicalCabinDeck = (overrides: Record<string, unknown> = {}) =>
  canonicalCabinExists({ statement_type: 'cabin.deck', value: '14', ...overrides });

describe('P0: unsupported decks fail closed', () => {
  it('throws for an unsupported deck instead of falling back to Deck 5', () => {
    for (const deck of [0, 4, 8, 13, 15, 99, Number.NaN]) {
      expect(() => buildDeckReviewWorkspaceViewModel(deck, {})).toThrow(UnsupportedDeckReviewError);
      expect(() => resolveDeckReviewSource(deck)).toThrow(UnsupportedDeckReviewError);
    }
  });

  it('refuses to finalize decisions for an unsupported deck', () => {
    expect(() =>
      finalizeReviewedDecisions(8, { 'bellissima-deck05-venue-london-theatre': { state: 'ACCEPT' } }, 'synthetic_test_reviewer'),
    ).toThrow(UnsupportedDeckReviewError);
  });

  it('renders an explicit refusal, and no Deck 5 object, for an unsupported initial deck', () => {
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={8} />);
    expect(html).toContain('Deck 8 is not available for review');
    expect(html).not.toContain('bellissima-deck05-');
    expect(html).not.toContain('Candidate label:');
  });

  it('lists exactly the explicitly wired decks', () => {
    expect([...SUPPORTED_REVIEW_DECKS]).toEqual([5, 6, 7, 14]);
    const vm = buildDeckReviewWorkspaceViewModel(14, {});
    expect(vm.availableDecks.map((d) => d.deckNumber)).toEqual([5, 6, 7, 14]);
  });
});

describe('P0: Deck 14 resolves its own governed proof and source raster', () => {
  it('resolves the actual Deck 14 proof objects', () => {
    const vm = buildDeckReviewWorkspaceViewModel(14, {});
    expect(vm.selectedDeckNumber).toBe(14);
    expect(vm.candidates.length).toBe(deck14Proof.objects.length);
    expect(vm.candidates.length).toBe(244);
    expect(vm.candidates.map((c) => c.objectId)).toEqual(deck14Proof.objects.map((o: any) => o.object_id));
    expect(vm.candidates.every((c) => c.objectId.startsWith('bellissima-deck14-'))).toBe(true);
    expect(vm.candidates.every((c) => c.deckNumber === 14)).toBe(true);
    expect(vm.availableDecks.find((d) => d.deckNumber === 14)?.objectCount).toBe(244);
  });

  it('reports source PDF page 5 for the deck and every candidate', () => {
    const vm = buildDeckReviewWorkspaceViewModel(14, {});
    expect(vm.sourceInfo.artifactId).toBe('ART-0001');
    expect(vm.sourceInfo.artifactSha256).toBe(ART_0001_SHA);
    expect(vm.sourceInfo.pageNumber).toBe(5);
    expect(vm.candidates.every((c) => c.sourcePage === 5)).toBe(true);
    expect(vm.candidates.every((c) => c.sourceLocator.startsWith('page5:'))).toBe(true);
  });

  it('does not use the page-3 raster for Deck 14', () => {
    const vm = buildDeckReviewWorkspaceViewModel(14, {});
    expect(vm.sourceInfo.sourceImageUri).not.toBe(page3Raster);
    expect(vm.sourceInfo.sourceImageUri).toBe('/data/deck14.page5.png');
  });

  it('binds the Deck 14 raster to its recorded page-5 provenance', () => {
    const src = resolveDeckReviewSource(14);
    expect(src.image.pdfPageNumber).toBe(5);
    expect(src.image.sha256).toBe(PAGE5_RASTER_SHA);
    expect(src.image.fullMediaBox).toBe(true);
    expect(src.image.provenanceRecord).toBe('frontend/public/data/deck14.page5.provenance.json');
    expect(deck14UnderlayProvenance.source.pdf_page_number).toBe(5);
    expect(deck14UnderlayProvenance.source.sha256).toBe(ART_0001_SHA);
    expect(deck14UnderlayProvenance.output_sha256).toBe(PAGE5_RASTER_SHA);
  });

  it('keeps Decks 5/6/7 on page 3 with the page-3 raster', () => {
    for (const [deck, count] of [[5, 30], [6, 26], [7, 15]] as const) {
      const vm = buildDeckReviewWorkspaceViewModel(deck, {});
      expect(vm.candidates.length).toBe(count);
      expect(vm.sourceInfo.pageNumber).toBe(3);
      expect(vm.sourceInfo.sourceImageUri).toBe(page3Raster);
      expect(vm.candidates.every((c) => c.objectId.startsWith(`bellissima-deck0${deck}-`))).toBe(true);
    }
  });
});

describe('P0: cabin 14122 review candidate and identity admission', () => {
  it('appears as its own Deck 14 cabin candidate with governed lifecycle axes preserved', () => {
    const vm = buildDeckReviewWorkspaceViewModel(14, {});
    const matches = vm.candidates.filter((c) => c.objectId === CABIN_14122);
    expect(matches.length).toBe(1);
    const c = matches[0];
    expect(c.semanticType).toBe('cabin');
    expect(c.candidateCategory).toBe('Stateroom Candidate');
    expect(c.extractedLabel).toBe('Cabin 14122');
    expect(c.deckNumber).toBe(14);
    expect(c.sourcePage).toBe(5);
    expect(c.sourceLocator).toBe('page5:text-block-46:line-0:word-0');
    expect(c.geometryProvenance).toBe('TRANSFORMED_SOURCE_GEOMETRY');
    expect(c.evidenceCondition).toBe('UNKNOWN');
    expect(c.humanReviewState).toBe('DRAFT');
    expect(c.publishStatus).toBe('PUBLISH_BLOCKED');
    expect(c.decision.state).toBe('UNREVIEWED');
    expect(c.decision.reviewer).toBe('');
  });

  it('uses the cabin identity path, not the venue path', () => {
    const c = buildDeckReviewWorkspaceViewModel(14, {}).candidates.find((x) => x.objectId === CABIN_14122)!;
    expect(c.identityPath).toBe('CABIN');
    expect(c.venueAssociation.state).toBe('NO_MATCH');
    expect(c.venueAssociation.reason).toMatch(/not applicable/i);
    expect(c.cabinIdentity?.cabinNumber).toBe('14122');
    expect(c.cabinIdentity?.existsStatementId).toBe('STM-0001');
    expect(c.cabinIdentity?.deckStatementId).toBe('STM-0002');
    expect(c.cabinIdentity?.state).toBe('FOUND_UNADMITTED');
    expect(c.cabinIdentity?.isAdmittedIdentity).toBe(false);
    expect(c.isAdmittedIdentity).toBe(false);
    // The venue matcher never admits a cabin number as a venue.
    expect(matchVenueStatement('14122', 14).isAdmittedIdentity).toBe(false);
  });

  it('reports why the repository identity for 14122 is unadmitted', () => {
    const r = matchCabinIdentityStatement('14122', 14);
    expect(r.state).toBe('FOUND_UNADMITTED');
    expect(r.isAdmittedIdentity).toBe(false);
    expect(r.vesselOwnershipConsistent).toBe(true);
    expect(r.blockers.join(' ')).toMatch(/legacy review_state/i);
    expect(r.blockers.join(' ')).toMatch(/no evidence events/i);
  });

  it('only admits a cabin identity when canonical axes, evidence events, deck and vessel all hold', () => {
    const ok = { A: canonicalCabinExists(), B: canonicalCabinDeck() };
    expect(matchCabinIdentityStatement('14122', 14, ok).isAdmittedIdentity).toBe(true);

    const legacy = {
      A: { artifact_id: 'ART-0001', entity_id: 'cabin:MSC-BELLISSIMA:14122', statement_type: 'cabin.exists', value: 'true', method: 'DIRECT', review_state: 'PUBLISHED' },
      B: canonicalCabinDeck(),
    };
    expect(matchCabinIdentityStatement('14122', 14, legacy).isAdmittedIdentity).toBe(false);

    const noEvents = { A: canonicalCabinExists({ evidence_event_ids: [] }), B: canonicalCabinDeck() };
    expect(matchCabinIdentityStatement('14122', 14, noEvents).isAdmittedIdentity).toBe(false);

    const wrongDeck = { A: canonicalCabinExists(), B: canonicalCabinDeck({ value: '15' }) };
    expect(matchCabinIdentityStatement('14122', 14, wrongDeck).isAdmittedIdentity).toBe(false);

    const noDeck = { A: canonicalCabinExists() };
    expect(matchCabinIdentityStatement('14122', 14, noDeck).isAdmittedIdentity).toBe(false);

    const foreignVesselArtifact = { A: canonicalCabinExists({ artifact_id: 'ART-0003' }), B: canonicalCabinDeck() };
    const foreign = matchCabinIdentityStatement('14122', 14, foreignVesselArtifact);
    expect(foreign.isAdmittedIdentity).toBe(false);
    expect(foreign.vesselOwnershipConsistent).toBe(false);

    const blocked = { A: canonicalCabinExists({ publish_status: 'PUBLISH_BLOCKED' }), B: canonicalCabinDeck() };
    expect(matchCabinIdentityStatement('14122', 14, blocked).isAdmittedIdentity).toBe(false);

    const competing = { A: canonicalCabinExists(), A2: canonicalCabinExists(), B: canonicalCabinDeck() };
    const amb = matchCabinIdentityStatement('14122', 14, competing);
    expect(amb.state).toBe('AMBIGUOUS');
    expect(amb.isAdmittedIdentity).toBe(false);

    expect(matchCabinIdentityStatement('14999', 14, ok).state).toBe('NO_STATEMENT');
  });

  it('never auto-accepts 14122', () => {
    const c = buildDeckReviewWorkspaceViewModel(14, {}).candidates.find((x) => x.objectId === CABIN_14122)!;
    expect(c.decision.state).toBe('UNREVIEWED');
    const result = finalizeReviewedDecisions(14, {}, 'synthetic_test_reviewer');
    expect(result.auditEntries).toEqual([]);
  });
});

describe('P0: Deck 14 finalization stays staged and publication-blocked', () => {
  it('geometry ACCEPT with unadmitted cabin identity stays PUBLISH_BLOCKED', () => {
    const result = finalizeReviewedDecisions(14, { [CABIN_14122]: { state: 'ACCEPT' } }, 'synthetic_test_reviewer');
    expect(result.adjudicatedObjectsCount).toBe(1);
    expect(result.promotedToPassengerCount).toBe(0);
    expect(result.blockedCount).toBe(1);
    const e = result.auditEntries[0];
    expect(e.objectId).toBe(CABIN_14122);
    expect(e.preReviewState).toEqual({ humanReviewState: 'DRAFT', publishStatus: 'PUBLISH_BLOCKED', evidenceCondition: 'UNKNOWN' });
    expect(e.postReviewState.publishStatus).toBe('PUBLISH_BLOCKED');
    expect(e.outcome).toBe('GEOMETRY_APPROVED_IDENTITY_BLOCKED');
  });

  it('empty or phantom reviewer still fails on Deck 14', () => {
    const d = { [CABIN_14122]: { state: 'ACCEPT' as const } };
    for (const who of ['', '   ', 'UNSPECIFIED_REVIEWER', 'human_curator', 'system', 'agent', 'null']) {
      expect(() => finalizeReviewedDecisions(14, d, who)).toThrow('Reviewer name is required before finalizing decisions.');
    }
  });

  it('produces a staged, unapplied review record bound to the page-5 source', () => {
    const result = finalizeReviewedDecisions(14, { [CABIN_14122]: { state: 'NEEDS_CORRECTION', note: 'n' } }, 'synthetic_test_reviewer');
    expect(result.applicationStatus).toBe('STAGED_NOT_APPLIED');
    const rec = result.stagedRecord;
    expect(rec.record_type).toBe('timonelo.deck-review.staged-record.v1');
    expect(rec.application_status).toBe('STAGED_NOT_APPLIED');
    expect(rec.applied_to_repository).toBe(false);
    expect(rec.deck_number).toBe(14);
    expect(rec.proof_path).toBe('geometry/proofs/bellissima/deck14/deck14.proof.json');
    expect(rec.source.artifact_sha256).toBe(ART_0001_SHA);
    expect(rec.source.pdf_page_number).toBe(5);
    expect(rec.source.review_image_sha256).toBe(PAGE5_RASTER_SHA);
    expect(rec.reviewer).toBe('synthetic_test_reviewer');
    expect(rec.entries.length).toBe(1);
  });

  it('does not mutate the governed proof', () => {
    const before = JSON.stringify(deck14Proof);
    finalizeReviewedDecisions(14, { [CABIN_14122]: { state: 'ACCEPT' } }, 'synthetic_test_reviewer');
    buildDeckReviewWorkspaceViewModel(14, { [CABIN_14122]: { state: 'ACCEPT' } });
    expect(JSON.stringify(deck14Proof)).toBe(before);
  });

  it('keeps passenger admission for 14122 closed', () => {
    const obj = deck14Proof.objects.find((o: any) => o.object_id === CABIN_14122)!;
    expect(isAdmittedPassengerEntity(obj)).toBe(false);
    expect(
      isPassengerEntityAdmitted(
        {
          ...obj,
          vessel_id: 'msc-bellissima',
          provenance_vessel_id: 'msc-bellissima',
          data_origin: 'CANONICAL_TRUTH_ENGINE',
          method: 'DIRECT',
          derivation: 'LOCAL',
        } as any,
        'msc-bellissima',
      ),
    ).toBe(false);
  });

  it('does not render bulk approval and does not claim completed or persisted adjudication', () => {
    const html = renderToStaticMarkup(<DeckReviewWorkspace initialDeckNumber={14} />);
    expect(html).toContain('Source: ART-0001 (Page 5)');
    expect(html).toContain('/data/deck14.page5.png');
    expect(html).not.toContain('art0001_page3');
    expect(html).not.toContain('Approve all');
    expect(html).not.toContain('Bulk approve');
    expect(html).not.toContain('Approve entire deck');

    const source = readFileSync(new URL('./DeckReviewWorkspace.tsx', import.meta.url), 'utf-8');
    expect(source).not.toContain('Adjudication Complete');
    expect(source).not.toContain('stored safely in review records');
    expect(source).not.toMatch(/Admitted Deck 14: 243 Cabins/);
    expect(source).toContain('STAGED — not applied to the repository');
  });
});
