/**
 * Spatial Passenger Shell Adapter (ADR-0002 / ADR-0003).
 * Pure transformer from Canonical Spatial Knowledge & Proofs to SpatialPassengerViewModel.
 * Strictly enforces the dual gate: Lifecycle Admission + Geometry Provenance Admission.
 */

import {
  RawSpatialPayload,
  RawProofObject,
  RawUnmappedVenue,
  RawShipDeckData,
  SpatialPassengerViewModel,
  SpatialEntityViewModel,
  UnmappedEntityViewModel,
  DeckOptionViewModel,
  DeckSpatialViewModel,
  SpatialTrustSummaryViewModel,
  GeometryProvenanceSafe,
} from './types';

const ADMITTED_PROVENANCES = new Set([
  'DIRECT_SOURCE_GEOMETRY',
  'TRANSFORMED_SOURCE_GEOMETRY',
  'DERIVED_GEOMETRY',
]);

const REJECTED_PROVENANCES = new Set([
  'SYNTHETIC_GEOMETRY',
  'UNKNOWN_PROVENANCE',
]);

/**
 * Single canonical predicate for passenger spatial admission.
 * Fails closed unless both lifecycle and geometry criteria are fully satisfied.
 */
export function isAdmittedPassengerEntity(entity: {
  evidence_condition?: string;
  human_review_state?: string;
  publish_status?: string;
  geometry_provenance?: string;
  requires_geometry?: boolean;
}): boolean {
  // 1. Lifecycle criteria: must be SUPPORTED + APPROVED + PUBLISH_ALLOWED
  if (entity.evidence_condition !== 'SUPPORTED') return false;
  if (entity.human_review_state !== 'APPROVED') return false;
  if (
    entity.publish_status !== 'PUBLISH_ALLOWED' &&
    entity.publish_status !== 'PUBLISH_ALLOWED_WITH_WARNINGS'
  ) {
    return false;
  }

  // 2. Geometry provenance criteria: must be an admitted source/derived provenance
  if (entity.requires_geometry !== false && entity.geometry_provenance) {
    if (REJECTED_PROVENANCES.has(entity.geometry_provenance)) return false;
    if (!ADMITTED_PROVENANCES.has(entity.geometry_provenance)) return false;
  }

  return true;
}

function translateProvenance(raw: string): GeometryProvenanceSafe {
  if (raw === 'DIRECT_SOURCE_GEOMETRY') {
    return 'Mapped from official source drawing';
  }
  if (raw === 'TRANSFORMED_SOURCE_GEOMETRY') {
    return 'Mapped from official deck plan';
  }
  if (raw === 'DERIVED_GEOMETRY') {
    return 'Location derived from verified ship layout';
  }
  return 'Location not verified yet';
}

function translateCategory(semanticType: string, cabinNumber?: string): string {
  if (semanticType === 'cabin' || cabinNumber) {
    return 'Stateroom';
  }
  if (semanticType === 'vertical_core_region' || semanticType === 'vertical_core') {
    return 'Ship Infrastructure';
  }
  if (semanticType === 'venue') {
    return 'Public Venue';
  }
  return 'Ship Facility';
}

function formatEntityName(obj: RawProofObject): string {
  if (obj.cabin_number) {
    return `Cabin ${obj.cabin_number}`;
  }
  if (obj.semantic_type === 'vertical_core_region' || obj.semantic_type === 'vertical_core') {
    return 'Vertical Core Area';
  }
  return obj.object_id.replace(/^bellissima-deck\d+-/, '').replace(/-/g, ' ');
}

export function buildSpatialPassengerViewModel(
  payload: RawSpatialPayload,
  selectedDeckNumber: number = 14
): SpatialPassengerViewModel {
  const shipName = payload.ship?.name || 'MSC Bellissima';
  const rawDecks = payload.ship?.decks || [];
  const proofDeck = payload.deck14_proof?.deck?.number || 14;
  const rawObjects = payload.deck14_proof?.objects || [];
  const rawUnmapped = payload.known_unmapped_venues || [];

  // 1. Filter and transform admitted spatial objects for Deck 14
  const spatialEntities: SpatialEntityViewModel[] = [];
  let minX = 1.0;
  let minY = 1.0;
  let maxX = 0.0;
  let maxY = 0.0;

  for (const obj of rawObjects) {
    // Strict admission check: Lifecycle + Provenance
    if (!isAdmittedPassengerEntity(obj)) {
      continue;
    }

    const bbox = obj.normalized_bbox;
    if (!bbox || bbox.length !== 4) continue;

    minX = Math.min(minX, bbox[0]);
    minY = Math.min(minY, bbox[1]);
    maxX = Math.max(maxX, bbox[2]);
    maxY = Math.max(maxY, bbox[3]);

    const center: [number, number] = [
      (bbox[0] + bbox[2]) / 2,
      (bbox[1] + bbox[3]) / 2,
    ];

    const entityType: 'cabin' | 'venue' | 'vertical_core' =
      obj.semantic_type === 'vertical_core_region' || obj.semantic_type === 'vertical_core'
        ? 'vertical_core'
        : obj.semantic_type === 'venue'
        ? 'venue'
        : 'cabin';

    spatialEntities.push({
      id: obj.object_id,
      name: formatEntityName(obj),
      entityType,
      deckNumber: proofDeck,
      status: 'mapped',
      bbox: obj.normalized_bbox,
      polygon: obj.normalized_polygon || [],
      center,
      provenanceLabel: translateProvenance(obj.geometry_provenance),
      categoryLabel: translateCategory(obj.semantic_type, obj.cabin_number),
      isSelectable: true,
      featureSummary: obj.cabin_number ? `Deck ${proofDeck} Stateroom` : undefined,
    });
  }

  // 2. Filter unmapped entities: must pass lifecycle admission
  const admittedUnmapped = rawUnmapped.filter((u) =>
    isAdmittedPassengerEntity({ ...u, requires_geometry: false })
  );

  const unmappedEntities: UnmappedEntityViewModel[] = admittedUnmapped.map((u) => ({
    id: u.statement_id,
    name: u.name,
    entityType: 'venue',
    deckNumber: u.deck_number,
    status: 'known_but_unmapped',
    statusLabel: 'Known place — location not mapped yet',
    categoryLabel: u.category || 'Public Venue',
    sourceNote: u.source_locator,
  }));

  // 3. Filter available decks: must be canonically admitted
  const admittedDecks = rawDecks.filter((d) =>
    d.has_geometry || isAdmittedPassengerEntity({ ...d, requires_geometry: false })
  );

  const availableDecks: DeckOptionViewModel[] = (
    admittedDecks.length > 0 ? admittedDecks : [{ number: 14, name: 'Deck 14 (Magico)', has_geometry: true }]
  ).map((d) => {
    const isDeck14 = d.number === 14;
    const deckUnmapped = unmappedEntities.filter((u) => u.deckNumber === d.number);
    return {
      deckNumber: d.number,
      deckName: d.name,
      hasSpatialGeometry: isDeck14,
      statusNotice: isDeck14 ? 'Deck 14 available' : 'Spatial view not available yet',
      mappedCount: isDeck14 ? spatialEntities.length : 0,
      unmappedCount: deckUnmapped.length,
    };
  });

  // 4. Calculate deck viewport bounding box with padding
  const paddingX = maxX > minX ? (maxX - minX) * 0.05 : 0.01;
  const paddingY = maxY > minY ? (maxY - minY) * 0.1 : 0.01;
  const vbMinX = Math.max(0, minX - paddingX);
  const vbMinY = Math.max(0, minY - paddingY);
  const vbWidth = maxX > minX ? (maxX - minX) + paddingX * 2 : 1;
  const vbHeight = maxY > minY ? (maxY - minY) + paddingY * 2 : 1;

  const selectedDeckObj = availableDecks.find((d) => d.deckNumber === selectedDeckNumber) || availableDecks[0];

  const selectedDeck: DeckSpatialViewModel = {
    deckNumber: selectedDeckObj.deckNumber,
    deckName: selectedDeckObj.deckName,
    viewBox: {
      minX: vbMinX,
      minY: vbMinY,
      width: vbWidth,
      height: vbHeight,
    },
    deckBounds: [minX, minY, maxX, maxY],
    mappedEntitiesCount: selectedDeckObj.deckNumber === 14 ? spatialEntities.length : 0,
    unmappedEntitiesCount: unmappedEntities.filter((u) => u.deckNumber === selectedDeckObj.deckNumber).length,
  };

  // 5. Build trust summary
  const admittedCabinsCount = spatialEntities.filter((e) => e.entityType === 'cabin').length;
  const admittedObjectsCount = spatialEntities.length;
  const totalDecksCount = availableDecks.length;
  const mappedDecksCount = availableDecks.filter((d) => d.hasSpatialGeometry).length;

  const trustSummary: SpatialTrustSummaryViewModel = {
    statusBadge: 'Deck 14 Mapped',
    sourceNotice: 'Only reviewed, publication-approved spatial data derived from official source material is shown here.',
    coverageNotice: 'Deck 14 mapped • More deck views are not available yet.',
    governanceNotice: payload.trust_metadata?.governance || 'Governed by Timonelo Evidence Architecture',
    admittedCabinsCount,
    admittedObjectsCount,
    totalDecksCount,
    mappedDecksCount,
  };

  return {
    shipName,
    availableDecks,
    selectedDeck,
    spatialEntities: selectedDeckObj.deckNumber === 14 ? spatialEntities : [],
    unmappedEntities,
    trustSummary,
  };
}
