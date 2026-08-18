/**
 * explainability/RuleRegistry.ts
 * 
 * Central registry of all deterministic intelligence rules.
 * Every rule has complete weight transparency, required graph edges, and evidence provenance.
 */

import { RuleDefinition } from "./types";

export const RULE_REGISTRY: Record<string, RuleDefinition> = {
  // =========================================================================
  // 1. TRANQUILITY & QUIETNESS RULES (category: "quiet")
  // =========================================================================
  "RULE-QUIET-001": {
    id: "RULE-QUIET-001",
    category: "quiet",
    title: "Pure Residential Buffer Deck",
    description: "Stateroom is sandwiched between purely residential stateroom decks above and below with zero active public venues.",
    weight: 6,
    polarity: "POSITIVE",
    required_graph_relations: ["adjacent_overhead", "adjacent_underfoot"],
    required_knowledge_entities: ["decks.json", "cabins.json"],
    required_geometry: ["deck09.geometry.json", "deck10.geometry.json", "deck11.geometry.json", "deck12.geometry.json", "deck13.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 4,
      title: "MSC Bellissima Residential Decks 9-13 Plan",
    },
  },
  "RULE-QUIET-002": {
    id: "RULE-QUIET-002",
    category: "quiet",
    title: "Absence of Nightlife & Theatre Venues Adjacent",
    description: "No high-energy entertainment venue (Carousel Lounge, Casino, London Theatre) directly below or adjacent.",
    weight: 8,
    polarity: "POSITIVE",
    required_graph_relations: ["adjacent_underfoot", "adjacent_across"],
    required_knowledge_entities: ["entertainment.json", "lounges.json"],
    required_geometry: ["deck06.geometry.json", "deck07.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 3,
      title: "MSC Bellissima Public Decks 5-7 Plan",
    },
  },
  "RULE-QUIET-004": {
    id: "RULE-QUIET-004",
    category: "quiet",
    title: "Marketplace Buffet Overhead Galley Proximity",
    description: "A public buffet directly above reduces acoustic tranquility due to early morning cart rolling, cleaning, and galley prep.",
    weight: -24,
    polarity: "NEGATIVE",
    required_graph_relations: ["adjacent_overhead"],
    required_knowledge_entities: ["RES-MARKETPLACE-BUFFET", "restaurants.json"],
    required_geometry: ["deck15.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 5,
      title: "MSC Bellissima Deck 15 Upper Deck Plan",
    },
  },
  "RULE-QUIET-005": {
    id: "RULE-QUIET-005",
    category: "quiet",
    title: "Open Pool Deck Overhead Lounger Scraping",
    description: "Open pool sundeck or aquapark located overhead causes morning lounger setup and footfall vibrations.",
    weight: -18,
    polarity: "NEGATIVE",
    required_graph_relations: ["adjacent_overhead"],
    required_knowledge_entities: ["pools.json", "public_areas.json"],
    required_geometry: ["deck15.geometry.json", "deck19.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 5,
      title: "MSC Bellissima Deck 15 & 19 Pool Decks",
    },
  },
  "RULE-QUIET-006": {
    id: "RULE-QUIET-006",
    category: "quiet",
    title: "Nightclub / Casino Floor Underfoot",
    description: "Nightclub (Attic Club) or Casino Imperiale directly underfoot introduces bass resonance through structural deckhead.",
    weight: -22,
    polarity: "NEGATIVE",
    required_graph_relations: ["adjacent_underfoot"],
    required_knowledge_entities: ["entertainment.json", "lounges.json"],
    required_geometry: ["deck07.geometry.json", "deck18.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 3,
      title: "MSC Bellissima Entertainment Floor Plans",
    },
  },

  // =========================================================================
  // 2. MOTION & STABILITY RULES (category: "motion")
  // =========================================================================
  "RULE-MOTION-001": {
    id: "RULE-MOTION-001",
    category: "motion",
    title: "Midship Flotation Center Neutral Axis",
    description: "Stateroom is positioned within the midship neutral roll-pitch center of flotation (FR-110 to FR-160), offering optimal seakeeping.",
    weight: 12,
    polarity: "POSITIVE",
    required_graph_relations: ["zone", "level"],
    required_knowledge_entities: ["technical.json"],
    required_geometry: ["deck08.geometry.json", "deck09.geometry.json", "deck10.geometry.json", "deck11.geometry.json", "deck12.geometry.json", "deck13.geometry.json", "deck14.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 4,
      title: "MSC Bellissima Midship Elevation Grid",
    },
  },
  "RULE-MOTION-002": {
    id: "RULE-MOTION-002",
    category: "motion",
    title: "Forward Bow Heave & Pitch Acceleration",
    description: "Forward bow staterooms experience maximum vertical acceleration (heave/slamming) during head seas.",
    weight: -18,
    polarity: "NEGATIVE",
    required_graph_relations: ["zone"],
    required_knowledge_entities: ["technical.json"],
    required_geometry: ["deck08.geometry.json", "deck09.geometry.json", "deck10.geometry.json", "deck11.geometry.json", "deck12.geometry.json", "deck13.geometry.json", "deck14.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 4,
      title: "MSC Bellissima Forward Bow Frame Layout",
    },
  },
  "RULE-MOTION-003": {
    id: "RULE-MOTION-003",
    category: "motion",
    title: "Low Vertical Elevation Stability",
    description: "Low deck location (Deck 5-8) close to waterline minimizes pendulum roll momentum.",
    weight: 5,
    polarity: "POSITIVE",
    required_graph_relations: ["level"],
    required_knowledge_entities: ["technical.json"],
    required_geometry: ["deck05.geometry.json", "deck08.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 3,
      title: "MSC Bellissima Lower Hull Elevation",
    },
  },
  "RULE-MOTION-004": {
    id: "RULE-MOTION-004",
    category: "motion",
    title: "High Deck Roll Amplitude",
    description: "High deck location (Deck 14+) amplifies horizontal displacement during vessel roll in heavy swell.",
    weight: -10,
    polarity: "NEGATIVE",
    required_graph_relations: ["level"],
    required_knowledge_entities: ["technical.json"],
    required_geometry: ["deck14.geometry.json", "deck15.geometry.json", "deck16.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 5,
      title: "MSC Bellissima Upper Deck Layout",
    },
  },

  // =========================================================================
  // 3. WALKING & LIFT RULES (category: "walking")
  // =========================================================================
  "RULE-WALK-001": {
    id: "RULE-WALK-001",
    category: "walking",
    title: "Direct Elevator Lobby Corridor Connection",
    description: "Immediate corridor link to vertical core bank within short walking radius.",
    weight: 8,
    polarity: "POSITIVE",
    required_graph_relations: ["connected_vertical_core"],
    required_knowledge_entities: ["decks.json"],
    required_geometry: ["deck14.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 4,
      title: "MSC Bellissima Lift Lobby Access Points",
    },
  },

  // =========================================================================
  // 4. PRIVACY RULES (category: "privacy")
  // =========================================================================
  "RULE-PRIV-001": {
    id: "RULE-PRIV-001",
    category: "privacy",
    title: "Private Ocean View Balcony Sightline",
    description: "Private balcony facing outward towards the open sea with zero public overlooking walkways.",
    weight: 5,
    polarity: "POSITIVE",
    required_graph_relations: ["has_balcony", "side"],
    required_knowledge_entities: ["cabins.json"],
    required_geometry: ["deck14.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 2,
      title: "MSC Bellissima Balcony Category Specifications",
    },
  },

  // =========================================================================
  // 5. ACCESSIBILITY RULES (category: "accessibility")
  // =========================================================================
  "RULE-ACC-001": {
    id: "RULE-ACC-001",
    category: "accessibility",
    title: "Official PRM Certified Accessible Stateroom (H)",
    description: "Official PRM stateroom certified with 85cm wide doors, zero threshold step-free entry, and roll-in shower with grab bars.",
    weight: 28,
    polarity: "POSITIVE",
    required_graph_relations: ["accessible"],
    required_knowledge_entities: ["cabins.json"],
    required_geometry: ["deck14.geometry.json"],
    required_evidence: {
      artifact_id: "MSC_BELLISSIMA_DECK_PLANS_11.2025_DEU",
      page: 2,
      title: "MSC Bellissima Accessible Staterooms Legend (Symbol H)",
    },
  },
};
