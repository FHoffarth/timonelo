/**
 * Public Deck Geometry Review Adapter (ADR-0002 / ADR-0003).
 * Bridges extracted proof JSON artifacts with the Human Review Workspace.
 *
 * Every reviewable deck is wired explicitly in `DECK_REVIEW_SOURCES`, together
 * with the proof it reviews and the source raster a human compares it against.
 * There is no default deck: asking for a deck that is not wired is an error,
 * because showing one deck's proof under another deck's number is a silent
 * truth fabrication.
 */

import {
  SpatialReviewCandidateViewModel,
  DeckReviewWorkspaceViewModel,
  ReviewDecisionState,
  VenueAssociationViewModel,
  ReviewAuditLogEntry,
  CabinIdentityViewModel,
  IdentityPath,
  FinalizeReviewResult,
  StagedDeckReviewRecord,
} from './types';

// Load extracted proofs for public decks
import deck05Proof from '../../../geometry/proofs/bellissima/deck05/deck05.proof.json';
import deck06Proof from '../../../geometry/proofs/bellissima/deck06/deck06.proof.json';
import deck07Proof from '../../../geometry/proofs/bellissima/deck07/deck07.proof.json';
import deck14Proof from '../../../geometry/proofs/bellissima/deck14/deck14.proof.json';
import statementsData from '../../../evidence/statements/statements.json';
import artifactIndex from '../../../evidence/artifacts/index.json';

// Internal review-only asset (isolated inside src/deck-review/assets/).
// ART-0001 PDF page 3 (Decks 5/6/7). No provenance record exists for it in the
// repository, so its digest is reported as null rather than asserted.
import reviewSourceImagePage3 from './assets/art0001_page3.png';
// ART-0001 PDF page 5 (Deck 14): full-MediaBox raster served from
// `frontend/public/data/`, with a recorded provenance (source digest, page,
// frame, render command, output digest) guarded by tests/test_spatial_proof_underlay.py.
import deck14Page5Provenance from '../../public/data/deck14.page5.provenance.json';

export class UnsupportedDeckReviewError extends Error {
  constructor(deckNumber: unknown) {
    super(
      `Deck ${String(deckNumber)} is not available for review: no governed proof and source review image are wired for it.`,
    );
    this.name = 'UnsupportedDeckReviewError';
  }
}

export class DeckReviewSourceIntegrityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DeckReviewSourceIntegrityError';
  }
}

export interface DeckReviewImageSource {
  uri: string;
  pdfPageNumber: number;
  sha256: string | null;
  fullMediaBox: boolean | null;
  provenanceRecord: string | null;
}

export interface DeckReviewSource {
  deckNumber: number;
  deckName: string;
  proof: any;
  proofPath: string;
  artifactId: string;
  artifactSha256: string;
  pdfPageNumber: number;
  image: DeckReviewImageSource;
}

interface DeckReviewWiring {
  deckName: string;
  proof: any;
  proofPath: string;
  image: DeckReviewImageSource;
}

const PAGE3_IMAGE: DeckReviewImageSource = {
  uri: reviewSourceImagePage3,
  pdfPageNumber: 3,
  sha256: null,
  fullMediaBox: null,
  provenanceRecord: null,
};

const DECK14_PAGE5_IMAGE: DeckReviewImageSource = {
  uri: `/data/${deck14Page5Provenance.asset}`,
  pdfPageNumber: deck14Page5Provenance.source.pdf_page_number,
  sha256: deck14Page5Provenance.output_sha256,
  fullMediaBox:
    deck14Page5Provenance.frame.full_mediabox === true &&
    deck14Page5Provenance.frame.cropped === false &&
    deck14Page5Provenance.frame.review_viewport_used === false,
  provenanceRecord: 'frontend/public/data/deck14.page5.provenance.json',
};

const DECK_REVIEW_WIRING: Readonly<Record<number, DeckReviewWiring>> = Object.freeze({
  5: { deckName: 'Deck 5 (Opera)', proof: deck05Proof, proofPath: 'geometry/proofs/bellissima/deck05/deck05.proof.json', image: PAGE3_IMAGE },
  6: { deckName: 'Deck 6 (Musica)', proof: deck06Proof, proofPath: 'geometry/proofs/bellissima/deck06/deck06.proof.json', image: PAGE3_IMAGE },
  7: { deckName: 'Deck 7 (Fantasia)', proof: deck07Proof, proofPath: 'geometry/proofs/bellissima/deck07/deck07.proof.json', image: PAGE3_IMAGE },
  14: { deckName: 'Deck 14 (World Class)', proof: deck14Proof, proofPath: 'geometry/proofs/bellissima/deck14/deck14.proof.json', image: DECK14_PAGE5_IMAGE },
});

export const SUPPORTED_REVIEW_DECKS: readonly number[] = Object.freeze(
  Object.keys(DECK_REVIEW_WIRING).map(Number).sort((a, b) => a - b),
);

/**
 * Resolve the governed proof and review raster for one deck, or fail closed.
 *
 * Proof schemas differ between decks (`source.page_number` on 5/6/7,
 * `source.pdf_page_number` on 14). Neither is defaulted: a proof whose page,
 * deck or artifact digest cannot be read, or disagrees with its review raster,
 * is refused rather than displayed.
 */
export function resolveDeckReviewSource(deckNumber: number): DeckReviewSource {
  if (!Number.isInteger(deckNumber) || !Object.prototype.hasOwnProperty.call(DECK_REVIEW_WIRING, deckNumber)) {
    throw new UnsupportedDeckReviewError(deckNumber);
  }
  const wiring = DECK_REVIEW_WIRING[deckNumber];
  const proof = wiring.proof;

  if (proof?.deck?.number !== deckNumber) {
    throw new DeckReviewSourceIntegrityError(
      `Proof wired for Deck ${deckNumber} declares deck ${String(proof?.deck?.number)}.`,
    );
  }
  const pdfPageNumber = proof.source?.pdf_page_number ?? proof.source?.page_number;
  if (!Number.isInteger(pdfPageNumber)) {
    throw new DeckReviewSourceIntegrityError(`Proof for Deck ${deckNumber} declares no source PDF page.`);
  }
  const artifactId = proof.source?.artifact_id;
  const artifactSha256 = proof.source?.artifact_sha256 ?? proof.source?.sha256;
  if (!artifactId || !artifactSha256) {
    throw new DeckReviewSourceIntegrityError(`Proof for Deck ${deckNumber} declares no source artifact identity.`);
  }
  if (wiring.image.pdfPageNumber !== pdfPageNumber) {
    throw new DeckReviewSourceIntegrityError(
      `Review image for Deck ${deckNumber} is PDF page ${wiring.image.pdfPageNumber}, but the proof is PDF page ${pdfPageNumber}.`,
    );
  }
  if (deckNumber === 14) {
    if (deck14Page5Provenance.source.sha256 !== artifactSha256 || deck14Page5Provenance.source.artifact_id !== artifactId) {
      throw new DeckReviewSourceIntegrityError('Deck 14 review image provenance names a different source artifact than the proof.');
    }
    if (wiring.image.fullMediaBox !== true) {
      throw new DeckReviewSourceIntegrityError('Deck 14 review image is not a full-MediaBox render; overlay geometry would misalign.');
    }
  }

  return {
    deckNumber,
    deckName: wiring.deckName,
    proof,
    proofPath: wiring.proofPath,
    artifactId,
    artifactSha256,
    pdfPageNumber,
    image: wiring.image,
  };
}

const KNOWN_VENUE_ALIASES: Record<string, string> = {
  'posidonia restaurant': 'POSIDONIA RESTAURANT',
  'infinity atrium': 'INFINITY ATRIUM',
  'infinity bar': 'INFINITY BAR',
  'london theatre': 'LONDON THEATRE',
  'lighthouse restaurant': 'LIGHTHOUSE RESTAURANT',
  'galleria bellissima': 'GALLERIA BELLISSIMA',
  'bellissima bar & lounge': 'BELLISSIMA BAR & LOUNGE',
  'bellissima lounge': 'BELLISSIMA BAR & LOUNGE',
  'edge cocktail bar': 'EDGE COCKTAIL BAR',
  'hola! tapas bar': 'HOLA! TAPAS BAR',
  'tapas bar': 'HOLA! TAPAS BAR',
  'imperial casino': 'IMPERIAL CASINO',
  'champagne bar': 'CHAMPAGNE BAR',
  'kaito sushi bar': 'KAITO SUSHI BAR',
  'tv studio & bar': 'TV STUDIO & BAR',
  'tv studio': 'TV STUDIO & BAR',
  'carousel lounge': 'CAROUSEL LOUNGE',
  'msc aurea spa': 'MSC AUREA SPA',
  "butcher's cut": "BUTCHER'S CUT",
  'kaito teppanyaki': 'KAITO TEPPANYAKI',
};

const BANNED_PHANTOM_REVIEWERS = new Set([
  '',
  'unspecified_reviewer',
  'human_curator',
  'null',
  'none',
  'undefined',
  'system',
  'agent',
  'machine',
]);

export function matchVenueStatement(
  candidateLabel: string,
  deckNumber: number
): VenueAssociationViewModel {
  const cleanLabel = candidateLabel.trim().toLowerCase();
  const canonicalTarget = KNOWN_VENUE_ALIASES[cleanLabel];

  const matches: Array<{ id: string; raw: any }> = [];

  for (const [sid, raw] of Object.entries(statementsData as Record<string, any>)) {
    if (raw.statement_type !== 'deck.venue_present') continue;

    const sDecks = raw.value || [raw.deck_number];
    const deckList = Array.isArray(sDecks) ? sDecks : [sDecks];
    if (!deckList.includes(deckNumber) && raw.deck_number !== deckNumber) {
      continue;
    }

    const target = (raw.target_entity || '').toUpperCase();
    const locator = (raw.locator || '').toUpperCase();

    let isMatch = false;
    if (canonicalTarget && (target.includes(canonicalTarget) || locator.includes(`"${canonicalTarget}"`))) {
      isMatch = true;
    } else if (cleanLabel.length > 2 && (target.includes(cleanLabel.toUpperCase()) || locator.includes(`"${cleanLabel.toUpperCase()}"`))) {
      isMatch = true;
    }

    if (isMatch) {
      matches.push({ id: sid, raw });
    }
  }

  if (matches.length === 1) {
    const hit = matches[0];
    const isAdmitted =
      hit.raw.evidence_condition === 'SUPPORTED' &&
      hit.raw.human_review_state === 'APPROVED' &&
      (hit.raw.publish_status === 'PUBLISH_ALLOWED' || hit.raw.publish_status === 'PUBLISH_ALLOWED_WITH_WARNINGS');

    return {
      state: 'MATCHED',
      statementId: hit.id,
      statementName: hit.raw.target_entity || cleanLabel.toUpperCase(),
      statementStatus: hit.raw.publish_status || 'UNKNOWN',
      isAdmittedIdentity: isAdmitted,
      reason: isAdmitted
        ? `Exact match with admitted statement ${hit.id} on Deck ${deckNumber}`
        : `Matched statement ${hit.id} on Deck ${deckNumber} (Statement currently ${hit.raw.publish_status || 'DRAFT'})`,
    };
  } else if (matches.length > 1) {
    return {
      state: 'AMBIGUOUS',
      isAdmittedIdentity: false,
      reason: `Multiple competing statements (${matches.length}) found for '${candidateLabel}' on Deck ${deckNumber}`,
    };
  } else {
    return {
      state: 'NO_MATCH',
      isAdmittedIdentity: false,
      reason: `No matching registered venue statement found on Deck ${deckNumber}`,
    };
  }
}

/**
 * Cabin identity admission.
 *
 * A cabin is not a venue. Its identity rests on `cabin.exists` and `cabin.deck`
 * statements scoped to the vessel's entity namespace, read from an artifact that
 * names that vessel. The venue matcher (`deck.venue_present`) is never consulted.
 *
 * Admission here is refused unless, for BOTH statements:
 *   - the record carries the canonical lifecycle axes (a legacy `review_state`
 *     string is not evidence — see src/timonelo/evidence/editor.py),
 *   - evidence_condition SUPPORTED, human_review_state APPROVED,
 *     publish_status PUBLISH_ALLOWED[_WITH_WARNINGS],
 *   - a DIRECT/CALCULATED read cites at least one evidence event
 *     (INFERRED identity is refused: derivation closure is not verifiable here),
 *   - the value agrees (exists = true; deck = the reviewed deck),
 *   - the source artifact's subject_vessels include the vessel.
 *
 * This is a staging-time check over decoded records. It cannot re-verify artifact
 * digests or event resolution; the backend `PublicationAuthority` remains the
 * authority. It can only ever be stricter than that gate, never a substitute.
 */
const CABIN_ENTITY_SCOPE = 'MSC-BELLISSIMA';
const VESSEL_IMO = 'IMO9766205';
const ALLOWED_PUBLISH = new Set(['PUBLISH_ALLOWED', 'PUBLISH_ALLOWED_WITH_WARNINGS']);
const INACTIVE_REVIEW = new Set(['SUPERSEDED', 'REJECTED']);

function normalizeImo(v: unknown): string {
  return String(v ?? '').replace(/\s+/g, '').toUpperCase().replace(/^(IMO)?/, 'IMO');
}

function statementIsActive(raw: any): boolean {
  const review = raw.human_review_state ?? raw.review_state;
  return !INACTIVE_REVIEW.has(String(review));
}

function statementBlockers(
  sid: string,
  raw: any,
  artifacts: Record<string, any>,
): { blockers: string[]; vesselOk: boolean } {
  const blockers: string[] = [];
  if (raw.human_review_state === undefined && raw.review_state !== undefined) {
    blockers.push(
      `${sid} carries only legacy review_state '${raw.review_state}'; canonical lifecycle axes are absent and a stored string is not evidence`,
    );
  }
  if (raw.evidence_condition !== 'SUPPORTED') {
    blockers.push(`${sid} evidence_condition is ${raw.evidence_condition ?? 'UNKNOWN (absent)'}`);
  }
  if (raw.human_review_state !== undefined && raw.human_review_state !== 'APPROVED') {
    blockers.push(`${sid} human_review_state is ${raw.human_review_state}`);
  }
  if (!ALLOWED_PUBLISH.has(raw.publish_status)) {
    blockers.push(`${sid} publish_status is ${raw.publish_status ?? 'PUBLISH_BLOCKED (absent)'}`);
  }
  if (raw.method === 'INFERRED') {
    blockers.push(`${sid} is INFERRED; identity derivation closure cannot be verified in the review workspace`);
  } else if (!Array.isArray(raw.evidence_event_ids) || raw.evidence_event_ids.length === 0) {
    blockers.push(`${sid} cites no evidence events`);
  }
  const artifact = artifacts[raw.artifact_id];
  const vessels: unknown[] = Array.isArray(artifact?.subject_vessels) ? artifact.subject_vessels : [];
  const vesselOk = vessels.some((v) => normalizeImo(v) === VESSEL_IMO);
  if (!vesselOk) {
    blockers.push(`${sid} source artifact ${raw.artifact_id ?? '(none)'} does not name vessel ${VESSEL_IMO}`);
  }
  return { blockers, vesselOk };
}

export function matchCabinIdentityStatement(
  cabinNumber: string,
  deckNumber: number,
  statements: Record<string, any> = statementsData as Record<string, any>,
  artifacts: Record<string, any> = artifactIndex as Record<string, any>,
): CabinIdentityViewModel {
  const cabin = String(cabinNumber ?? '').trim();
  const expectedEntityId = `cabin:${CABIN_ENTITY_SCOPE}:${cabin}`;

  const exists: Array<[string, any]> = [];
  const decks: Array<[string, any]> = [];
  for (const [sid, raw] of Object.entries(statements)) {
    if (!raw || raw.entity_id !== expectedEntityId || !statementIsActive(raw)) continue;
    if (raw.statement_type === 'cabin.exists') exists.push([sid, raw]);
    else if (raw.statement_type === 'cabin.deck') decks.push([sid, raw]);
  }

  const base = { cabinNumber: cabin, expectedEntityId };

  if (exists.length === 0) {
    return {
      ...base,
      state: 'NO_STATEMENT',
      vesselOwnershipConsistent: false,
      isAdmittedIdentity: false,
      blockers: [`No active cabin.exists statement for ${expectedEntityId}`],
      reason: `No cabin identity statement registered for ${expectedEntityId}`,
    };
  }
  if (exists.length > 1) {
    return {
      ...base,
      state: 'AMBIGUOUS',
      vesselOwnershipConsistent: false,
      isAdmittedIdentity: false,
      blockers: [`${exists.length} competing active cabin.exists statements for ${expectedEntityId}`],
      reason: `Multiple competing cabin identity statements for ${expectedEntityId}`,
    };
  }

  const [existsId, existsRaw] = exists[0];
  const blockers: string[] = [];
  const e = statementBlockers(existsId, existsRaw, artifacts);
  blockers.push(...e.blockers);
  let vesselOk = e.vesselOk;
  if (String(existsRaw.value).toLowerCase() !== 'true') {
    blockers.push(`${existsId} value is '${String(existsRaw.value)}', not 'true'`);
  }

  let deckStatementId: string | undefined;
  if (decks.length !== 1) {
    blockers.push(
      decks.length === 0
        ? `No active cabin.deck statement for ${expectedEntityId}`
        : `${decks.length} competing active cabin.deck statements for ${expectedEntityId}`,
    );
    vesselOk = vesselOk && decks.length > 0;
  } else {
    const [deckId, deckRaw] = decks[0];
    deckStatementId = deckId;
    const d = statementBlockers(deckId, deckRaw, artifacts);
    blockers.push(...d.blockers);
    vesselOk = vesselOk && d.vesselOk;
    if (String(deckRaw.value) !== String(deckNumber)) {
      blockers.push(`${deckId} places the cabin on deck '${String(deckRaw.value)}', not Deck ${deckNumber}`);
    }
  }

  const admitted = blockers.length === 0;
  return {
    ...base,
    state: admitted ? 'ADMITTED' : 'FOUND_UNADMITTED',
    existsStatementId: existsId,
    deckStatementId,
    vesselOwnershipConsistent: vesselOk,
    isAdmittedIdentity: admitted,
    blockers,
    reason: admitted
      ? `Cabin identity ${expectedEntityId} admitted via ${existsId}${deckStatementId ? ` + ${deckStatementId}` : ''}`
      : `Cabin identity statements exist for ${expectedEntityId} but are not admitted (${blockers.length} blocker${blockers.length === 1 ? '' : 's'})`,
  };
}

function deckBoundsFrom(proof: any): [number, number, number, number] {
  const declared = proof.review_viewport?.normalized_bbox;
  if (Array.isArray(declared) && declared.length === 4) {
    return declared as [number, number, number, number];
  }
  // No normalized viewport declared (Deck 14 marks its viewport DISPLAY_ONLY in
  // PDF points). Frame the review on the union of the proof's own envelopes.
  let minX = 1, minY = 1, maxX = 0, maxY = 0;
  for (const o of proof.objects || []) {
    const b = o.normalized_bbox;
    if (!Array.isArray(b) || b.length !== 4) continue;
    minX = Math.min(minX, b[0]);
    minY = Math.min(minY, b[1]);
    maxX = Math.max(maxX, b[2]);
    maxY = Math.max(maxY, b[3]);
  }
  return maxX > minX && maxY > minY ? [minX, minY, maxX, maxY] : [0, 0, 1, 1];
}

export function buildDeckReviewWorkspaceViewModel(
  deckNumber: number,
  stagedDecisions: Record<string, { state: ReviewDecisionState; note?: string; reviewer?: string; reviewedAt?: string }> = {}
): DeckReviewWorkspaceViewModel {
  const source = resolveDeckReviewSource(deckNumber);
  const proof = source.proof;
  const rawObjects = proof.objects || [];

  const candidates: SpatialReviewCandidateViewModel[] = rawObjects.map((obj: any) => {
    const rawBbox = obj.normalized_bbox || [0, 0, 1, 1];
    const center: [number, number] = [
      (rawBbox[0] + rawBbox[2]) / 2,
      (rawBbox[1] + rawBbox[3]) / 2,
    ];

    const staged = stagedDecisions[obj.object_id] || { state: 'UNREVIEWED' };
    const isCabin = obj.semantic_type === 'cabin' || Boolean(obj.cabin_number);
    const extractedLabel = obj.label || (obj.cabin_number ? `Cabin ${obj.cabin_number}` : obj.object_id);

    const venueAssoc: VenueAssociationViewModel = isCabin
      ? {
          state: 'NO_MATCH',
          isAdmittedIdentity: false,
          reason: 'Not applicable: cabin identity is admitted through cabin statements, not venue statements',
        }
      : matchVenueStatement(obj.label || obj.object_id, deckNumber);

    let semanticType: 'venue' | 'cabin' | 'vertical_core' | 'unknown' = 'unknown';
    if (isCabin) {
      semanticType = 'cabin';
    } else if (obj.semantic_type === 'vertical_core_region' || (obj.label || '').toUpperCase().includes('LIFT')) {
      semanticType = 'vertical_core';
    } else if (obj.semantic_type === 'venue' || venueAssoc.state === 'MATCHED') {
      semanticType = 'venue';
    }

    const candidateCategory =
      semanticType === 'venue'
        ? 'Public Venue Candidate'
        : semanticType === 'vertical_core'
        ? 'Vertical Core Candidate'
        : semanticType === 'cabin'
        ? 'Stateroom Candidate'
        : 'Generic Public Space';

    let identityPath: IdentityPath;
    let cabinIdentity: CabinIdentityViewModel | undefined;
    let isAdmittedIdentity: boolean;
    if (semanticType === 'cabin') {
      identityPath = 'CABIN';
      cabinIdentity = obj.cabin_number
        ? matchCabinIdentityStatement(String(obj.cabin_number), deckNumber)
        : {
            state: 'NO_STATEMENT',
            cabinNumber: '',
            expectedEntityId: '',
            vesselOwnershipConsistent: false,
            isAdmittedIdentity: false,
            blockers: ['Cabin candidate carries no cabin_number'],
            reason: 'Cabin candidate carries no cabin_number; identity cannot be evaluated',
          };
      isAdmittedIdentity = cabinIdentity.isAdmittedIdentity;
    } else if (semanticType === 'vertical_core') {
      // No canonical identity statement type exists for vertical cores.
      identityPath = 'NONE';
      isAdmittedIdentity = false;
    } else {
      identityPath = 'VENUE';
      isAdmittedIdentity = venueAssoc.isAdmittedIdentity;
    }

    return {
      objectId: obj.object_id,
      deckNumber,
      extractedLabel,
      candidateCategory,
      semanticType,
      sourcePage: source.pdfPageNumber,
      sourceLocator: obj.source_references?.[0] || `page${source.pdfPageNumber}:unlocated`,
      sourceBbox: obj.source_bbox || [0, 0, 0, 0],
      normalizedBbox: rawBbox,
      normalizedPolygon: obj.normalized_polygon || [],
      center,
      geometryProvenance: obj.geometry_provenance || 'UNKNOWN_PROVENANCE',
      evidenceCondition: obj.evidence_condition || 'UNKNOWN',
      humanReviewState: obj.human_review_state || 'DRAFT',
      publishStatus: obj.publish_status || 'PUBLISH_BLOCKED',
      venueAssociation: venueAssoc,
      identityPath,
      cabinIdentity,
      decision: {
        state: staged.state,
        reviewer: staged.reviewer || '',
        reviewedAt: staged.reviewedAt,
        note: staged.note,
      },
      isAdmittedIdentity,
    };
  });

  const total = candidates.length;
  const accepted = candidates.filter((c) => c.decision.state === 'ACCEPT').length;
  const rejected = candidates.filter((c) => c.decision.state === 'REJECT').length;
  const needsCorrection = candidates.filter((c) => c.decision.state === 'NEEDS_CORRECTION').length;
  const unreviewed = candidates.filter((c) => c.decision.state === 'UNREVIEWED').length;

  const rawViewport = deckBoundsFrom(proof);
  const padding = 0.02;
  const minX = Math.max(0, rawViewport[0] - padding);
  const minY = Math.max(0, rawViewport[1] - padding);
  const width = Math.min(1 - minX, rawViewport[2] - rawViewport[0] + padding * 2);
  const height = Math.min(1 - minY, rawViewport[3] - rawViewport[1] + padding * 2);

  return {
    selectedDeckNumber: deckNumber,
    availableDecks: SUPPORTED_REVIEW_DECKS.map((n) => {
      const w = DECK_REVIEW_WIRING[n];
      const count = (w.proof?.objects || []).length;
      return { deckNumber: n, deckName: w.deckName, objectCount: count, unreviewedCount: count };
    }),
    sourceInfo: {
      artifactId: source.artifactId,
      artifactSha256: source.artifactSha256,
      pageNumber: source.pdfPageNumber,
      sourceImageUri: source.image.uri,
      sourceImageSha256: source.image.sha256,
      sourceImageProvenanceRecord: source.image.provenanceRecord,
      deckBounds: rawViewport,
      viewBox: { minX, minY, width, height },
    },
    candidates,
    summary: { total, accepted, rejected, needsCorrection, unreviewed },
  };
}

/**
 * Compute the staged outcome of explicit human decisions.
 *
 * This does NOT persist anything and does NOT change any proof, statement or
 * lifecycle axis in the repository. It returns audit entries and a
 * `StagedDeckReviewRecord` marked `STAGED_NOT_APPLIED`, which a human must apply
 * through the governed repository path. Only objects with an explicit
 * non-UNREVIEWED decision appear; there is no bulk path.
 */
export function finalizeReviewedDecisions(
  deckNumber: number,
  stagedDecisions: Record<string, { state: ReviewDecisionState; note?: string; reviewer?: string }>,
  reviewerName: string
): FinalizeReviewResult {
  const actor = (reviewerName || '').trim();
  if (!actor || BANNED_PHANTOM_REVIEWERS.has(actor.toLowerCase())) {
    throw new Error('Reviewer name is required before finalizing decisions.');
  }

  const source = resolveDeckReviewSource(deckNumber);
  const vm = buildDeckReviewWorkspaceViewModel(deckNumber, stagedDecisions);
  const auditEntries: ReviewAuditLogEntry[] = [];
  const generatedAt = new Date().toISOString();
  let promoted = 0;
  let blocked = 0;

  for (const c of vm.candidates) {
    if (c.decision.state === 'UNREVIEWED') continue;

    let toReview = c.humanReviewState;
    let toPublish = c.publishStatus;
    let toCondition = c.evidenceCondition;
    let outcome = 'NO_CHANGE';

    if (c.decision.state === 'ACCEPT') {
      toReview = 'APPROVED';
      toCondition = 'SUPPORTED';

      if (c.isAdmittedIdentity) {
        toPublish = 'PUBLISH_ALLOWED';
        outcome = 'PROMOTED_TO_PASSENGER_PUBLISH';
        promoted++;
      } else {
        toPublish = 'PUBLISH_BLOCKED';
        outcome = 'GEOMETRY_APPROVED_IDENTITY_BLOCKED';
        blocked++;
      }
    } else if (c.decision.state === 'REJECT') {
      toReview = 'REJECTED';
      toPublish = 'PUBLISH_BLOCKED';
      toCondition = 'UNSUPPORTED';
      outcome = 'REJECTED_BY_REVIEWER';
      blocked++;
    } else if (c.decision.state === 'NEEDS_CORRECTION') {
      toReview = 'UNDER_REVIEW';
      toPublish = 'PUBLISH_BLOCKED';
      toCondition = 'UNKNOWN';
      outcome = 'NEEDS_CORRECTION_FLAGGED';
      blocked++;
    }

    auditEntries.push({
      objectId: c.objectId,
      decision: c.decision.state,
      reviewer: actor,
      timestamp: generatedAt,
      note: c.decision.note || '',
      deckNumber,
      preReviewState: {
        humanReviewState: c.humanReviewState,
        publishStatus: c.publishStatus,
        evidenceCondition: c.evidenceCondition,
      },
      postReviewState: {
        humanReviewState: toReview,
        publishStatus: toPublish,
        evidenceCondition: toCondition,
      },
      outcome,
      identityPath: c.identityPath,
      identityReason: c.identityPath === 'CABIN' ? c.cabinIdentity?.reason : c.venueAssociation.reason,
    });
  }

  const stagedRecord: StagedDeckReviewRecord = {
    record_type: 'timonelo.deck-review.staged-record.v1',
    application_status: 'STAGED_NOT_APPLIED',
    applied_to_repository: false,
    deck_number: deckNumber,
    proof_path: source.proofPath,
    proof_schema: String(source.proof.schema ?? ''),
    source: {
      artifact_id: source.artifactId,
      artifact_sha256: source.artifactSha256,
      pdf_page_number: source.pdfPageNumber,
      review_image_uri: source.image.uri,
      review_image_sha256: source.image.sha256,
      review_image_provenance_record: source.image.provenanceRecord,
    },
    reviewer: actor,
    generated_at: generatedAt,
    entries: auditEntries,
  };

  return {
    adjudicatedObjectsCount: auditEntries.length,
    promotedToPassengerCount: promoted,
    blockedCount: blocked,
    auditEntries,
    applicationStatus: 'STAGED_NOT_APPLIED',
    stagedRecord,
  };
}
