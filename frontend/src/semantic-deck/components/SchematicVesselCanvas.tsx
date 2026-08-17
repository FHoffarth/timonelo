import React, { useRef, useState, useEffect } from "react";
import { SemanticLevel, SemanticEntity } from "../types";
import { getClassificationColorToken, getEpistemicPatternToken } from "../apiClient";
import { useTheme } from "../themeContext";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Compass,
  Utensils,
  Film,
  Building,
  Layers,
  Sparkles,
  Accessibility,
  ArrowRight,
  ShieldCheck,
  Calculator,
  HelpCircle,
  AlertTriangle,
  Move,
  Activity,
  Waves,
  Sun,
  Crown,
  Gamepad2,
  HeartPulse,
} from "lucide-react";

interface SchematicVesselCanvasProps {
  level: SemanticLevel;
  selectedEntity: SemanticEntity | null;
  hoveredEntity: SemanticEntity | null;
  allLevels: SemanticLevel[];
  onSelectLevel: (levelIndex: number) => void;
  onSelectEntity: (entity: SemanticEntity) => void;
  onHoverEntity: (entity: SemanticEntity | null) => void;
}

// Deck-specific canonical venues based on the official MSC Bellissima deck plan
function getDeckLandmarks(deckLevel: number) {
  switch (deckLevel) {
    case 5:
      return {
        fwd: { title: "London Theatre", sub: "Main Stage • Capacity 975", icon: "Film", type: "ENTERTAINMENT" },
        midFwd: { title: "Infinity Reception", sub: "Guest Services & Excursions", icon: "Building", type: "SERVICE" },
        mid: { title: "Infinity Atrium", sub: "Swarovski Crystal Staircase", icon: "Sparkles", type: "PUBLIC" },
        midAft: { title: "Infinity Bar", sub: "Lounge & Live Music", icon: "Utensils", type: "LOUNGE" },
        aft: { title: "Posidonia Restaurant", sub: "Main Dining Room", icon: "Utensils", type: "DINING" },
      };
    case 6:
      return {
        fwd: { title: "London Theatre (Upper)", sub: "Balcony Seating", icon: "Film", type: "ENTERTAINMENT" },
        midFwd: { title: "Galleria Bellissima", sub: "Jean-Philippe Chocolat & Boutiques", icon: "Sparkles", type: "PROMENADE" },
        mid: { title: "LED Sky Dome", sub: "80m Visual Dome & Edge Cocktail Bar", icon: "Sparkles", type: "PUBLIC" },
        midAft: { title: "Il Ciliegio & Le Cerisier", sub: "Specialty Dining Rooms", icon: "Utensils", type: "DINING" },
        aft: { title: "Lighthouse Restaurant", sub: "Panoramic Stern Dining", icon: "Utensils", type: "DINING" },
      };
    case 7:
      return {
        fwd: { title: "MSC Aurea Spa", sub: "Thermal Area & Balinese Massage", icon: "HeartPulse", type: "WELLNESS" },
        midFwd: { title: "Specialty Dining Hub", sub: "Kaito Teppanyaki, Sushi & Butcher's Cut", icon: "Utensils", type: "DINING" },
        mid: { title: "TV Studio & Masters of the Sea", sub: "British Pub & Broadcasting Bar", icon: "Sparkles", type: "LOUNGE" },
        midAft: { title: "Imperial Casino", sub: "Gaming Tables & Slots", icon: "Sparkles", type: "ENTERTAINMENT" },
        aft: { title: "Carousel Lounge", sub: "Cirque / Immersive Shows & Dining", icon: "Film", type: "ENTERTAINMENT" },
      };
    case 15:
      return {
        fwd: { title: "Top Sail Lounge / YC", sub: "Exclusive Yacht Club Panoramic Lounge", icon: "Crown", type: "YACHT_CLUB" },
        midFwd: { title: "Grand Canyon Pool", sub: "Sliding Glass Magrodome Roof", icon: "Waves", type: "POOL" },
        mid: { title: "Atmosphere Pool", sub: "Central Pool Deck & Giant LED Screen", icon: "Sun", type: "POOL" },
        midAft: { title: "Marketplace Buffet", sub: "1,345 Seats • Mediterranean Cuisine", icon: "Utensils", type: "DINING" },
        aft: { title: "Marketplace Family & Kids", sub: "Horizon Pool & Bar Overlook", icon: "Utensils", type: "DINING" },
      };
    case 16:
      return {
        fwd: { title: "Top Sail Solarium (YC)", sub: "Yacht Club Private Forward Sundeck", icon: "Crown", type: "YACHT_CLUB" },
        midFwd: { title: "Power Walking Track", sub: "328m Jogging Circuit", icon: "Activity", type: "FITNESS" },
        mid: { title: "MSC Gym by Technogym", sub: "Panoramic Fitness Centre", icon: "HeartPulse", type: "FITNESS" },
        midAft: { title: "Virtual Arcade & Cinema", sub: "XD Cinema, VR Maze, Formula Racer", icon: "Gamepad2", type: "ENTERTAINMENT" },
        aft: { title: "Sportplex & Horizon Amphitheatre", sub: "Basketball, Football Arena & Sun Deck", icon: "Activity", type: "SPORTS" },
      };
    case 18:
      return {
        fwd: { title: "MSC Yacht Club Restaurant", sub: "Fine Dining for Suites", icon: "Crown", type: "YACHT_CLUB" },
        midFwd: { title: "MSC Yacht Club Grill & Bar", sub: "Private Open-Air Terrace", icon: "Crown", type: "YACHT_CLUB" },
        mid: { title: "Sky Lounge", sub: "Piano Bar & Panoramic Ocean Vista", icon: "Sparkles", type: "LOUNGE" },
        midAft: { title: "Doremi Lab & Studio", sub: "Children's Interactive Center", icon: "Gamepad2", type: "KIDS" },
        aft: { title: "Doremiland (Lego & Chicco)", sub: "Baby, Mini, Junior, Teen Clubs", icon: "Gamepad2", type: "KIDS" },
      };
    case 19:
      return {
        fwd: { title: "Top 19 Solarium", sub: "Exclusive Adults Sundeck & Spa Tub", icon: "Sun", type: "SOLARIUM" },
        midFwd: { title: "MSC Yacht Club Sundeck", sub: "Private Whirlpool & Cabanas", icon: "Crown", type: "YACHT_CLUB" },
        mid: { title: "Himalayan Bridge", sub: "82m High Suspension Rope Walk", icon: "Activity", type: "ADVENTURE" },
        midAft: { title: "Arizona Aquapark", sub: "3 Water Slides & Champagne Bowl", icon: "Waves", type: "AQUAPARK" },
        aft: { title: "Arizona Bar & Splash Area", sub: "Poolside Refreshments", icon: "Utensils", type: "AQUAPARK" },
      };
    default:
      // Decks 8, 9, 10, 11, 12, 13, 14 (Canonical Stateroom Decks)
      return {
        fwd: { title: "Forward Suites & Staterooms", sub: "Bow Facing Deluxe Balconies & Suites", icon: "Crown", type: "STATEROOM_ZONE" },
        midFwd: { title: "Forward Lift Core (Core A)", sub: "6 Elevators + Main Forward Stairwell", icon: "Layers", type: "VERTICAL_CORE" },
        mid: { title: "Midship Panoramic Core", sub: "Glass Panoramic Lifts & Central Atrium Void", icon: "Sparkles", type: "VERTICAL_CORE" },
        midAft: { title: "Aft Lift Core (Core B)", sub: "4 Elevators + Service Galley Core", icon: "Layers", type: "VERTICAL_CORE" },
        aft: { title: "Aft Transom Balconies", sub: "Scenic Wake View Staterooms", icon: "Crown", type: "STATEROOM_ZONE" },
      };
  }
}

export default function SchematicVesselCanvas({
  level,
  selectedEntity,
  hoveredEntity,
  allLevels,
  onSelectLevel,
  onSelectEntity,
  onHoverEntity,
}: SchematicVesselCanvasProps) {
  const { theme } = useTheme();
  const isNight = theme === "night";

  const [zoom, setZoom] = useState(1);
  const [activeZone, setActiveZone] = useState<"ALL" | "FWD" | "MID" | "AFT">("ALL");

  const selectedRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to selected cell
  useEffect(() => {
    if (selectedRef.current && viewportRef.current) {
      selectedRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });
    }
  }, [selectedEntity?.id]);

  const spaces = level.spaces || [];
  const landmarks = getDeckLandmarks(level.level_index);

  // Filter spaces by zone if selected
  const filterSpaces = (list: SemanticEntity[]) => {
    if (activeZone === "ALL") return list;
    if (activeZone === "FWD") return list.filter((s) => s.zone.includes("FORWARD") || s.zone.includes("BOW"));
    if (activeZone === "MID") return list.filter((s) => s.zone.includes("MID"));
    if (activeZone === "AFT") return list.filter((s) => s.zone.includes("AFT") || s.zone.includes("STERN"));
    return list;
  };

  const portSpaces = filterSpaces(spaces.filter((s) => s.side === "PORT"));
  const centerSpaces = filterSpaces(spaces.filter((s) => s.side === "CENTER"));
  const starboardSpaces = filterSpaces(spaces.filter((s) => s.side === "STARBOARD"));

  // Portside sections matching official sequence
  const bowPort = portSpaces.slice(0, Math.min(2, portSpaces.length));
  const fwdPort = portSpaces.slice(2, Math.floor(portSpaces.length * 0.4));
  const midPort = portSpaces.slice(Math.floor(portSpaces.length * 0.4), Math.floor(portSpaces.length * 0.75));
  const aftPort = portSpaces.slice(Math.floor(portSpaces.length * 0.75), Math.max(0, portSpaces.length - 2));
  const sternPort = portSpaces.slice(Math.max(0, portSpaces.length - 2));

  // Starboard sections matching official sequence
  const bowStbd = starboardSpaces.slice(0, Math.min(2, starboardSpaces.length));
  const fwdStbd = starboardSpaces.slice(2, Math.floor(starboardSpaces.length * 0.4));
  const midStbd = starboardSpaces.slice(Math.floor(starboardSpaces.length * 0.4), Math.floor(starboardSpaces.length * 0.75));
  const aftStbd = starboardSpaces.slice(Math.floor(starboardSpaces.length * 0.75), Math.max(0, starboardSpaces.length - 2));
  const sternStbd = starboardSpaces.slice(Math.max(0, starboardSpaces.length - 2));

  const renderCell = (space: SemanticEntity) => {
    const isSelected = selectedEntity?.id === space.id;
    const isHovered = hoveredEntity?.id === space.id;

    // Check adjacent neighbor relation
    const isNeighbor =
      selectedEntity &&
      selectedEntity.level === space.level &&
      (selectedEntity.relations?.adjacent_fore === space.id ||
        selectedEntity.relations?.adjacent_aft === space.id ||
        selectedEntity.relations?.adjacent_across === space.id);

    const colorToken = getClassificationColorToken(space.classification);
    const patternToken = getEpistemicPatternToken(space.epistemic_state);

    return (
      <div
        key={space.id}
        ref={isSelected ? selectedRef : null}
        id={`space-cell-${space.id}`}
        onClick={() => onSelectEntity(space)}
        onMouseEnter={() => onHoverEntity(space)}
        onMouseLeave={() => onHoverEntity(null)}
        className={`relative group cursor-pointer transition-all duration-150 rounded-lg p-1.5 flex flex-col justify-between select-none min-w-[52px] max-w-[60px] h-[74px] border ${
          isNight ? colorToken.bg : "bg-white shadow-sm"
        } ${patternToken.borderClass} ${
          isSelected
            ? "ring-2 ring-sky-400 shadow-xl shadow-sky-500/40 scale-[1.09] z-30 font-bold"
            : isNeighbor
            ? "ring-1.5 ring-emerald-400 shadow-md shadow-emerald-500/20 scale-[1.03] z-20"
            : isHovered
            ? "scale-[1.04] shadow-md z-20"
            : "hover:border-slate-400"
        }`}
      >
        {/* Selection pointer arrow at bottom pointing up into cell */}
        {isSelected && (
          <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-b-[6px] border-b-sky-400 animate-bounce" />
        )}

        {/* Top: Space ID & Category Dot */}
        <div className="flex items-center justify-between gap-0.5">
          <span
            className={`font-mono text-[10.5px] font-bold tracking-tight truncate ${
              isSelected
                ? "text-sky-300"
                : isNight
                ? colorToken.text
                : "text-slate-900"
            }`}
          >
            {space.id}
          </span>
          <span
            className="w-1.5 h-1.5 rounded-full shrink-0"
            style={{ backgroundColor: colorToken.dotColor }}
            title={space.classification_label}
          />
        </div>

        {/* Middle: Classification abbreviation or PRM */}
        <div className="flex items-center justify-center my-0.5">
          {space.accessible ? (
            <span className="px-1 py-0.2 rounded text-[7.5px] font-mono font-bold bg-sky-500/20 text-sky-400 border border-sky-400/30">
              PRM
            </span>
          ) : (
            <span className="text-[8px] font-mono text-slate-400 truncate">
              {space.classification_label.split(" ")[0]}
            </span>
          )}
        </div>

        {/* Bottom: Epistemic State & Confidence */}
        <div className="flex items-center justify-between text-[7.5px] font-mono text-slate-400 pt-0.5 border-t border-white/5">
          <span>{space.epistemic_state[0]}</span>
          <span className="text-slate-500 font-mono">#{(space.confidence * 100).toFixed(0)}</span>
        </div>
      </div>
    );
  };

  return (
    <div
      className={`relative flex-1 h-full flex flex-col overflow-y-auto no-scrollbar select-none transition-colors duration-200 ${
        isNight ? "bg-slate-950 text-white" : "bg-slate-100 text-slate-900"
      }`}
    >
      {/* 1. Level Header & Epistemic Summary Bar */}
      <div
        className={`px-8 py-3.5 border-b flex items-center justify-between z-20 backdrop-blur-xl shrink-0 ${
          isNight ? "bg-slate-900/85 border-white/10" : "bg-white/95 border-slate-200"
        }`}
      >
        <div className="flex items-center gap-3">
          <div className="px-3 py-1 rounded-xl font-mono font-bold text-xs bg-sky-500/20 text-sky-400 border border-sky-400/30">
            LEVEL {level.level_index}
          </div>
          <div>
            <h2 className="text-base font-bold tracking-tight">
              {level.level_name}
            </h2>
            <p className="text-[11px] font-mono text-slate-400">
              Canonical Schematic View • {level.spaces_count} Verified Semantic Spaces • Topology Aware
            </p>
          </div>
        </div>

        {/* Epistemic Health Stats */}
        <div className="flex items-center gap-5 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-emerald-400 font-semibold">{level.epistemic_breakdown.direct} Direct</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-sm border border-sky-400 bg-sky-500/30" />
            <span className="text-sky-400 font-semibold">{level.epistemic_breakdown.derived} Derived</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full border border-dashed border-slate-400" />
            <span className="text-slate-400">{level.epistemic_breakdown.unknown} Unknown</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rotate-45 bg-amber-400" />
            <span className="text-amber-400">{level.epistemic_breakdown.conflict} Conflict</span>
          </div>
        </div>

        {/* Pan & Zoom Controls */}
        <div className="flex items-center gap-1.5">
          <div
            className={`p-1 rounded-xl border flex items-center gap-1 ${
              isNight ? "bg-slate-950/80 border-white/10" : "bg-slate-100 border-slate-200"
            }`}
          >
            <button
              onClick={() => setZoom((z) => Math.max(0.6, z - 0.1))}
              className={`p-1.5 rounded-lg transition-colors ${
                isNight ? "hover:bg-white/10 text-slate-300" : "hover:bg-white text-slate-700"
              }`}
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="px-1 text-[11px] font-mono font-bold text-slate-400 min-w-[36px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => setZoom((z) => Math.min(1.5, z + 0.1))}
              className={`p-1.5 rounded-lg transition-colors ${
                isNight ? "hover:bg-white/10 text-slate-300" : "hover:bg-white text-slate-700"
              }`}
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setZoom(1)}
              className={`p-1.5 rounded-lg transition-colors ${
                isNight ? "hover:bg-white/10 text-slate-300" : "hover:bg-white text-slate-700"
              }`}
              title="Reset Zoom (100%)"
            >
              <Maximize2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Master Schematic Hull Silhouette Viewport */}
      <div
        ref={viewportRef}
        className="relative flex-1 p-8 flex items-center justify-center overflow-x-auto overflow-y-auto no-scrollbar min-h-[460px]"
      >
        <div
          style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
          className="relative transition-transform duration-150 ease-out py-4"
        >
          {/* Hull Silhouette Container with Bow & Stern Curvature */}
          <div
            className={`relative rounded-[100px_45px_45px_100px] border-2 p-8 shadow-2xl backdrop-blur-2xl transition-all duration-300 min-w-[1340px] max-w-[1600px] ${
              isNight
                ? "bg-slate-900/75 border-slate-700/80 shadow-black/80 ring-1 ring-white/5"
                : "bg-white/95 border-slate-300 shadow-slate-300/60 ring-1 ring-black/5"
            }`}
          >
            {/* Outer Bow / Stern Structural Markers */}
            <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-1 text-slate-500 font-mono text-[10px] uppercase font-bold tracking-widest pointer-events-none">
              <span>BOW</span>
              <span className="w-1.5 h-6 bg-slate-700 rounded-full" />
              <span>FWD</span>
            </div>

            <div className="absolute right-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-1 text-slate-500 font-mono text-[10px] uppercase font-bold tracking-widest pointer-events-none">
              <span>AFT</span>
              <span className="w-1.5 h-6 bg-slate-700 rounded-full" />
              <span>STERN</span>
            </div>

            {/* Compass Rose Indicator (Top Right) */}
            <div
              className={`absolute right-12 top-6 p-2 rounded-2xl border flex flex-col items-center gap-1 text-[9px] font-mono z-20 ${
                isNight ? "bg-slate-950/80 border-white/10 text-slate-400" : "bg-white/90 border-slate-200 text-slate-600"
              }`}
            >
              <div className="text-sky-400 font-bold">PORT (Odd) ↑</div>
              <div className="flex items-center gap-2">
                <span>← BOW</span>
                <Compass className="w-4 h-4 text-sky-400" />
                <span>AFT →</span>
              </div>
              <div className="text-emerald-400 font-bold">STARBOARD (Even) ↓</div>
            </div>

            {/* Inner Deck Schematic Corridors & Canonical Landmark Spine */}
            <div className="space-y-4 px-12 py-2">
              {/* Portside Corridor (Odd Cabins) */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-sky-400">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    Portside Corridor (Odd Cabin Numbers)
                  </span>
                  <span className="font-mono text-slate-500 text-[10px]">
                    {portSpaces.length} Spaces
                  </span>
                </div>

                <div className="flex items-center gap-1.5 overflow-x-visible">
                  {/* Curved Bow Port Section */}
                  {bowPort.length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-sky-950/20 border border-sky-500/20 rounded-xl">
                      {bowPort.map(renderCell)}
                    </div>
                  )}

                  {/* Forward Port Section */}
                  {fwdPort.length > 0 && (
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {fwdPort.map(renderCell)}
                    </div>
                  )}

                  {/* Midship Port Section */}
                  {midPort.length > 0 && (
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {midPort.map(renderCell)}
                    </div>
                  )}

                  {/* Aft Port Section */}
                  {aftPort.length > 0 && (
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {aftPort.map(renderCell)}
                    </div>
                  )}

                  {/* Stern Transom Port Section */}
                  {sternPort.length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-amber-950/20 border border-amber-500/20 rounded-xl">
                      {sternPort.map(renderCell)}
                    </div>
                  )}
                </div>
              </div>

              {/* Central Public Landmarks & Vertical Elevator Core Spine */}
              <div
                className={`rounded-2xl p-4 border grid grid-cols-5 gap-3 items-stretch min-h-[140px] ${
                  isNight ? "bg-slate-950/80 border-white/5" : "bg-slate-50 border-slate-200"
                }`}
              >
                {/* 1. Forward Zone / Venue Landmark */}
                <div
                  className={`rounded-xl p-3 border flex flex-col justify-between transition-all ${
                    isNight
                      ? "bg-amber-950/20 border-amber-500/20 hover:border-amber-400/40"
                      : "bg-amber-50 border-amber-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
                      {landmarks.fwd.type}
                    </span>
                    <Crown className="w-4 h-4 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-amber-300">{landmarks.fwd.title}</h3>
                    <p className="text-[10px] text-slate-400 font-mono">{landmarks.fwd.sub}</p>
                  </div>
                  <div className="text-[9px] font-mono text-slate-500 flex items-center gap-2">
                    <span>Bow Vista</span> • <span>Deck {level.level_index}</span>
                  </div>
                </div>

                {/* 2. Forward Lift Core A */}
                <div
                  className={`rounded-xl p-3 border flex flex-col justify-between ${
                    isNight ? "bg-blue-950/20 border-blue-500/20" : "bg-blue-50 border-blue-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                      {landmarks.midFwd.type}
                    </span>
                    <Layers className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-blue-300">{landmarks.midFwd.title}</h3>
                    <p className="text-[10px] text-slate-400 font-mono">{landmarks.midFwd.sub}</p>
                  </div>
                  <div className="text-[9px] font-mono text-emerald-400 font-semibold">
                    Vertical Core • Levels 4 — 19
                  </div>
                </div>

                {/* 3. Central Atrium / Promenade / Midship Panoramic Lifts */}
                <div
                  className={`rounded-xl p-3 border flex flex-col justify-between items-center text-center ${
                    isNight ? "bg-indigo-950/20 border-indigo-500/20" : "bg-indigo-50 border-indigo-200"
                  }`}
                >
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                    {landmarks.mid.type}
                  </span>
                  <div>
                    <h3 className="text-xs font-bold text-indigo-300">{landmarks.mid.title}</h3>
                    <p className="text-[10px] text-slate-400 font-mono">{landmarks.mid.sub}</p>
                  </div>
                  <div className="text-[9px] font-mono text-slate-500">
                    Panoramic Lift Overlook
                  </div>
                </div>

                {/* 4. Aft Lift Core B / Specialty Hub */}
                <div
                  className={`rounded-xl p-3 border flex flex-col justify-between ${
                    isNight ? "bg-blue-950/20 border-blue-500/20" : "bg-blue-50 border-blue-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                      {landmarks.midAft.type}
                    </span>
                    <Layers className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-blue-300">{landmarks.midAft.title}</h3>
                    <p className="text-[10px] text-slate-400 font-mono">{landmarks.midAft.sub}</p>
                  </div>
                  <div className="text-[9px] font-mono text-emerald-400 font-semibold">
                    Vertical Core • Levels 5 — 18
                  </div>
                </div>

                {/* 5. Aft Venue / Carousel Lounge / Stern Transom */}
                <div
                  className={`rounded-xl p-3 border flex flex-col justify-between transition-all ${
                    isNight
                      ? "bg-fuchsia-950/20 border-fuchsia-500/20 hover:border-fuchsia-400/40"
                      : "bg-fuchsia-50 border-fuchsia-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-fuchsia-500/20 text-fuchsia-400 border border-fuchsia-500/30">
                      {landmarks.aft.type}
                    </span>
                    <Film className="w-4 h-4 text-fuchsia-400" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-fuchsia-300">{landmarks.aft.title}</h3>
                    <p className="text-[10px] text-slate-400 font-mono">{landmarks.aft.sub}</p>
                  </div>
                  <div className="text-[9px] font-mono text-slate-500 flex items-center gap-2">
                    <span>Aft Wake Vista</span> • <span>Deck {level.level_index}</span>
                  </div>
                </div>
              </div>

              {/* Starboard Corridor (Even Cabins) */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-emerald-400">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    Starboard Corridor (Even Cabin Numbers)
                  </span>
                  <span className="font-mono text-slate-500 text-[10px]">
                    {starboardSpaces.length} Spaces
                  </span>
                </div>

                <div className="flex items-center gap-1.5 overflow-x-visible">
                  {/* Curved Bow Starboard Section */}
                  {bowStbd.length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-sky-950/20 border border-sky-500/20 rounded-xl">
                      {bowStbd.map(renderCell)}
                    </div>
                  )}

                  {/* Forward Starboard Section */}
                  {fwdStbd.length > 0 && (
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {fwdStbd.map(renderCell)}
                    </div>
                  )}

                  {/* Midship Starboard Section */}
                  {midStbd.length > 0 && (
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {midStbd.map(renderCell)}
                    </div>
                  )}

                  {/* Aft Starboard Section */}
                  {aftStbd.length > 0 && (
                    <div className="flex items-center gap-1 flex-1 justify-between">
                      {aftStbd.map(renderCell)}
                    </div>
                  )}

                  {/* Stern Transom Starboard Section */}
                  {sternStbd.length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-amber-950/20 border border-amber-500/20 rounded-xl">
                      {sternStbd.map(renderCell)}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Comprehensive Information Architecture Deck Card (From Image A) */}
      <div
        className={`p-6 border-t space-y-6 z-20 backdrop-blur-xl shrink-0 ${
          isNight ? "bg-slate-900/90 border-white/10" : "bg-white/95 border-slate-200"
        }`}
      >
        {/* Row A: Semantic Space Types, Epistemic State, Topology Elements Legends */}
        <div className="grid grid-cols-3 gap-6 text-xs pb-4 border-b border-white/5">
          {/* Space Types */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 font-mono block">
              Semantic Space Types
            </span>
            <div className="flex items-center gap-3 flex-wrap text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-indigo-500" />
                <span className="text-slate-300">Interior</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-sky-500" />
                <span className="text-slate-300">Ocean View</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500" />
                <span className="text-slate-300">Balcony</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-amber-500" />
                <span className="text-slate-300">Suite / Yacht Club</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-fuchsia-500" />
                <span className="text-slate-300">Venue / Dining</span>
              </div>
            </div>
          </div>

          {/* Epistemic State */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 font-mono block">
              Epistemic State (Knowledge)
            </span>
            <div className="flex items-center gap-3 flex-wrap text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-emerald-300 font-mono">Direct (Verified)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm border border-dashed border-sky-400 bg-sky-500/30" />
                <span className="text-sky-300 font-mono">Derived (Inferred)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm border border-dotted border-slate-500 opacity-60" />
                <span className="text-slate-400 font-mono">Unknown</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rotate-45 bg-amber-400" />
                <span className="text-amber-300 font-mono">Conflict</span>
              </div>
            </div>
          </div>

          {/* Topology Elements */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 font-mono block">
              Topology Elements
            </span>
            <div className="flex items-center gap-3 flex-wrap text-[11px] font-mono text-slate-300">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm border border-slate-600" />
                <span>Space (Cell)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-sky-400" />
                <span>Transition (Door)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Layers className="w-3 h-3 text-blue-400" />
                <span>Vertical Connection</span>
              </div>
            </div>
          </div>
        </div>

        {/* Row B: Deck Summary Counters */}
        <div className="space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 font-mono block">
            Deck Summary
          </span>
          <div className="grid grid-cols-6 gap-3">
            <div
              className={`p-3 rounded-2xl border ${
                isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
              }`}
            >
              <span className="text-[10px] text-slate-500 font-mono block">Total Spaces</span>
              <span className="text-lg font-bold font-mono text-white">{level.spaces_count}</span>
            </div>
            <div
              className={`p-3 rounded-2xl border ${
                isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
              }`}
            >
              <span className="text-[10px] text-slate-500 font-mono block">Direct (Verified)</span>
              <span className="text-lg font-bold font-mono text-emerald-400">
                {level.epistemic_breakdown.direct}
              </span>
            </div>
            <div
              className={`p-3 rounded-2xl border ${
                isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
              }`}
            >
              <span className="text-[10px] text-slate-500 font-mono block">Derived (Inferred)</span>
              <span className="text-lg font-bold font-mono text-sky-400">
                {level.epistemic_breakdown.derived}
              </span>
            </div>
            <div
              className={`p-3 rounded-2xl border ${
                isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
              }`}
            >
              <span className="text-[10px] text-slate-500 font-mono block">Unknown</span>
              <span className="text-lg font-bold font-mono text-slate-400">
                {level.epistemic_breakdown.unknown}
              </span>
            </div>
            <div
              className={`p-3 rounded-2xl border ${
                isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
              }`}
            >
              <span className="text-[10px] text-slate-500 font-mono block">Conflict</span>
              <span className="text-lg font-bold font-mono text-amber-400">
                {level.epistemic_breakdown.conflict}
              </span>
            </div>
            <div
              className={`p-3 rounded-2xl border ${
                isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
              }`}
            >
              <span className="text-[10px] text-slate-500 font-mono block">Epistemic Confidence</span>
              <span className="text-lg font-bold font-mono text-emerald-400">99%</span>
            </div>
          </div>
        </div>

        {/* Row C: Level Context, Primary Zones, Vertical Connections, Major Venues */}
        <div className="grid grid-cols-4 gap-4 text-xs">
          {/* Level Context Quick Jump */}
          <div
            className={`p-3.5 rounded-2xl border space-y-2 ${
              isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
            }`}
          >
            <span className="text-[10px] text-slate-500 uppercase font-mono font-semibold block">
              Level Context
            </span>
            <div className="flex items-center gap-2">
              {allLevels.slice(Math.max(0, level.level_index - 3), level.level_index + 2).map((lvl) => (
                <button
                  key={lvl.level_index}
                  onClick={() => onSelectLevel(lvl.level_index)}
                  className={`w-8 h-8 rounded-xl font-mono font-bold text-xs transition-all ${
                    lvl.level_index === level.level_index
                      ? "bg-sky-500 text-white shadow-lg shadow-sky-500/30 ring-2 ring-sky-400 font-extrabold"
                      : isNight
                      ? "bg-slate-800 text-slate-400 hover:bg-slate-700"
                      : "bg-slate-200 text-slate-700 hover:bg-slate-300"
                  }`}
                >
                  {lvl.level_index}
                </button>
              ))}
            </div>
          </div>

          {/* Primary Zones Selector */}
          <div
            className={`p-3.5 rounded-2xl border space-y-2 ${
              isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
            }`}
          >
            <span className="text-[10px] text-slate-500 uppercase font-mono font-semibold block">
              Primary Zones
            </span>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setActiveZone("FWD")}
                className={`px-2.5 py-1 rounded-xl text-[11px] font-semibold transition-all ${
                  activeZone === "FWD"
                    ? "bg-sky-500/20 text-sky-400 border border-sky-400/40"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Forward
              </button>
              <button
                onClick={() => setActiveZone("MID")}
                className={`px-2.5 py-1 rounded-xl text-[11px] font-semibold transition-all ${
                  activeZone === "MID"
                    ? "bg-sky-500/20 text-sky-400 border border-sky-400/40"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Midship
              </button>
              <button
                onClick={() => setActiveZone("AFT")}
                className={`px-2.5 py-1 rounded-xl text-[11px] font-semibold transition-all ${
                  activeZone === "AFT"
                    ? "bg-sky-500/20 text-sky-400 border border-sky-400/40"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Aft
              </button>
            </div>
          </div>

          {/* Vertical Connections */}
          <div
            className={`p-3.5 rounded-2xl border space-y-2 ${
              isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
            }`}
          >
            <span className="text-[10px] text-slate-500 uppercase font-mono font-semibold block">
              Vertical Connections
            </span>
            <div className="flex items-center gap-3 text-xs font-mono">
              <div className="flex items-center gap-1.5 text-blue-300">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                <span>Core A (Fwd)</span>
              </div>
              <div className="flex items-center gap-1.5 text-blue-300">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                <span>Core B (Aft)</span>
              </div>
            </div>
          </div>

          {/* Major Venues Landmark on this Level */}
          <div
            className={`p-3.5 rounded-2xl border space-y-2 ${
              isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
            }`}
          >
            <span className="text-[10px] text-slate-500 uppercase font-mono font-semibold block">
              Deck Landmark
            </span>
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-300 truncate">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span className="truncate">{landmarks.mid.title}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
