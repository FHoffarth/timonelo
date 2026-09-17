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
  GeometryJudgement,
  StagedDeckReviewRecord,
} from './types';

// Load extracted proofs for public decks
import deck05Proof from '../../../geometry/proofs/bellissima/deck05/deck05.proof.json';
import deck06Proof from '../../../geometry/proofs/bellissima/deck06/deck06.proof.json';
import deck07Proof from '../../../geometry/proofs/bellissima/deck07/deck07.proof.json';
import deck14Proof from '../../../geometry/proofs/bellissima/deck14/deck14.proof.json';
import deck05ProofProvenance from '../../../geometry/proofs/bellissima/deck05/deck05.proof.provenance.json';
import deck06ProofProvenance from '../../../geometry/proofs/bellissima/deck06/deck06.proof.provenance.json';
import deck07ProofProvenance from '../../../geometry/proofs/bellissima/deck07/deck07.proof.provenance.json';
import deck14ProofProvenance from '../../../geometry/proofs/bellissima/deck14/deck14.proof.provenance.json';
import statementsData from '../../../evidence/statements/statements.json';
import artifactIndex from '../../../evidence/artifacts/index.json';
import eventsData from '../../../evidence/events/events.json';

// Internal review-only asset (isolated inside src/deck-review/assets/).
// ART-0001 PDF page 3 (Decks 5/6/7).
import reviewSourceImagePage3 from './assets/art0001_page3.png';
import page3Provenance from './assets/art0001_page3.provenance.json';
// ART-0001 PDF page 5 (Deck 14): full-MediaBox raster served from
// `frontend/public/data/`. The canonical href is owned by the spatial-proof
// viewer and re-used here rather than re-declared, so the path exists once.
import { UNDERLAY_HREF } from '../spatial-proof/ProofCanvas';
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

/**
 * Whether a review raster binding to its source page is proven or only claimed.
 *
 * REPRODUCED - re-rendering the cited artifact page with the recorded command
 *              yields these exact bytes. The Deck 14 page-5 raster does.
 * DECLARED   - the record names an artifact and page, re-rendering does not
 *              reproduce the bytes, so the binding rests on the record alone.
 */
export type RasterVerificationLevel = 'REPRODUCED' | 'DECLARED';

export interface DeckReviewImageSource {
  uri: string;
  pdfPageNumber: number;
  sha256: string | null;
  fullMediaBox: boolean | null;
  provenanceRecord: string | null;
  verification: RasterVerificationLevel;
  verificationNote: string | null;
}

export interface DeckReviewSource {
  deckNumber: number;
  deckName: string;
  proof: any;
  proofPath: string;
  /** Digest of the exact proof bytes this review is being made against. */
  proofSha256: string;
  artifactId: string;
  artifactSha256: string;
  pdfPageNumber: number;
  image: DeckReviewImageSource;
}

interface DeckReviewWiring {
  deckName: string;
  proof: any;
  proofPath: string;
  proofProvenance: any;
  image: DeckReviewImageSource;
}

// Page 3 now has a provenance record like page 5, so both are described by the
// same mechanism rather than one being a hand-written constant. The record is
// deliberately not flattering: re-rendering ART-0001 page 3 with the recorded
// command does not reproduce these bytes, and the asset matches no page of
// ART-0001 at those settings, so its page binding is DECLARED and says so.
// Decks 5/6/7 are not closed over this. The raster is visual context beneath the
// proof and carries no geometry authority; the honest response is to surface the
// weakness, not to trust it silently and not to blank a working review surface.
const PAGE3_IMAGE: DeckReviewImageSource = {
  uri: reviewSourceImagePage3,
  pdfPageNumber: page3Provenance.source.pdf_page_number,
  sha256: page3Provenance.output_sha256,
  fullMediaBox: page3Provenance.frame.full_mediabox,
  provenanceRecord: 'frontend/src/deck-review/assets/art0001_page3.provenance.json',
  verification: 'DECLARED',
  verificationNote: page3Provenance.verification.note,
};

const DECK14_PAGE5_IMAGE: DeckReviewImageSource = {
  uri: UNDERLAY_HREF,
  pdfPageNumber: deck14Page5Provenance.source.pdf_page_number,
  sha256: deck14Page5Provenance.output_sha256,
  fullMediaBox:
    deck14Page5Provenance.frame.full_mediabox === true &&
    deck14Page5Provenance.frame.cropped === false &&
    deck14Page5Provenance.frame.review_viewport_used === false,
  provenanceRecord: 'frontend/public/data/deck14.page5.provenance.json',
  verification: 'REPRODUCED',
  verificationNote: null,
};

const DECK_REVIEW_WIRING: Readonly<Record<number, DeckReviewWiring>> = Object.freeze({
  5: { deckName: 'Deck 5 (Opera)', proof: deck05Proof, proofPath: 'geometry/proofs/bellissima/deck05/deck05.proof.json', proofProvenance: deck05ProofProvenance, image: PAGE3_IMAGE },
  6: { deckName: 'Deck 6 (Musica)', proof: deck06Proof, proofPath: 'geometry/proofs/bellissima/deck06/deck06.proof.json', proofProvenance: deck06ProofProvenance, image: PAGE3_IMAGE },
  7: { deckName: 'Deck 7 (Fantasia)', proof: deck07Proof, proofPath: 'geometry/proofs/bellissima/deck07/deck07.proof.json', proofProvenance: deck07ProofProvenance, image: PAGE3_IMAGE },
  14: { deckName: 'Deck 14 (World Class)', proof: deck14Proof, proofPath: 'geometry/proofs/bellissima/deck14/deck14.proof.json', proofProvenance: deck14ProofProvenance, image: DECK14_PAGE5_IMAGE },
});

const RASTER_PROVENANCE_BY_URI: ReadonlyMap<string, any> = new Map<string, any>([
  [PAGE3_IMAGE.uri, page3Provenance],
  [DECK14_PAGE5_IMAGE.uri, deck14Page5Provenance],
]);

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
  // The same rules for every wired deck: the raster must carry a provenance
  // record, and that record must name the artifact the proof names. Previously
  // only Deck 14 was checked and Decks 5/6/7 rested on a hand-written constant.
  const rasterProvenance = RASTER_PROVENANCE_BY_URI.get(wiring.image.uri);
  if (!rasterProvenance || !wiring.image.provenanceRecord) {
    throw new DeckReviewSourceIntegrityError(
      `Review image for Deck ${deckNumber} has no provenance record.`,
    );
  }
  if (rasterProvenance.source.sha256 !== artifactSha256 || rasterProvenance.source.artifact_id !== artifactId) {
    throw new DeckReviewSourceIntegrityError(
      `Deck ${deckNumber} review image provenance names a different source artifact than the proof.`,
    );
  }
  // A raster whose bytes were reproduced from the artifact must also be a full
  // MediaBox render, or the overlay would misalign. A DECLARED raster cannot be
  // asserted either way, and says so rather than claiming a frame it has not
  // proven -- it is visual context, never geometry.
  if (wiring.image.verification === 'REPRODUCED' && wiring.image.fullMediaBox !== true) {
    throw new DeckReviewSourceIntegrityError(
      `Deck ${deckNumber} review image is not a full-MediaBox render; overlay geometry would misalign.`,
    );
  }

  // The proof is the artifact actually being adjudicated, so its bytes are
  // identified too. Everything else here was digest-bound already; leaving this
  // one out meant a staged decision could be applied to a proof that had been
  // regenerated since, against object ids and pre-states that no longer matched.
  const proofSha256 = wiring.proofProvenance?.output_sha256;
  if (typeof proofSha256 !== 'string' || proofSha256.length !== 64) {
    throw new DeckReviewSourceIntegrityError(
      `Proof for Deck ${deckNumber} has no usable provenance digest.`,
    );
  }
  if (wiring.proofProvenance.proof?.deck_number !== deckNumber) {
    throw new DeckReviewSourceIntegrityError(
      `Proof provenance for Deck ${deckNumber} describes deck ${String(wiring.proofProvenance.proof?.deck_number)}.`,
    );
  }
  if (wiring.proofProvenance.proof?.object_count !== (proof.objects || []).length) {
    throw new DeckReviewSourceIntegrityError(
      `Proof provenance for Deck ${deckNumber} counts ${String(wiring.proofProvenance.proof?.object_count)} objects, proof holds ${(proof.objects || []).length}.`,
    );
  }

  return {
    deckNumber,
    deckName: wiring.deckName,
    proof,
    proofPath: wiring.proofPath,
    proofSha256,
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
 *   - a DIRECT/CALCULATED read cites at least one evidence event, and every
 *     cited event exists in evidence/events/events.json, is not superseded, and
 *     is bound to this claim (entity_id, question_id and observed_value agree)
 *     (INFERRED identity is refused: derivation closure is not verifiable here),
 *   - the value agrees (exists = true; deck = the reviewed deck),
 *   - the source artifact's subject_vessels include the vessel.
 *
 * LIMITATION, stated plainly: this cannot re-verify artifact digests, and it
 * is not sufficient for backend admission. The backend `PublicationAuthority` remains
 * the authority and checks things this cannot -- artifact bytes on disk, private
 * source re-verifiability, question metadata, rule provenance for INFERRED.
 *
 * An earlier version of this comment claimed the check could never be looser
 * than that gate. It was: it accepted any non-empty `evidence_event_ids` array,
 * so a statement citing an event id that does not exist passed here and was
 * refused by the backend with UNKNOWN_EVIDENCE_EVENT. Event resolution and claim
 * binding are checked now, which closes that specific gap. It does not make the
 * broader claim true, so the broader claim is gone rather than restated.
 */
const CABIN_ENTITY_SCOPE = 'MSC-BELLISSIMA';
const VESSEL_IMO = 'IMO9766205';
const ALLOWED_PUBLISH = new Set(['PUBLISH_ALLOWED', 'PUBLISH_ALLOWED_WITH_WARNINGS']);
const INACTIVE_REVIEW = new Set(['SUPERSEDED', 'REJECTED']);

function normalizeImo(v: unknown): string {
  return String(v ?? '').replace(/\s+/g, '').toUpperCase().replace(/^(IMO)?/, 'IMO');
}

/**
 * Events by id, with superseded events removed.
 *
 * `supersedes` names the event a later observation replaces, so anything named
 * there is no longer current and must not back a claim.
 */
function indexEvents(events: any[]): { byId: Map<string, any>; superseded: Set<string> } {
  const byId = new Map<string, any>();
  const superseded = new Set<string>();
  for (const e of events || []) {
    if (!e || typeof e.event_id !== 'string') continue;
    byId.set(e.event_id, e);
    if (typeof e.supersedes === 'string' && e.supersedes) superseded.add(e.supersedes);
  }
  return { byId, superseded };
}

/** Whether an observation records the value a statement asserts. */
function observedValueAgrees(observed: unknown, claimed: unknown): boolean {
  if (typeof observed === 'boolean' || typeof claimed === 'boolean') {
    return String(observed).toLowerCase() === String(claimed).toLowerCase();
  }
  if (observed === claimed) return true;
  if (observed === null || observed === undefined || claimed === null || claimed === undefined) return false;
  return String(observed).trim() === String(claimed).trim();
}

/**
 * Every reason a cited event cannot back this statement.
 *
 * Existence alone is not backing: the event has to be about this entity, this
 * question and this value, or it is somebody else's observation being counted.
 */
function eventBindingBlockers(
  sid: string,
  raw: any,
  events: { byId: Map<string, any>; superseded: Set<string> },
): string[] {
  const blockers: string[] = [];
  const cited: unknown[] = Array.isArray(raw.evidence_event_ids) ? raw.evidence_event_ids : [];
  for (const rawId of cited) {
    const id = typeof rawId === 'string' ? rawId : String(rawId);
    const event = events.byId.get(id);
    if (!event) {
      blockers.push(`${sid} cites evidence event ${id}, which is not a recorded event`);
      continue;
    }
    if (events.superseded.has(id)) {
      blockers.push(`${sid} cites evidence event ${id}, which has been superseded`);
      continue;
    }
    if (event.entity_id !== raw.entity_id) {
      blockers.push(`${sid} cites ${id}, which observed entity ${String(event.entity_id)}, not ${String(raw.entity_id)}`);
    }
    if (raw.question_id !== undefined && event.question_id !== raw.question_id) {
      blockers.push(`${sid} cites ${id}, which answered question ${String(event.question_id)}, not ${String(raw.question_id)}`);
    }
    if (!observedValueAgrees(event.observed_value, raw.value)) {
      blockers.push(
        `${sid} cites ${id}, which observed '${String(event.observed_value)}', not the claimed '${String(raw.value)}'`,
      );
    }
  }
  return blockers;
}

function statementIsActive(raw: any): boolean {
  const review = raw.human_review_state ?? raw.review_state;
  return !INACTIVE_REVIEW.has(String(review));
}

function statementBlockers(
  sid: string,
  raw: any,
  artifacts: Record<string, any>,
  events: { byId: Map<string, any>; superseded: Set<string> },
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
  } else {
    blockers.push(...eventBindingBlockers(sid, raw, events));
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
  events: any[] = eventsData as any[],
): CabinIdentityViewModel {
  const cabin = String(cabinNumber ?? '').trim();
  const expectedEntityId = `cabin:${CABIN_ENTITY_SCOPE}:${cabin}`;
  const eventIndex = indexEvents(events);

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
  // `vesselOwnershipConsistent` reports one thing only: whether every artifact
  // behind the statements we examined names this vessel. It used to be ANDed
  // with `decks.length > 0`, so a missing cabin.deck statement was reported as a
  // vessel-ownership failure -- which was not what had been found. Statement
  // count problems belong in `blockers`, and are there.
  const vesselChecks: boolean[] = [];
  const e = statementBlockers(existsId, existsRaw, artifacts, eventIndex);
  blockers.push(...e.blockers);
  vesselChecks.push(e.vesselOk);
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
    // Competing statements are still checked for vessel ownership, rather than
    // their artifacts going unexamined because the count was wrong.
    for (const [deckId, deckRaw] of decks) {
      vesselChecks.push(statementBlockers(deckId, deckRaw, artifacts, eventIndex).vesselOk);
    }
  } else {
    const [deckId, deckRaw] = decks[0];
    deckStatementId = deckId;
    const d = statementBlockers(deckId, deckRaw, artifacts, eventIndex);
    blockers.push(...d.blockers);
    vesselChecks.push(d.vesselOk);
    if (String(deckRaw.value) !== String(deckNumber)) {
      blockers.push(`${deckId} places the cabin on deck '${String(deckRaw.value)}', not Deck ${deckNumber}`);
    }
  }
  const vesselOk = vesselChecks.every(Boolean);

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
      const objects = w.proof?.objects || [];
      // Counted from the staged decisions actually held for that deck, not set
      // to the object count. Staged decisions are scoped to the deck being
      // viewed, so other decks correctly report every object as unreviewed.
      const unreviewed =
        n === deckNumber
          ? objects.filter((o: any) => (stagedDecisions[o.object_id]?.state ?? 'UNREVIEWED') === 'UNREVIEWED').length
          : objects.length;
      return { deckNumber: n, deckName: w.deckName, objectCount: objects.length, unreviewedCount: unreviewed };
    }),
    sourceInfo: {
      artifactId: source.artifactId,
      artifactSha256: source.artifactSha256,
      pageNumber: source.pdfPageNumber,
      sourceImageUri: source.image.uri,
      sourceImageSha256: source.image.sha256,
      sourceImageProvenanceRecord: source.image.provenanceRecord,
      sourceImageVerification: source.image.verification,
      proofSha256: source.proofSha256,
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
  // No review decision can promote. Retained so the staged record states the
  // count explicitly rather than leaving a reader to infer it.
  const promoted = 0;
  let blocked = 0;

  for (const c of vm.candidates) {
    if (c.decision.state === 'UNREVIEWED') continue;

    // A human review decision is not an evidence event.
    //
    // ACCEPT used to set evidence_condition to SUPPORTED. It should never have:
    // a person looking at a polygon against a drawing has performed a review
    // act, not an observation recorded against an artifact, and SUPPORTED is
    // what an evidence event earns. Writing it here is caller-set SUPPORTED --
    // the defect the backend spent three rounds removing -- and it left an
    // accepted object one axis from passenger publication, with that axis set by
    // the same click.
    //
    // The evidence condition is therefore carried through untouched. The human
    // judgement is recorded in its own field, `geometryJudgement`, where it can
    // be read without being mistaken for evidence.
    let toReview = c.humanReviewState;
    let toPublish = c.publishStatus;
    const toCondition = c.evidenceCondition;
    let geometryJudgement: GeometryJudgement = 'NOT_JUDGED';
    let outcome = 'NO_CHANGE';

    if (c.decision.state === 'ACCEPT') {
      toReview = 'APPROVED';
      geometryJudgement = 'ACCEPTED';
      // Publication still requires SUPPORTED evidence, which no review act
      // creates, so an accepted envelope stays blocked whatever its identity.
      toPublish = 'PUBLISH_BLOCKED';
      outcome = c.isAdmittedIdentity
        ? 'GEOMETRY_APPROVED_IDENTITY_ADMITTED_EVIDENCE_PENDING'
        : 'GEOMETRY_APPROVED_IDENTITY_BLOCKED';
      blocked++;
    } else if (c.decision.state === 'REJECT') {
      toReview = 'REJECTED';
      toPublish = 'PUBLISH_BLOCKED';
      geometryJudgement = 'REJECTED';
      outcome = 'REJECTED_BY_REVIEWER';
      blocked++;
    } else if (c.decision.state === 'NEEDS_CORRECTION') {
      toReview = 'UNDER_REVIEW';
      toPublish = 'PUBLISH_BLOCKED';
      geometryJudgement = 'NEEDS_CORRECTION';
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
      geometryJudgement,
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
    proof_sha256: source.proofSha256,
    proof_schema: String(source.proof.schema ?? ''),
    source: {
      artifact_id: source.artifactId,
      artifact_sha256: source.artifactSha256,
      pdf_page_number: source.pdfPageNumber,
      review_image_uri: source.image.uri,
      review_image_sha256: source.image.sha256,
      review_image_provenance_record: source.image.provenanceRecord,
      review_image_verification: source.image.verification,
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
