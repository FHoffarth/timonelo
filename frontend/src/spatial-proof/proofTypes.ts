/**
 * Types mirroring `timonelo.one-deck-geometry-proof.v1`.
 *
 * These describe the canonical Deck 14 geometry proof exactly as it is stored.
 * Nothing here is computed, widened or defaulted: if the artifact does not carry
 * a field, this file does not invent one.
 *
 * Coordinates are normalized fractions of the PDF page MediaBox. They are NOT
 * metres and carry no scale. See `REFERENCE_FRAME_STATEMENT`.
 */

export const PROOF_SCHEMA = "timonelo.one-deck-geometry-proof.v1";
export const PROOF_DECK_NUMBER = 14;

export type GeometryProvenance =
  | "DIRECT_SOURCE_GEOMETRY"
  | "TRANSFORMED_SOURCE_GEOMETRY"
  | "DERIVED_GEOMETRY"
  | "SYNTHETIC_GEOMETRY"
  | "UNKNOWN_PROVENANCE";

export type EvidenceCondition = "SUPPORTED" | "UNSUPPORTED" | "CONFLICTED" | "UNKNOWN";
export type HumanReviewState =
  | "DRAFT"
  | "UNDER_REVIEW"
  | "APPROVED"
  | "REJECTED"
  | "SUPERSEDED";
export type PublishStatus =
  | "PUBLISH_ALLOWED"
  | "PUBLISH_ALLOWED_WITH_WARNINGS"
  | "PUBLISH_BLOCKED";

/** [x0, y0, x1, y1] */
export type BBox = [number, number, number, number];
/** [x, y] pairs in normalized page fractions. */
export type Polygon = Array<[number, number]>;

export interface ProofObject {
  object_id: string;
  semantic_type: string;
  cabin_number?: string;
  source_text_bbox: BBox;
  source_bbox: BBox;
  normalized_bbox: BBox;
  normalized_polygon: Polygon;
  source_references: string[];
  transform_id: string;
  geometry_provenance: GeometryProvenance;
  semantic_association_method: string;
  association_staging_note?: string;
  derivation?: string;
  evidence_condition: EvidenceCondition;
  human_review_state: HumanReviewState;
  publish_status: PublishStatus;
}

export interface ProofSource {
  artifact_id: string;
  artifact_sha256: string;
  physical_pdf_path: string;
  pdf_page_number: number;
  visible_deck_number: number;
  visible_deck_name: string;
  page_dimensions_points: [number, number];
  source_coordinate_system: string;
  extraction_tool: string;
}

export interface ProofTransform {
  transform_id: string;
  frame_type: string;
  target_units: string;
  formula: string;
  semantic: boolean;
}

/** Recorded refusal. `accepted_geometry: false` means there is nothing to draw. */
export interface Observation {
  classification?: string | null;
  accepted_geometry: boolean;
  geometry: unknown | null;
  reason?: string;
}

export interface ProofDocument {
  schema: string;
  source: ProofSource;
  deck: { number: number; name: string };
  transform: ProofTransform;
  /** Hand-picked crop, DISPLAY_ONLY. Never a canonical render frame. */
  review_viewport: { bbox: BBox; classification: string; semantic: boolean };
  objects: ProofObject[];
  corridor_observation: Observation;
  venue_observation: Observation;
  /** Null means no connectivity is evidenced. There is no graph to route over. */
  navigation_graph: unknown | null;
  nearest_core_calculation: unknown | null;
  cross_deck_relationships: unknown[];
  above_below_relations: unknown[];
  port_starboard_associations: unknown[];
}

/**
 * Shown persistently in the viewer. The proof establishes position within a page
 * frame, not distance in the world, and the UI must never let the two be confused.
 */
export const REFERENCE_FRAME_STATEMENT =
  "Coordinates are normalized fractions of the PDF page MediaBox " +
  "(589.606 x 807.874 pt). Not metres. No scale has been established.";

export const isCabin = (o: ProofObject): boolean => o.semantic_type === "cabin";

/** Geometry styling is driven by provenance ONLY, never by publish status. */
export const provenanceClass = (o: ProofObject): "transformed" | "derived" | "other" =>
  o.geometry_provenance === "TRANSFORMED_SOURCE_GEOMETRY"
    ? "transformed"
    : o.geometry_provenance === "DERIVED_GEOMETRY"
      ? "derived"
      : "other";
