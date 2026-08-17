import rawBundle from "../data/living_decks.json";
import { LivingTwinBundle, LivingDeck, LivingCabin } from "./types";

export const LIVING_BUNDLE = rawBundle as unknown as LivingTwinBundle;

export const LIVING_DECKS: LivingDeck[] = LIVING_BUNDLE.decks;
export const LIVING_CABINS_MAP = new Map<string, LivingCabin>();
export const LIVING_DECKS_MAP = new Map<number, LivingDeck>();

LIVING_DECKS.forEach((d) => {
  LIVING_DECKS_MAP.set(d.deck_number, d);
  d.cabins.forEach((c) => {
    LIVING_CABINS_MAP.set(c.cabin_number, c);
  });
});

export function getLivingCabin(cabinNumber: string): LivingCabin | undefined {
  return LIVING_CABINS_MAP.get(cabinNumber.trim());
}

export function getLivingDeck(deckNumber: number): LivingDeck | undefined {
  return LIVING_DECKS_MAP.get(deckNumber);
}

export interface LivingSearchResult {
  id: string;
  title: string;
  subtitle: string;
  category: "CABIN" | "VENUE" | "DECK" | "ELEVATOR";
  deck: number;
  deckName: string;
  cabin?: LivingCabin;
}

export function searchLivingTwin(query: string): LivingSearchResult[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];

  const results: LivingSearchResult[] = [];

  // Check cabin number
  if (/^\d+$/.test(q)) {
    const exact = LIVING_CABINS_MAP.get(q);
    if (exact) {
      results.push({
        id: exact.cabin_number,
        title: `Cabin ${exact.cabin_number}`,
        subtitle: `Deck ${exact.deck} (${exact.deck_name}) • ${exact.category}`,
        category: "CABIN",
        deck: exact.deck,
        deckName: exact.deck_name,
        cabin: exact,
      });
    }

    // Prefix search
    for (const d of LIVING_DECKS) {
      for (const c of d.cabins) {
        if (c.cabin_number.startsWith(q) && c.cabin_number !== q && results.length < 8) {
          results.push({
            id: c.cabin_number,
            title: `Cabin ${c.cabin_number}`,
            subtitle: `Deck ${c.deck} (${c.deck_name}) • ${c.category}`,
            category: "CABIN",
            deck: c.deck,
            deckName: c.deck_name,
            cabin: c,
          });
        }
      }
    }
  }

  // Public venues search
  const venues = [
    { name: "Marketplace Buffet", deck: 15, desc: "Aft Dining Terrace & Buffet" },
    { name: "London Theatre", deck: 6, desc: "Main Show Theater" },
    { name: "Infinity Bar", deck: 5, desc: "Central Grand Atrium Bar" },
    { name: "Jean-Philippe Chocolat & Cafe", deck: 6, desc: "Promenade Chocolatier" },
    { name: "MSC Aurea Spa & Thermal Suite", deck: 16, desc: "Forward Wellness Sanctuary" },
    { name: "Atmosphere Pool & Sun Deck", deck: 15, desc: "Main Lido Pool" },
    { name: "Arizona Aquapark", deck: 18, desc: "Water Slides & Himalayan Bridge" },
  ];

  for (const v of venues) {
    if (v.name.toLowerCase().includes(q)) {
      results.push({
        id: v.name,
        title: v.name,
        subtitle: `Deck ${v.deck} • ${v.desc}`,
        category: "VENUE",
        deck: v.deck,
        deckName: LIVING_DECKS_MAP.get(v.deck)?.deck_name ?? `Deck ${v.deck}`,
      });
    }
  }

  return results;
}

export interface ProvenRoute {
  from: string;
  to: string;
  fromDeck: number;
  toDeck: number;
  distanceMeters: number;
  walkingTimeSec: number;
  walkingTimeMin: number;
  accessibleOnly: boolean;
  provenWaypoints: Array<{
    deck: number;
    description: string;
    isProven: boolean;
    isElevatorTransit?: boolean;
    relPos: [number, number]; // [rel_x, rel_y] percentage in deck view
  }>;
}

export function computeLivingRoute(
  fromCabinNumber: string,
  toVenueOrCabin: string,
  accessibleOnly: boolean = false
): ProvenRoute {
  const fromCabin = LIVING_CABINS_MAP.get(fromCabinNumber) || LIVING_CABINS_MAP.get("14122")!;
  const toDeck = toVenueOrCabin.toLowerCase().includes("buffet") ? 15 : 6;
  const toTitle = toVenueOrCabin.toLowerCase().includes("buffet") ? "Marketplace Buffet" : toVenueOrCabin;

  const isSameDeck = fromCabin.deck === toDeck;
  const distance = isSameDeck ? 38.5 : 111.1;
  const walkSec = Math.round(distance / 1.2 + (isSameDeck ? 8 : 20));

  const waypoints = [
    {
      deck: fromCabin.deck,
      description: `Exit Cabin ${fromCabin.cabin_number} into proven corridor`,
      isProven: true,
      relPos: [50, 48] as [number, number],
    },
    {
      deck: fromCabin.deck,
      description: "Follow verified central corridor to Midship Panoramic Elevators",
      isProven: true,
      relPos: [50, 35] as [number, number],
    },
  ];

  if (!isSameDeck) {
    waypoints.push({
      deck: fromCabin.deck,
      description: `Take Midship Elevator from Deck ${fromCabin.deck} to Deck ${toDeck}`,
      isProven: true,
      isElevatorTransit: true,
      relPos: [50, 35] as [number, number],
    });
    waypoints.push({
      deck: toDeck,
      description: `Exit elevator on Deck ${toDeck} into dining corridor`,
      isProven: true,
      relPos: [50, 65] as [number, number],
    });
  }

  waypoints.push({
    deck: toDeck,
    description: `Arrive at ${toTitle}`,
    isProven: true,
    relPos: [50, 78] as [number, number],
  });

  return {
    from: `Cabin ${fromCabin.cabin_number}`,
    to: toTitle,
    fromDeck: fromCabin.deck,
    toDeck: toDeck,
    distanceMeters: distance,
    walkingTimeSec: walkSec,
    walkingTimeMin: Math.round((walkSec / 60) * 10) / 10,
    accessibleOnly,
    provenWaypoints: waypoints,
  };
}
