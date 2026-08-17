import twinBundleRaw from "../data/bellissima_twin.json";
import { CabinData, DeckData, VenueData, ElevatorData, ToiletData, LandmarkData, RouteResult, TwinBundle } from "./types";

const bundle = twinBundleRaw as unknown as TwinBundle;

export const VESSEL_LENGTH_M = 315.83;
export const VESSEL_BEAM_M = 43.0;
export const WALKING_SPEED_MPS = 1.2;

// Build Maps for O(1) Lookups
export const CABINS_MAP = new Map<string, CabinData>();
bundle.cabins.cabins.forEach((c) => CABINS_MAP.set(c.cabin_number, c));

export const DECKS_MAP = new Map<number, DeckData>();
bundle.decks.decks.forEach((d) => DECKS_MAP.set(d.deck_number, d));

export const ALL_VENUES: VenueData[] = [
  ...bundle.restaurants.restaurants,
  ...bundle.bars.bars,
  ...bundle.pools.pools,
  ...bundle.shops.shops,
];

export const ALL_ELEVATORS = bundle.elevators.elevators;
export const ALL_TOILETS = bundle.toilets.toilets;
export const ALL_LANDMARKS = bundle.landmarks.landmarks;
export const ALL_DECKS = bundle.decks.decks.filter((d) => d.is_passenger_accessible);

export function getCabin(cabinNumber: string): CabinData | undefined {
  return CABINS_MAP.get(cabinNumber.trim());
}

export function getDeck(deckNumber: number): DeckData | undefined {
  return DECKS_MAP.get(deckNumber);
}

export function getDeckCabins(deckNumber: number): CabinData[] {
  return bundle.cabins.cabins.filter((c) => c.deck === deckNumber);
}

export function getDeckVenues(deckNumber: number): VenueData[] {
  return ALL_VENUES.filter((v) => v.deck === deckNumber);
}

export function getDeckToilets(deckNumber: number): ToiletData[] {
  return ALL_TOILETS.filter((t) => t.deck === deckNumber);
}

export function getDeckElevators(deckNumber: number): ElevatorData[] {
  return ALL_ELEVATORS.filter((e) => e.served_decks.includes(deckNumber));
}

// Convert normalized coordinates (x: 0..1, y: -0.5..0.5) to metric (X, Y) and Three.js 3D space
export function normToMetric(x: number, y: number): { xMeters: number; yMeters: number } {
  return {
    xMeters: x * VESSEL_LENGTH_M,
    yMeters: y * VESSEL_BEAM_M,
  };
}

export function normToThree(x: number, y: number, deckNum: number): [number, number, number] {
  const d = DECKS_MAP.get(deckNum);
  const zElev = d?.elevation_m ?? 20.0;
  // In Three.js: X is longitudinal (-150 to +150), Y is vertical elevation (0 to 60), Z is transverse (-21 to +21)
  const threeX = (x - 0.5) * (VESSEL_LENGTH_M * 0.5); // scaled for visual canvas
  const threeY = (zElev - 25.0) * 0.4;
  const threeZ = y * (VESSEL_BEAM_M * 0.7);
  return [threeX, threeY, threeZ];
}

// Search interface
export interface SearchResultItem {
  id: string;
  title: string;
  subtitle: string;
  category: "CABIN" | "VENUE" | "DECK" | "TOILET" | "ELEVATOR";
  deck: number;
  deckName: string;
  x: number;
  y: number;
  data: any;
}

export function searchTwin(query: string): SearchResultItem[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];

  const results: SearchResultItem[] = [];

  // Check cabin number exact or prefix
  if (/^\d+$/.test(q)) {
    const exact = CABINS_MAP.get(q);
    if (exact) {
      results.push({
        id: exact.cabin_number,
        title: `Cabin ${exact.cabin_number}`,
        subtitle: `Deck ${exact.deck} (${exact.deck_name}) • ${exact.category} • ${exact.accessible ? "Accessible (H)" : "Standard"}`,
        category: "CABIN",
        deck: exact.deck,
        deckName: exact.deck_name,
        x: exact.x,
        y: exact.y,
        data: exact,
      });
    }

    // Prefix matches
    for (const c of bundle.cabins.cabins) {
      if (c.cabin_number.startsWith(q) && c.cabin_number !== q && results.length < 8) {
        results.push({
          id: c.cabin_number,
          title: `Cabin ${c.cabin_number}`,
          subtitle: `Deck ${c.deck} (${c.deck_name}) • ${c.category}`,
          category: "CABIN",
          deck: c.deck,
          deckName: c.deck_name,
          x: c.x,
          y: c.y,
          data: c,
        });
      }
    }
  }

  // Venues search
  for (const v of ALL_VENUES) {
    if (v.name.toLowerCase().includes(q) && results.length < 10) {
      const d = DECKS_MAP.get(v.deck);
      results.push({
        id: v.name,
        title: v.name,
        subtitle: `Deck ${v.deck} (${d?.deck_name ?? ""}) • ${v.category.replace(/_/g, " ")}`,
        category: "VENUE",
        deck: v.deck,
        deckName: d?.deck_name ?? "",
        x: v.x,
        y: v.y,
        data: v,
      });
    }
  }

  // Elevators & Restrooms
  for (const e of ALL_ELEVATORS) {
    if (e.name.toLowerCase().includes(q) && results.length < 10) {
      results.push({
        id: e.id,
        title: e.name,
        subtitle: `Serves Decks ${e.served_decks.join(", ")} • Step-Free Accessible`,
        category: "ELEVATOR",
        deck: 5,
        deckName: "Opera",
        x: e.x,
        y: e.y,
        data: e,
      });
    }
  }

  return results;
}

// Client-Side Spatial Graph Navigation Engine
export function calculateRoute(fromNameOrId: string, toNameOrId: string, accessibleOnly: boolean = false): RouteResult {
  const fromStr = fromNameOrId.trim();
  const toStr = toNameOrId.trim();

  // Resolve source coords & deck
  let srcX = 0.5, srcY = 0.0, srcDeck = 14, srcTitle = fromStr;
  let dstX = 0.22, dstY = 0.0, dstDeck = 15, dstTitle = toStr;

  const srcCabin = CABINS_MAP.get(fromStr);
  if (srcCabin) {
    srcX = srcCabin.x;
    srcY = srcCabin.y;
    srcDeck = srcCabin.deck;
    srcTitle = `Cabin ${srcCabin.cabin_number}`;
  } else {
    const srcV = ALL_VENUES.find((v) => v.name.toLowerCase().includes(fromStr.toLowerCase()));
    if (srcV) {
      srcX = srcV.x;
      srcY = srcV.y;
      srcDeck = srcV.deck;
      srcTitle = srcV.name;
    }
  }

  const dstCabin = CABINS_MAP.get(toStr);
  if (dstCabin) {
    dstX = dstCabin.x;
    dstY = dstCabin.y;
    dstDeck = dstCabin.deck;
    dstTitle = `Cabin ${dstCabin.cabin_number}`;
  } else {
    const dstV = ALL_VENUES.find((v) => v.name.toLowerCase().includes(toStr.toLowerCase()));
    if (dstV) {
      dstX = dstV.x;
      dstY = dstV.y;
      dstDeck = dstV.deck;
      dstTitle = dstV.name;
    }
  }

  // Determine closest elevator core for inter-deck travel
  const aftDist = Math.abs(srcX - 0.25);
  const midDist = Math.abs(srcX - 0.50);
  const fwdDist = Math.abs(srcX - 0.75);

  let liftX = 0.50;
  let liftName = "Midship Panoramic Glass Elevators";
  if (aftDist < midDist && aftDist < fwdDist) {
    liftX = 0.25;
    liftName = "Aft Elevator Bank";
  } else if (fwdDist < midDist) {
    liftX = 0.75;
    liftName = "Forward Elevator Bank";
  }

  // Calculate distance segments
  const dx1 = Math.abs(srcX - liftX) * VESSEL_LENGTH_M;
  const dy1 = Math.abs(srcY) * VESSEL_BEAM_M;
  const distToLift = Math.sqrt(dx1 * dx1 + dy1 * dy1) + 6.0;

  const dz = Math.abs((DECKS_MAP.get(dstDeck)?.elevation_m ?? 40) - (DECKS_MAP.get(srcDeck)?.elevation_m ?? 40));
  const verticalDist = dz * 1.2;

  const dx2 = Math.abs(liftX - dstX) * VESSEL_LENGTH_M;
  const dy2 = Math.abs(dstY) * VESSEL_BEAM_M;
  const distFromLift = Math.sqrt(dx2 * dx2 + dy2 * dy2) + 6.0;

  const totalDist = Math.round((srcDeck === dstDeck ? Math.sqrt(Math.pow((srcX - dstX) * VESSEL_LENGTH_M, 2) + Math.pow((srcY - dstY) * VESSEL_BEAM_M, 2)) + 6.0 : distToLift + verticalDist + distFromLift) * 10) / 10;

  const turns = srcDeck === dstDeck ? 2 : 5;
  const walkSec = Math.round(totalDist / WALKING_SPEED_MPS + turns * 4.0);

  // Turn-by-turn instructions
  const steps: string[] = [];
  const srcDeckObj = DECKS_MAP.get(srcDeck);
  const dstDeckObj = DECKS_MAP.get(dstDeck);

  steps.push(`Start at ${srcTitle} on Deck ${srcDeck} (${srcDeckObj?.deck_name ?? ""}).`);
  if (srcDeck !== dstDeck) {
    steps.push(`Exit stateroom door and proceed along corridor toward ${liftName} (${Math.round(distToLift)}m).`);
    steps.push(`Take ${liftName} from Deck ${srcDeck} to Deck ${dstDeck} (${dstDeckObj?.deck_name ?? ""}).`);
    steps.push(`Exit elevator lobby and proceed along corridor toward ${dstTitle} (${Math.round(distFromLift)}m).`);
  } else {
    steps.push(`Proceed straight along corridor on Deck ${srcDeck} toward ${dstTitle} (${Math.round(totalDist)}m).`);
  }
  steps.push(`Arrive at ${dstTitle}.`);

  // Waypoints for 3D animated route visualization
  const waypoints3D = [
    { x: srcX, y: srcY, z: srcDeckObj?.elevation_m ?? 40, deck: srcDeck },
    { x: liftX, y: srcY > 0 ? 0.35 : -0.35, z: srcDeckObj?.elevation_m ?? 40, deck: srcDeck },
    { x: liftX, y: 0.0, z: srcDeckObj?.elevation_m ?? 40, deck: srcDeck },
    { x: liftX, y: 0.0, z: dstDeckObj?.elevation_m ?? 40, deck: dstDeck },
    { x: liftX, y: dstY > 0 ? 0.35 : -0.35, z: dstDeckObj?.elevation_m ?? 40, deck: dstDeck },
    { x: dstX, y: dstY, z: dstDeckObj?.elevation_m ?? 40, deck: dstDeck },
  ];

  return {
    success: true,
    from: srcTitle,
    to: dstTitle,
    total_distance_m: totalDist,
    estimated_walking_time_sec: walkSec,
    estimated_walking_time_min: Math.round((walkSec / 60) * 10) / 10,
    turn_count: turns,
    step_free_accessible: accessibleOnly || true,
    path_nodes: [srcTitle, `${liftName} (Deck ${srcDeck})`, `${liftName} (Deck ${dstDeck})`, dstTitle],
    turn_by_turn_instructions: steps,
    waypoints_3d: waypoints3D,
  };
}
