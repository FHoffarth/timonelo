export interface LivingCabin {
  cabin_number: string;
  deck: number;
  deck_name: string;
  pdf_bbox: [number, number, number, number]; // [x0, y0, x1, y1] in PDF points
  rel_bbox: [number, number, number, number]; // [x, y, w, h] relative to deck slice
  center_x: number;
  center_y: number;
  category: string;
  accessible: boolean;
  connecting: boolean;
  balcony: boolean;
  evidence_artifact: string;
  page: number;
  locator: string;
  statement_id: string;
  confidence: number;
  epistemic_method: "DIRECT_EVIDENTIARY" | "DERIVED_DETERMINISTIC" | "UNKNOWN";
  review_state: string;
  neighbor_left?: string | null;
  neighbor_right?: string | null;
  neighbor_across?: string | null;
  cabin_above?: string | null;
  cabin_below?: string | null;
}

export interface LivingDeck {
  deck_number: number;
  deck_name: string;
  bounds: {
    x_min: number;
    x_max: number;
    y_min: number;
    y_max: number;
  };
  clip_rect: [number, number, number, number];
  width_pt: number;
  height_pt: number;
  cabins_count: number;
  cabins: LivingCabin[];
  public_areas: Array<{
    name: string;
    deck: number;
    bbox: number[];
    evidence: string;
  }>;
  elevators: Array<{
    id: string;
    deck: number;
    center: [number, number];
    bbox: number[];
    evidence: string;
  }>;
}

export interface LivingTwinBundle {
  ship_name: string;
  source_document: string;
  sha256: string;
  pdf_page_width_pt: number;
  pdf_page_height_pt: number;
  total_cabins: number;
  decks: LivingDeck[];
}

export type LivingViewMode = "single_deck" | "exploded_stack" | "evidence_split";
