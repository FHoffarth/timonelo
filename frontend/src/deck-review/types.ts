/**
 * Public Deck Geometry Review Adjudication Types (ADR-0002 / ADR-0003).
 */

export type ReviewDecisionState = 'UNREVIEWED' | 'ACCEPT' | 'REJECT' | 'NEEDS_CORRECTION';
export type VenueAssociationState = 'MATCHED' | 'AMBIGUOUS' | 'NO_MATCH';

/**
 * Which identity admission path a candidate is evaluated on. Cabins and venues
 * are different kinds of entity with different canonical statement types, so
 * neither may borrow the other's admission.
 */
export type IdentityPath = 'VENUE' | 'CABIN' | 'NONE';

export type CabinIdentityState =
  | 'ADMITTED'
  | 'FOUND_UNADMITTED'
  | 'AMBIGUOUS'
  | 'NO_STATEMENT';

export interface CabinIdentityViewModel {
  state: CabinIdentityState;
  cabinNumber: string;
  expectedEntityId: string;
  existsStatementId?: string;
  deckStatementId?: string;
  /** Artifact behind the statements names the expected vessel, and the entity id is scoped to it. */
  vesselOwnershipConsistent: boolean;
  isAdmittedIdentity: boolean;
  /** Every reason admission is refused. Empty only when admitted. */
  blockers: string[];
  reason: string;
}

export type ReviewApplicationStatus = 'STAGED_NOT_APPLIED';

/**
 * What a human decided about a geometry envelope.
 *
 * Deliberately separate from `evidence_condition`. Looking at a polygon against
 * a drawing is a review act; SUPPORTED is what an evidence event earns. Folding
 * one into the other is how a visual check became publication eligibility.
 */
export type GeometryJudgement = 'NOT_JUDGED' | 'ACCEPTED' | 'REJECTED' | 'NEEDS_CORRECTION';

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
  identityPath: IdentityPath;
  cabinIdentity?: CabinIdentityViewModel;
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
    artifactSha256: string;
    pageNumber: number;
    sourceImageUri: string;
    /** SHA-256 of the review raster when a provenance record exists for it, else null. */
    sourceImageSha256: string | null;
    sourceImageProvenanceRecord: string | null;
    /** REPRODUCED when the raster was re-rendered from the artifact; DECLARED when its page binding rests on the record alone. */
    sourceImageVerification: 'REPRODUCED' | 'DECLARED';
    /** SHA-256 of the exact proof bytes being reviewed. */
    proofSha256: string;
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
  /** The human judgement on the envelope. Never an evidence condition. */
  geometryJudgement: GeometryJudgement;
  /** Identity admission path the outcome was computed on. */
  identityPath?: IdentityPath;
  /** Why identity was or was not admitted, as evaluated at staging time. */
  identityReason?: string;
}

/**
 * A generated review record. It is NOT applied to the repository: no proof,
 * statement or lifecycle axis changes until a human applies it through the
 * governed repository path. `applied_to_repository` is always false here.
 */
export interface StagedDeckReviewRecord {
  record_type: 'timonelo.deck-review.staged-record.v1';
  application_status: ReviewApplicationStatus;
  applied_to_repository: false;
  deck_number: number;
  proof_path: string;
  /** Digest of the proof bytes the decisions were made against. An apply path must refuse a mismatch. */
  proof_sha256: string;
  proof_schema: string;
  source: {
    artifact_id: string;
    artifact_sha256: string;
    pdf_page_number: number;
    review_image_uri: string;
    review_image_sha256: string | null;
    review_image_provenance_record: string | null;
    review_image_verification: 'REPRODUCED' | 'DECLARED';
  };
  reviewer: string;
  generated_at: string;
  entries: ReviewAuditLogEntry[];
}

export interface FinalizeReviewResult {
  adjudicatedObjectsCount: number;
  promotedToPassengerCount: number;
  blockedCount: number;
  auditEntries: ReviewAuditLogEntry[];
  applicationStatus: ReviewApplicationStatus;
  stagedRecord: StagedDeckReviewRecord;
}
