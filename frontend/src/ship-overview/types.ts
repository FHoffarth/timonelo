/**
 * Spatial Passenger Shell Types (ADR-0002 / ADR-0003).
 * Explicit view-model definitions for the mobile-first Ship Overview.
 */

export type BBox = [number, number, number, number];
export type Polygon = Array<[number, number]>;

export type SpatialEntityStatus = 'mapped' | 'known_but_unmapped' | 'blocked';

export type GeometryProvenanceSafe =
  | 'Mapped from official source drawing'
  | 'Mapped from official deck plan'
  | 'Location derived from verified ship layout'
  | 'Location not verified yet';

export interface SpatialEntityViewModel {
  id: string;
  name: string;
  entityType: 'cabin' | 'venue' | 'vertical_core';
  deckNumber: number;
  status: 'mapped';
  bbox: BBox;
  polygon: Polygon;
  center: [number, number];
  provenanceLabel: GeometryProvenanceSafe;
  categoryLabel: string;
  isSelectable: boolean;
  featureSummary?: string;
}

export interface UnmappedEntityViewModel {
  id: string;
  name: string;
  entityType: 'venue' | 'cabin' | 'facility';
  deckNumber: number;
  status: 'known_but_unmapped';
  statusLabel: string;
  categoryLabel: string;
  sourceNote?: string;
}

export interface DeckOptionViewModel {
  deckNumber: number;
  deckName: string;
  hasSpatialGeometry: boolean;
  statusNotice: string;
  mappedCount: number;
  unmappedCount: number;
}

export interface DeckSpatialViewModel {
  deckNumber: number;
  deckName: string;
  viewBox: {
    minX: number;
    minY: number;
    width: number;
    height: number;
  };
  deckBounds?: BBox;
  mappedEntitiesCount: number;
  unmappedEntitiesCount: number;
}

export interface SpatialTrustSummaryViewModel {
  statusBadge: string;
  sourceNotice: string;
  coverageNotice: string;
  governanceNotice: string;
  admittedCabinsCount: number;
  admittedObjectsCount: number;
  totalDecksCount: number;
  mappedDecksCount: number;
}

export interface SpatialPassengerViewModel {
  shipName: string;
  availableDecks: DeckOptionViewModel[];
  selectedDeck: DeckSpatialViewModel;
  spatialEntities: SpatialEntityViewModel[];
  unmappedEntities: UnmappedEntityViewModel[];
  trustSummary: SpatialTrustSummaryViewModel;
}

/** Raw Input Contract from Canonical Evidence & Proofs */
export interface RawProofObject {
  object_id: string;
  semantic_type: string;
  cabin_number?: string;
  source_bbox: BBox;
  normalized_bbox: BBox;
  normalized_polygon: Polygon;
  geometry_provenance: string;
  evidence_condition: string;
  human_review_state: string;
  publish_status: string;
}

export interface RawShipDeckData {
  number: number;
  name: string;
  has_geometry: boolean;
  evidence_condition?: string;
  human_review_state?: string;
  publish_status?: string;
}

export interface RawUnmappedVenue {
  statement_id: string;
  name: string;
  deck_number: number;
  category: string;
  status: string;
  source_locator?: string;
  evidence_condition?: string;
  human_review_state?: string;
  publish_status?: string;
}

export interface RawSpatialPayload {
  ship: {
    name: string;
    imo?: string;
    decks: RawShipDeckData[];
  };
  deck14_proof: {
    schema: string;
    deck: { number: number; name: string };
    objects: RawProofObject[];
    review_viewport?: { bbox: BBox };
  };
  known_unmapped_venues: RawUnmappedVenue[];
  trust_metadata?: {
    governance?: string;
    source_artifact?: string;
    geometry_truth_policy?: string;
  };
}
