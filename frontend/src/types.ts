export interface PowerSockets {
  eu_count: number;
  us_count: number;
  usb_a_count: number;
  usb_c_count: number;
  bedside_usb: boolean;
}

export interface LayerSurrounding {
  deck_number: number | null;
  deck_name: string | null;
  venues: string[];
  is_residential: boolean;
  is_noise_generator?: boolean;
}

export interface CabinSurroundings {
  overhead: LayerSurrounding;
  underfoot: LayerSurrounding;
  adjacent_connecting: string | null;
}

export interface Sightlines {
  horizon_angle_deg: number;
  downward_angle_deg: number;
  has_lifeboat_obstruction: boolean;
  description: string;
}

export interface DistanceMetric {
  meters: number;
  seconds: number;
  steps: number;
  step_free: boolean;
}

export interface CabinLenses {
  accessibility: {
    is_certified: boolean;
    summary: string;
    lift_distance_m: number;
  };
  family: {
    is_optimized: boolean;
    has_connecting: boolean;
    connecting_cabin: string | null;
    kids_club_distance_m: number;
    summary: string;
  };
  quiet: {
    is_quiet_tier: boolean;
    acoustic_flags: string[];
    summary: string;
  };
}

export interface EvidenceRecord {
  source_id: string;
  sha256: string;
  locator: string;
}

export interface CabinData {
  cabin_number: string;
  deck_number: number;
  deck_name: string;
  hull_side: "PORT" | "STARBOARD" | "CENTERLINE";
  zone: string;
  category_code: string;
  square_meters: number;
  balcony_type: string;
  connecting_cabin_number: string | null;
  bed_near_balcony: boolean | null;
  is_accessible: boolean;
  door_width_mm: number;
  sockets: PowerSockets;
  surroundings: CabinSurroundings;
  sightlines: Sightlines;
  distances: Record<string, DistanceMetric>;
  lenses: CabinLenses;
  evidence: EvidenceRecord[];
}

export interface ShipData {
  imo: string;
  name: string;
  ship_class: string;
  length_m: number;
  beam_m: number;
  total_decks: number;
  decks: Record<string, { deck_number: number; name: string; elevation_m: number; zone: string; venues: { id: string; name: string; category: string; is_noise_generator: boolean }[] }>;
  cabins: Record<string, CabinData>;
}
