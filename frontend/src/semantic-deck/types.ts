export type EpistemicState = "DIRECT" | "DERIVED" | "UNKNOWN" | "CONFLICT";

export type SemanticCategory = "INTERIOR" | "OCEAN_VIEW" | "BALCONY" | "SUITE" | "VENUE" | "FACILITY";

export type HullSide = "PORT" | "STARBOARD" | "CENTER";

export interface EvidenceReference {
  artifact_id: string;
  page?: number;
  locator_type?: string;
  locator: string;
  digest?: string;
}

export interface UnknownRelation {
  field: string;
  reason: string;
  required_document: string;
}

export interface KnownRelations {
  neighbor_fore?: string | null;
  neighbor_aft?: string | null;
  across_corridor?: string | null;
  overhead?: string | null;
  underfoot?: string | null;
  nearest_elevator?: string | null;
  nearest_emergency_station?: string | null;
  [key: string]: string | null | undefined;
}

export interface SemanticObject {
  id: string;
  type: "STATEROOM" | "VENUE" | "FACILITY" | "NODE";
  label: string;
  category: SemanticCategory;
  category_label: string;
  deck: number;
  side: HullSide;
  zone: string;
  sequence_index: number;
  accessible: boolean;
  connecting: boolean;
  balcony: boolean;
  epistemic_state: EpistemicState;
  review_state: string;
  confidence: number;
  statements: string[];
  evidence_links: EvidenceReference[];
  known_relations: KnownRelations;
  unknown_relations: UnknownRelation[];
}

export interface SemanticCorridor {
  corridor_id: string;
  side: HullSide;
  label: string;
}

export interface SemanticDeck {
  deck_level: number;
  deck_name: string;
  corridors: SemanticCorridor[];
  objects: SemanticObject[];
}

export interface VesselEpistemicSummary {
  total_objects: number;
  direct_count: number;
  derived_count: number;
  unknown_count: number;
  conflict_count: number;
  confidence_avg: number;
}

export interface VesselSemanticModel {
  vessel_id: string;
  vessel_name: string;
  operator: string;
  class_name: string;
  epistemic_summary: VesselEpistemicSummary;
  decks: SemanticDeck[];
}
