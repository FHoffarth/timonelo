/**
 * Timonelo Canonical Semantic Spatial Contract
 * 
 * Aligned with international spatial & semantic standards:
 * - W3C BOT (Building Topology Ontology)
 * - W3C PROV-O (Provenance Ontology)
 * - OGC IndoorGML (Indoor Spatial Data Model)
 * - JSON-LD (Linked Data Representation)
 */

// Canonical Epistemic Enums re-exported from Python canon generator
export type {
  Method,
  Derivation,
  EvidenceCondition,
  HumanReviewState,
  PublishStatus,
  GeometryProvenance,
} from "../generated/canon";

/**
 * Non-canonical legacy display state for prototype 2D viewport fixtures.
 * NOT for canonical epistemic ground truth. Governed by ADR-0002.
 */
export type LegacySemanticDeckState = "DIRECT" | "DERIVED" | "UNKNOWN" | "CONFLICT";

/** @deprecated Use LegacySemanticDeckState for legacy fixtures or canonical types from generated/canon */
export type EpistemicState = LegacySemanticDeckState;

export type SpatialClassification =
  | "STATEROOM_INTERIOR"
  | "STATEROOM_OCEAN_VIEW"
  | "STATEROOM_BALCONY"
  | "STATEROOM_SUITE"
  | "PUBLIC_DINING"
  | "PUBLIC_LOUNGE"
  | "PUBLIC_WELLNESS"
  | "PUBLIC_ENTERTAINMENT"
  | "CIRCULATION_CORRIDOR"
  | "CIRCULATION_VERTICAL_CORE"
  | "SERVICE_FACILITY";

export type SpatialSide = "PORT" | "STARBOARD" | "CENTER";

export interface EvidenceReference {
  artifact_id: string;
  source_title: string;
  digest: string | null;
  locator: string;
  page?: number;
}

export interface UnknownField {
  field_name: string;
  epistemic_reason: string;
  required_artifact_class: string;
}

export interface SpatialRelations {
  adjacent_fore?: string | null;
  adjacent_aft?: string | null;
  adjacent_across?: string | null;
  adjacent_overhead?: string | null;
  adjacent_underfoot?: string | null;
  connected_vertical_core?: string | null;
  nearest_assembly_station?: string | null;
  [key: string]: string | null | undefined;
}

export interface SemanticEntity {
  id: string;
  iri: string; // W3C Linked Data IRI (e.g., timonelo:vessel/bel/space/14122)
  label: string;
  classification: SpatialClassification;
  classification_label: string;
  level: number;
  level_name: string;
  side: SpatialSide;
  zone: string;
  sequence_order: number;
  accessible: boolean;
  connecting: boolean;
  has_balcony: boolean;
  
  // Epistemic Ground Truth
  epistemic_state: EpistemicState;
  review_state: string;
  confidence: number;
  statement_count: number;
  statements: string[];
  artifact_count: number;
  evidence_links: EvidenceReference[];
  
  // Topology & Adjacency
  relations: SpatialRelations;
  unknown_fields: UnknownField[];
}

export interface SemanticLevel {
  level_index: number;
  level_name: string;
  spaces_count: number;
  spaces: SemanticEntity[];
  epistemic_breakdown: {
    direct: number;
    derived: number;
    unknown: number;
    conflict: number;
  };
}

export interface VesselKnowledgeGraph {
  vessel_id: string;
  vessel_name: string;
  operator: string;
  vessel_class: string;
  canonical_model_version: string;
  epistemic_summary: {
    total_entities: number;
    direct_evidence_count: number;
    derived_count: number;
    unknown_count: number;
    conflict_count: number;
    mean_confidence: number;
  };
  levels: SemanticLevel[];
}

// Standards Export Formats
export interface StandardsExportPayload {
  entity_id: string;
  json_ld: Record<string, unknown>;
  bot_turtle: string;
  prov_o_turtle: string;
  indoor_gml_xml: string;
}
