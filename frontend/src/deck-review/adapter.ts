/**
 * Public Deck Geometry Review Adapter (ADR-0002 / ADR-0003).
 * Bridges extracted proof JSON artifacts with the Human Review Workspace.
 */

import {
  SpatialReviewCandidateViewModel,
  DeckReviewWorkspaceViewModel,
  ReviewDecisionState,
  VenueAssociationViewModel,
  ReviewAuditLogEntry,
} from './types';

// Load extracted proofs for public decks
import deck05Proof from '../../../geometry/proofs/bellissima/deck05/deck05.proof.json';
import deck06Proof from '../../../geometry/proofs/bellissima/deck06/deck06.proof.json';
import deck07Proof from '../../../geometry/proofs/bellissima/deck07/deck07.proof.json';
import statementsData from '../../../evidence/statements/statements.json';

// Internal review-only asset (isolated inside src/deck-review/assets/)
import reviewSourceImage from './assets/art0001_page3.png';

const PROOFS_BY_DECK: Record<number, any> = {
  5: deck05Proof,
  6: deck06Proof,
  7: deck07Proof,
};

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

export function buildDeckReviewWorkspaceViewModel(
  deckNumber: number,
  stagedDecisions: Record<string, { state: ReviewDecisionState; note?: string; reviewer?: string; reviewedAt?: string }> = {}
): DeckReviewWorkspaceViewModel {
  const proof = PROOFS_BY_DECK[deckNumber] || deck05Proof;
  const rawObjects = proof.objects || [];

  const candidates: SpatialReviewCandidateViewModel[] = rawObjects.map((obj: any) => {
    const rawBbox = obj.normalized_bbox || [0, 0, 1, 1];
    const center: [number, number] = [
      (rawBbox[0] + rawBbox[2]) / 2,
      (rawBbox[1] + rawBbox[3]) / 2,
    ];

    const venueAssoc = matchVenueStatement(obj.label || obj.object_id, deckNumber);
    const staged = stagedDecisions[obj.object_id] || { state: 'UNREVIEWED' };

    let semanticType: 'venue' | 'cabin' | 'vertical_core' | 'unknown' = 'unknown';
    if (obj.semantic_type === 'cabin' || obj.cabin_number) {
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

    return {
      objectId: obj.object_id,
      deckNumber,
      extractedLabel: obj.label || obj.object_id,
      candidateCategory,
      semanticType,
      sourcePage: proof.source?.page_number || 3,
      sourceLocator: obj.source_references?.[0] || `page3:mediabox`,
      sourceBbox: obj.source_bbox || [0, 0, 0, 0],
      normalizedBbox: rawBbox,
      normalizedPolygon: obj.normalized_polygon || [],
      center,
      geometryProvenance: obj.geometry_provenance || 'TRANSFORMED_SOURCE_GEOMETRY',
      evidenceCondition: obj.evidence_condition || 'UNKNOWN',
      humanReviewState: obj.human_review_state || 'DRAFT',
      publishStatus: obj.publish_status || 'PUBLISH_BLOCKED',
      venueAssociation: venueAssoc,
      decision: {
        state: staged.state,
        reviewer: staged.reviewer || '',
        reviewedAt: staged.reviewedAt,
        note: staged.note,
      },
      isAdmittedIdentity: venueAssoc.isAdmittedIdentity,
    };
  });

  const total = candidates.length;
  const accepted = candidates.filter((c) => c.decision.state === 'ACCEPT').length;
  const rejected = candidates.filter((c) => c.decision.state === 'REJECT').length;
  const needsCorrection = candidates.filter((c) => c.decision.state === 'NEEDS_CORRECTION').length;
  const unreviewed = candidates.filter((c) => c.decision.state === 'UNREVIEWED').length;

  const rawViewport = proof.review_viewport?.normalized_bbox || [0, 0, 1, 1];
  const padding = 0.02;
  const minX = Math.max(0, rawViewport[0] - padding);
  const minY = Math.max(0, rawViewport[1] - padding);
  const width = Math.min(1 - minX, rawViewport[2] - rawViewport[0] + padding * 2);
  const height = Math.min(1 - minY, rawViewport[3] - rawViewport[1] + padding * 2);

  return {
    selectedDeckNumber: deckNumber,
    availableDecks: [
      { deckNumber: 5, deckName: 'Deck 5 (Opera)', objectCount: (PROOFS_BY_DECK[5]?.objects || []).length, unreviewedCount: 30 },
      { deckNumber: 6, deckName: 'Deck 6 (Musica)', objectCount: (PROOFS_BY_DECK[6]?.objects || []).length, unreviewedCount: 26 },
      { deckNumber: 7, deckName: 'Deck 7 (Fantasia)', objectCount: (PROOFS_BY_DECK[7]?.objects || []).length, unreviewedCount: 15 },
    ],
    sourceInfo: {
      artifactId: proof.source?.artifact_id || 'ART-0001',
      pageNumber: proof.source?.page_number || 3,
      sourceImageUri: reviewSourceImage,
      deckBounds: rawViewport,
      viewBox: { minX, minY, width, height },
    },
    candidates,
    summary: { total, accepted, rejected, needsCorrection, unreviewed },
  };
}

export function finalizeReviewedDecisions(
  deckNumber: number,
  stagedDecisions: Record<string, { state: ReviewDecisionState; note?: string; reviewer?: string }>,
  reviewerName: string
): {
  adjudicatedObjectsCount: number;
  promotedToPassengerCount: number;
  blockedCount: number;
  auditEntries: ReviewAuditLogEntry[];
} {
  const actor = (reviewerName || '').trim();
  if (!actor || BANNED_PHANTOM_REVIEWERS.has(actor.toLowerCase())) {
    throw new Error('Reviewer name is required before finalizing decisions.');
  }

  const vm = buildDeckReviewWorkspaceViewModel(deckNumber, stagedDecisions);
  const auditEntries: ReviewAuditLogEntry[] = [];
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
      timestamp: new Date().toISOString(),
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
    });
  }

  return {
    adjudicatedObjectsCount: auditEntries.length,
    promotedToPassengerCount: promoted,
    blockedCount: blocked,
    auditEntries,
  };
}
