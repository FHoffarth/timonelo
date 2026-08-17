/**
 * Timonelo Spatial Grammar Engine
 * 
 * Discovers and formalizes the semantic organisation of the canonical MSC deck plan:
 * - 4 Parallel Topological Tracks: Port Outer, Port Inner, Starboard Inner, Starboard Outer
 * - Structural Skeleton: Lift Core A (Forward), Midship Panoramic Core, Lift Core B (Aft)
 * - End Caps: Forward Bow Wedge & Aft Stern Transom
 * - Interrupted Runs: Discrete zone blocks separated by structural vertical cores
 */

import { SemanticEntity, SemanticLevel } from "./types";

export interface CabinTrack {
  trackId: "PORT_OUTER" | "PORT_INNER" | "STARBOARD_INNER" | "STARBOARD_OUTER" | "BOW_WEDGE" | "STERN_TRANSOM";
  label: string;
  spaces: SemanticEntity[];
}

export interface StructuralZoneBlock {
  zoneId: "BOW_CAP" | "FORWARD_RUN" | "LIFT_CORE_A" | "MIDSHIP_RUN" | "PANORAMIC_CORE" | "AFT_RUN" | "LIFT_CORE_B" | "STERN_TRANSOM";
  title: string;
  subtitle: string;
  isStructuralCore: boolean;
  coreDetails?: {
    elevatorCount: number;
    stairwells: boolean;
    serviceAccess: string;
    connectsDecks: string;
  };
  portOuterTrack: SemanticEntity[];
  portInnerTrack: SemanticEntity[];
  starboardInnerTrack: SemanticEntity[];
  starboardOuterTrack: SemanticEntity[];
  transverseTrack?: SemanticEntity[];
}

export interface DeckSpatialGrammarModel {
  deckLevel: number;
  deckName: string;
  totalSpaces: number;
  bowWedgeCap: SemanticEntity[];
  sternTransomCap: SemanticEntity[];
  zoneBlocks: StructuralZoneBlock[];
  tracksSummary: {
    portOuterCount: number;
    portInnerCount: number;
    starboardInnerCount: number;
    starboardOuterCount: number;
  };
}

/**
 * Builds the canonical Spatial Grammar Model for any given deck level
 */
export function buildDeckSpatialGrammar(level: SemanticLevel): DeckSpatialGrammarModel {
  const spaces = level.spaces || [];

  // Separate Port, Center/Interior, Starboard
  const portSpaces = spaces.filter((s) => s.side === "PORT");
  const centerSpaces = spaces.filter((s) => s.side === "CENTER");
  const starboardSpaces = spaces.filter((s) => s.side === "STARBOARD");

  // Distinguish Outer vs Inner staterooms
  // In MSC numbering:
  // Port Outer (Balcony/OceanView): odd numbers starting with lower tens / high hundreds
  // Port Inner (Interior): odd numbers placed centrally (e.g., 14089, 14091, 14123)
  // Starboard Inner (Interior): even numbers placed centrally (e.g., 14088, 14090, 14122)
  // Starboard Outer (Balcony/OceanView): even numbers on the outer perimeter

  const isInterior = (s: SemanticEntity) =>
    s.classification === "STATEROOM_INTERIOR" || s.classification_label.toLowerCase().includes("interior");

  const portOuter = portSpaces.filter((s) => !isInterior(s));
  const portInner = [...portSpaces.filter(isInterior), ...centerSpaces.filter((_, idx) => idx % 2 === 1)];

  const stbdOuter = starboardSpaces.filter((s) => !isInterior(s));
  const stbdInner = [...starboardSpaces.filter(isInterior), ...centerSpaces.filter((_, idx) => idx % 2 === 0)];

  // Bow & Stern Caps
  const bowSpaces = spaces.filter((s) => s.zone.includes("BOW") || s.zone.includes("FORWARD_CAP"));
  const bowWedgeCap = bowSpaces.length > 0 ? bowSpaces : [...portOuter.slice(0, 2), ...stbdOuter.slice(0, 2)];

  const sternSpaces = spaces.filter((s) => s.zone.includes("STERN") || s.zone.includes("AFT_TRANSOM"));
  const sternTransomCap = sternSpaces.length > 0 ? sternSpaces : [...portOuter.slice(-2), ...stbdOuter.slice(-2)];

  // Slice into 3 sequential runs across the ship length: Forward, Midship, Aft
  const sliceTrack = (track: SemanticEntity[]) => {
    const total = track.length;
    if (total === 0) return { fwd: [], mid: [], aft: [] };
    const fwdEnd = Math.floor(total * 0.35);
    const midEnd = Math.floor(total * 0.70);
    return {
      fwd: track.slice(0, fwdEnd),
      mid: track.slice(fwdEnd, midEnd),
      aft: track.slice(midEnd),
    };
  };

  const pOut = sliceTrack(portOuter);
  const pIn = sliceTrack(portInner);
  const sIn = sliceTrack(stbdInner);
  const sOut = sliceTrack(stbdOuter);

  // Construct the 5 Structural Zone Blocks
  const zoneBlocks: StructuralZoneBlock[] = [
    // 1. Forward Stateroom Run
    {
      zoneId: "FORWARD_RUN",
      title: "Forward Section",
      subtitle: "Bow Residential Quarter",
      isStructuralCore: false,
      portOuterTrack: pOut.fwd,
      portInnerTrack: pIn.fwd,
      starboardInnerTrack: sIn.fwd,
      starboardOuterTrack: sOut.fwd,
    },
    // 2. Lift Core A (Forward Elevators & Grand Stairs)
    {
      zoneId: "LIFT_CORE_A",
      title: "Forward Lift Core A",
      subtitle: "6 Elevators + Grand Stairwell",
      isStructuralCore: true,
      coreDetails: {
        elevatorCount: 6,
        stairwells: true,
        serviceAccess: "Galley Riser & Linen Station A",
        connectsDecks: "Decks 4 — 19",
      },
      portOuterTrack: [],
      portInnerTrack: [],
      starboardInnerTrack: [],
      starboardOuterTrack: [],
    },
    // 3. Midship Stateroom Run & Panoramic Core
    {
      zoneId: "MIDSHIP_RUN",
      title: "Midship Central Section",
      subtitle: "Flanked by Panoramic Elevators & Atrium Overlook",
      isStructuralCore: false,
      portOuterTrack: pOut.mid,
      portInnerTrack: pIn.mid,
      starboardInnerTrack: sIn.mid,
      starboardOuterTrack: sOut.mid,
    },
    // 4. Lift Core B (Aft Elevators & Service Spine)
    {
      zoneId: "LIFT_CORE_B",
      title: "Aft Lift Core B",
      subtitle: "4 Elevators + Aft Stairwell",
      isStructuralCore: true,
      coreDetails: {
        elevatorCount: 4,
        stairwells: true,
        serviceAccess: "Emergency Vertical Shaft & Service Core B",
        connectsDecks: "Decks 5 — 18",
      },
      portOuterTrack: [],
      portInnerTrack: [],
      starboardInnerTrack: [],
      starboardOuterTrack: [],
    },
    // 5. Aft Stateroom Run & Stern Wake View
    {
      zoneId: "AFT_RUN",
      title: "Aft Section & Transom",
      subtitle: "Scenic Wake View Corridor",
      isStructuralCore: false,
      portOuterTrack: pOut.aft,
      portInnerTrack: pIn.aft,
      starboardInnerTrack: sIn.aft,
      starboardOuterTrack: sOut.aft,
    },
  ];

  return {
    deckLevel: level.level_index,
    deckName: level.level_name,
    totalSpaces: spaces.length,
    bowWedgeCap,
    sternTransomCap,
    zoneBlocks,
    tracksSummary: {
      portOuterCount: portOuter.length,
      portInnerCount: portInner.length,
      starboardInnerCount: stbdInner.length,
      starboardOuterCount: stbdOuter.length,
    },
  };
}
