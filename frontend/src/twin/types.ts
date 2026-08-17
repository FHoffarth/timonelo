export interface CabinData {
  cabin_number: string;
  deck: number;
  deck_name: string;
  elevation_m: number;
  hull_side: "STARBOARD" | "PORT" | "CENTER";
  zone: "AFT" | "MID" | "FORWARD";
  category: string;
  accessible: boolean;
  connecting_cabin: boolean;
  balcony: boolean;
  additional_beds: string;
  x: number; // 0.0 - 1.0 longitudinal
  y: number; // -0.5 - 0.5 transverse
  door_x?: number;
  door_y?: number;
  corridor_snap_node: string;
  nearest_elevator: {
    id: string;
    name: string;
    walking_distance_m: number;
  };
  nearest_muster_station: string;
  evidence_artifact: string;
  page: number;
  locator: string;
  pdf_bbox: [number, number, number, number];
  review_state: string;
  notes?: string;
  neighbor_left?: string | null;
  neighbor_right?: string | null;
  neighbor_across?: string | null;
  cabin_above?: string | null;
  cabin_below?: string | null;
}

export interface DeckData {
  deck_number: number;
  deck_name: string;
  elevation_m: number | null;
  is_passenger_accessible: boolean;
  cabins: number;
  venues: string[];
  zone?: string;
  evidence?: string;
}

export interface VenueData {
  name: string;
  deck: number;
  deck_name?: string;
  category: string;
  capacity?: number;
  x: number;
  y: number;
  nearest_venue?: string;
}

export interface ElevatorData {
  id: string;
  name: string;
  served_decks: number[];
  x: number;
  y: number;
  capacity_persons: number;
  speed_mps: number;
  accessible: boolean;
  vertical_core_id: string;
  evidence: string;
}

export interface ToiletData {
  id: string;
  deck: number;
  deck_name: string;
  name: string;
  x: number;
  y: number;
  gender: string;
  accessible: boolean;
  family: boolean;
  nearest_venue: string;
}

export interface LandmarkData {
  id: string;
  name: string;
  deck: number;
  x: number;
  y: number;
  visibility_range_m: number;
}

export interface ZoneData {
  id: string;
  name: string;
  decks: number[];
  type: string;
  is_lively: boolean;
}

export interface RouteResult {
  success: boolean;
  from: string;
  to: string;
  total_distance_m: number;
  estimated_walking_time_sec: number;
  estimated_walking_time_min: number;
  turn_count: number;
  step_free_accessible: boolean;
  path_nodes: string[];
  turn_by_turn_instructions: string[];
  waypoints_3d?: Array<{ x: number; y: number; z: number; deck: number }>;
  error?: string;
}

export interface TwinBundle {
  ship: {
    vessel: {
      name: string;
      imo: number;
      flag: string;
      gross_tonnage: number;
      length_overall_m: number;
      beam_m: number;
      max_passenger_capacity: number;
      staterooms_count: number;
    };
  };
  decks: { decks: DeckData[] };
  cabins: { cabins: CabinData[] };
  venues: { venues: any[] };
  restaurants: { restaurants: VenueData[] };
  bars: { bars: VenueData[] };
  pools: { pools: VenueData[] };
  shops: { shops: VenueData[] };
  elevators: { elevators: ElevatorData[] };
  toilets: { toilets: ToiletData[] };
  landmarks: { landmarks: LandmarkData[] };
  zones: { zones: ZoneData[] };
}

export type ViewMode = "3d_exterior" | "deck_topdown" | "split_evidence" | "cinematic";

export interface ActiveLayers {
  cabins: boolean;
  restaurants: boolean;
  bars: boolean;
  pools: boolean;
  shops: boolean;
  toilets: boolean;
  elevators: boolean;
  stairs: boolean;
  accessible: boolean;
  routingGraph: boolean;
  landmarks: boolean;
  zones: boolean;
  heatmap: boolean;
}
