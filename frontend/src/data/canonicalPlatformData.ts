import { ShipProfile, CabinAnalysis } from "../types";
import { knowledgeRepository } from "../knowledge";

const bellissimaSpecs = knowledgeRepository.getShip("msc-bellissima");

export const CANONICAL_SHIPS: Record<string, ShipProfile> = {
  "msc-virtuosa": {
    slug: "msc-virtuosa",
    name: "MSC Virtuosa",
    className: "Meraviglia-Plus Class",
    operator: "MSC Cruises",
    builtYear: 2021,
    grossTonnage: 181541,
    lengthFt: 1036,
    guestCapacity: 6334,
    deckCount: 19,
    heroImageUrl: "https://images.unsplash.com/photo-1548574505-5e239809ee19?auto=format&fit=crop&w=1600&q=80",
    description:
      "Launched in 2021, MSC Virtuosa stands as one of the largest and most advanced ships in the MSC fleet. Highly distinguished by its indoor promenade topped with a massive 262-foot LED dome ceiling, it offers travelers high-energy entertainment alongside quieter, acoustically sound retreat spaces when navigated correctly.",
    keyFacts: {
      elevators: "16 passenger elevators across 2 main vertical cores (Core A Forward, Core B Aft) plus 2 panoramic glass elevators at midship overlooking the central Galleria.",
      transitZones: "High-traffic zones concentrated along Deck 6 and Deck 7 Promenade; residential quiet zones span Decks 8 through 14.",
      atriumFeatures: "3-deck high Swarovski crystal staircase at midship atrium; 80m LED sky dome projection visual ceiling.",
      stabilizers: "State-of-the-art hydrodynamic fin stabilizers minimizing roll during open sea transits.",
    },
  },
  "msc-bellissima": {
    slug: bellissimaSpecs.vessel_id,
    name: bellissimaSpecs.vessel_name,
    className: bellissimaSpecs.technical_specifications.class,
    operator: "MSC Cruises",
    builtYear: parseInt(bellissimaSpecs.technical_specifications.key_milestones.maiden_voyage),
    grossTonnage: bellissimaSpecs.technical_specifications.tonnage_gt,
    lengthFt: bellissimaSpecs.technical_specifications.dimensions.length_feet,
    guestCapacity: bellissimaSpecs.technical_specifications.capacities.passenger_capacity_max_occupancy,
    deckCount: bellissimaSpecs.technical_specifications.capacities.total_decks,
    heroImageUrl: "https://images.unsplash.com/photo-1599640842225-85d111c60e6b?auto=format&fit=crop&w=1600&q=80",
    description:
      "MSC Bellissima offers a stunning array of features to rival its sister ship, starting with the iconic 96-meter central Mediterranean promenade with an 80-meter LED sky screen, 12 distinct dining venues, and 20 bars.",
    keyFacts: {
      elevators: "14 passenger elevators connecting Decks 4 through 19 with dual panoramic atrium lifts.",
      transitZones: "Deck 6/7 Galleria entertainment spine; Decks 8-14 serene stateroom corridors.",
      atriumFeatures: "Infinity Atrium with Swarovski crystal staircases and 2-deck panoramic glass wall.",
      stabilizers: "Active fin stabilization with dynamic pitch compensation.",
    },
  },
};

export const CANONICAL_CABINS: Record<string, CabinAnalysis> = {
  "12142": {
    id: "12142",
    shipSlug: "msc-virtuosa",
    deckNumber: 12,
    deckName: "Grandiosa",
    category: "Deluxe Balcony",
    tier: "Fantastica Tier",
    side: "PORT",
    zone: "MIDSHIP",
    sqmInterior: 17,
    sqmBalcony: 4,
    bedConfig: "Twin beds convertible to double (king size)",
    connectingCabinId: "12140",
    accessible: false,
    heroImageUrl: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1600&q=80",
    locationAnalysis:
      "Cabin 12142 is situated on Deck 12 (port side), positioned almost exactly midship. This represents one of the most structurally stable zones on the vessel, minimizing pitch and roll during rough sea transits. It is buffered directly above and below by quiet passenger stateroom decks (Deck 11 and Deck 13), ensuring zero mechanical or dining noise transfer.",
    epistemicStatus: "KNOWN",
    statements: ["STM-VIR-12142-CAT", "STM-VIR-12142-LOC", "STM-VIR-12142-DIM"],
    evidenceArtifactId: "MSC-VIR-GA-2021-P12",
  },
};

export const CANONICAL_PORTS: Record<string, any> = {
  "santorini": {
    slug: "santorini",
    name: "Santorini, Greece",
    tenderPort: true,
    bodyOfWater: "Aegean Sea",
    population: "15,500",
    currency: "EUR (€)",
    language: "Greek",
    heroImageUrl: "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&w=1600&q=80",
    overviewText:
      "Santorini is a world-famous volcanic island in the Cyclades. Cruise ships anchor offshore in the caldera, with passenger tenders arriving at the Old Port of Fira (Fira Skala). Access to the town cliff-top is via cable car, walking steps, or organized excursion buses from Athinios Port.",
    gettingAround: "Tender boats take ~10-15 min to Old Port. The Cable Car costs €6 per direction. Taxis and local KTEL buses connect Fira to Oia, Kamari, and Akrotiri.",
    allAboardWarning: "High-season cable car queues at Fira can exceed 60-90 minutes in the afternoon. Always allocate at least 2 hours before all-aboard time to return to the tender pier.",
  },
  "genoa": {
    slug: "genoa",
    name: "Genoa, Italy",
    tenderPort: false,
    bodyOfWater: "Ligurian Sea",
    population: "580,000",
    currency: "EUR (€)",
    language: "Italian",
    heroImageUrl: "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=1600&q=80",
    overviewText:
      "Ponte dei Mille Cruise Terminal is located right next to the historic city center of Genoa. The historic harbor (Porto Antico), Aquarium, and Palazzi dei Rolli are within a 10-15 minute walk from the gangway.",
    gettingAround: "Direct walking access to Piazza Principe train station and Metro. Trains to Portofino and Cinque Terre depart regularly.",
    allAboardWarning: "Standard 30-minute all-aboard rule prior to departure. Zero tender transfers required.",
  },
};

export const CANONICAL_ROUTES: Record<string, any> = {
  "7-night-adriatic-aegean": {
    slug: "7-night-adriatic-aegean",
    title: "7-Night Adriatic & Aegean",
    vesselName: "MSC Virtuosa",
    seasonalProfile: "March 2026",
    ports: [
      { day: 1, portName: "Venice (Italy)", status: "Embarkation / 18:00 Departure", epistemic: "LIKELY" },
      { day: 2, portName: "Bari (Italy)", status: "08:00 — 14:00 Port Call", epistemic: "LIKELY" },
      { day: 3, portName: "Corfu (Greece)", status: "09:00 — 19:00 Port Call", epistemic: "LIKELY" },
      { day: 4, portName: "Mykonos (Greece)", status: "08:00 — 20:00 Port Call", epistemic: "LIKELY" },
      { day: 5, portName: "Sea Day", status: "Cruising Southern Aegean", epistemic: "KNOWN" },
      { day: 6, portName: "Dubrovnik (Croatia)", status: "07:00 — 14:00 Port Call", epistemic: "LIKELY" },
      { day: 7, portName: "Venice (Italy)", status: "09:00 Disembarkation", epistemic: "LIKELY" },
    ],
    weatherOverview: "Typical spring conditions expected across the Adriatic and Southern Aegean zones during the March transit (10°C - 16°C, occasional light mist).",
  },
};

export const CANONICAL_CRUISE_MATH = {
  // Cruise Math is a calculator, and it was quietly also a claim: it opened on
  // "MSC Virtuosa", "Mediterranean", 7 nights and a EUR 1890 fare, so a tester
  // sailing Bellissima to Tokyo for three nights read a confident summary of
  // somebody else's holiday. The day rates below are genuine generic inputs and
  // stay. The identity does not: no ship is named, and the fare is an example.
  defaultConfig: {
    shipSlug: null,
    shipName: null,
    destination: null,
    durationNights: 7,
    travelers: 2,
    // An illustrative figure for the worked example, not a quoted price and not
    // this voyage's fare. Timonelo holds no pricing for the live-test trip.
    baseFareEur: 1890,
    baseFareIsExample: true,
  },
  drinkPackages: [
    {
      id: "easy",
      name: "Easy Drink Package",
      pricePerDayPerPerson: 49,
      description: "Covers classic hot beverages, standard draft beers, house wines by the glass, and selected spirits.",
      breakEven: "Approx. 5 drinks daily per guest",
      epistemic: "KNOWN",
    },
    {
      id: "premium-extra",
      name: "Premium Extra Package",
      pricePerDayPerPerson: 69,
      description: "Covers premium craft beers, high-end specialty cocktails, top-shelf spirits, and premium bottled waters.",
      breakEven: "Approx. 6 drinks daily per guest",
      epistemic: "KNOWN",
    },
  ],
  tripSummaryDefaults: {
    baseFare: 1890.00,
    drinkPackages: { min: 686.00, max: 966.00 },
    specialtyDining: 140.00,
    onboardInternet: { min: 0.00, max: 350.00 },
    dailyGratuities: 196.00, // 7 nights * 2 guests * 14€
    portExcursions: { min: 200.00, max: 600.00 },
  },
};

// CANONICAL_TRAVEL_INFO is gone. It held three Schengen entries -- Italy,
// Greece, Croatia -- each marked KNOWN, and Travel Info rendered them beneath a
// promise that they had been researched for the reader's own itinerary. The
// live-test voyage sails Shanghai to Tokyo, so a passenger was being told with
// confidence that they needed no advance visa, about countries they were not
// visiting, for a region whose rules are nothing like the ones that applied.
//
// It is deleted rather than narrowed. Keeping the shape and swapping in China
// and Japan entries written from general knowledge would be the same defect
// with fresher-sounding facts, and this is the one surface where being
// plausibly wrong can cost someone their sailing. Travel Info now says it does
// not have this voyage yet and points at the authorities who do.
