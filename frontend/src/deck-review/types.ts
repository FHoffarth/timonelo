/**
 * Public Deck Geometry Review Adjudication Types (ADR-0002 / ADR-0003).
 */

export type ReviewDecisionState = 'UNREVIEWED' | 'ACCEPT' | 'REJECT' | 'NEEDS_CORRECTION';
export type VenueAssociationState = 'MATCHED' | 'AMBIGUOUS' | 'NO_MATCH';

export interface BBox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface VenueAssociationViewModel {
  state: VenueAssociationState;
  statementId?: string;
  statementName?: string;
  statementStatus?: string;
  isAdmittedIdentity: boolean;
  reason: string;
}

export interface ReviewDecisionViewModel {
  state: ReviewDecisionState;
  reviewer?: string;
  reviewedAt?: string;
  note?: string;
}

export interface SpatialReviewCandidateViewModel {
  objectId: string;
  deckNumber: number;
  extractedLabel: string;
  candidateCategory: string;
  semanticType: 'venue' | 'cabin' | 'vertical_core' | 'unknown';
  sourcePage: number;
  sourceLocator: string;
  sourceBbox: [number, number, number, number];
  normalizedBbox: [number, number, number, number];
  normalizedPolygon: Array<[number, number]>;
  center: [number, number];
  geometryProvenance: string;
  evidenceCondition: string;
  humanReviewState: string;
  publishStatus: string;
  venueAssociation: VenueAssociationViewModel;
  decision: ReviewDecisionViewModel;
  isAdmittedIdentity: boolean;
}

export interface DeckReviewSummary {
  total: number;
  accepted: number;
  rejected: number;
  needsCorrection: number;
  unreviewed: number;
}

export interface DeckReviewWorkspaceViewModel {
  selectedDeckNumber: number;
  availableDecks: Array<{
    deckNumber: number;
    deckName: string;
    objectCount: number;
    unreviewedCount: number;
  }>;
  sourceInfo: {
    artifactId: string;
    pageNumber: number;
    sourceImageUri: string;
    deckBounds: [number, number, number, number];
    viewBox: { minX: number; minY: number; width: number; height: number };
  };
  candidates: SpatialReviewCandidateViewModel[];
  summary: DeckReviewSummary;
}

export interface ReviewAuditLogEntry {
  objectId: string;
  decision: ReviewDecisionState;
  reviewer: string;
  timestamp: string;
  note: string;
  deckNumber: number;
  preReviewState: {
    humanReviewState: string;
    publishStatus: string;
    evidenceCondition: string;
  };
  postReviewState: {
    humanReviewState: string;
    publishStatus: string;
    evidenceCondition: string;
  };
  outcome: string;
}
