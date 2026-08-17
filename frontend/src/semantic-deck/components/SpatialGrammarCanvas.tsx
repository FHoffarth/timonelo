import React, { useRef, useState, useEffect, useMemo } from "react";
import { SemanticLevel, SemanticEntity } from "../types";
import { buildDeckSpatialGrammar, StructuralZoneBlock } from "../spatialGrammar";
import { getClassificationColorToken, getEpistemicPatternToken } from "../apiClient";
import { useTheme } from "../themeContext";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Compass,
  Layers,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Calculator,
  HelpCircle,
  AlertTriangle,
  Crown,
  Waves,
  Utensils,
  Film,
} from "lucide-react";

interface SpatialGrammarCanvasProps {
  level: SemanticLevel;
  selectedEntity: SemanticEntity | null;
  hoveredEntity: SemanticEntity | null;
  allLevels: SemanticLevel[];
  onSelectLevel: (levelIndex: number) => void;
  onSelectEntity: (entity: SemanticEntity) => void;
  onHoverEntity: (entity: SemanticEntity | null) => void;
}

export default function SpatialGrammarCanvas({
  level,
  selectedEntity,
  hoveredEntity,
  allLevels,
  onSelectLevel,
  onSelectEntity,
  onHoverEntity,
}: SpatialGrammarCanvasProps) {
  const { theme } = useTheme();
  const isNight = theme === "night";

  const [zoom, setZoom] = useState(1);
  const [activeZoneId, setActiveZoneId] = useState<string>("ALL");

  const grammarModel = useMemo(() => buildDeckSpatialGrammar(level), [level]);
  const selectedCellRef = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to selected cabin
  useEffect(() => {
    if (selectedCellRef.current && viewportRef.current) {
      selectedCellRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });
    }
  }, [selectedEntity?.id]);

  const renderCell = (space: SemanticEntity) => {
    const isSelected = selectedEntity?.id === space.id;
    const isHovered = hoveredEntity?.id === space.id;

    // Adjacency check
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
        ref={isSelected ? selectedCellRef : null}
        id={`grammar-cell-${space.id}`}
        onClick={() => onSelectEntity(space)}
        onMouseEnter={() => onHoverEntity(space)}
        onMouseLeave={() => onHoverEntity(null)}
        className={`relative group cursor-pointer transition-all duration-150 rounded-lg p-1.5 flex flex-col justify-between select-none min-w-[52px] max-w-[58px] h-[72px] border ${
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
        {/* Selection pointer arrow */}
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

        {/* Middle: PRM badge or classification abbreviation */}
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
      {/* 1. Header Bar: Level & Epistemic Telemetry */}
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
              Spatial Grammar Model • 4 Parallel Topological Tracks • Uniform Cell Geometry
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

      {/* 2. Master Spatial Grammar Diagram Canvas */}
      <div
        ref={viewportRef}
        className="relative flex-1 p-8 flex items-center justify-center overflow-x-auto overflow-y-auto no-scrollbar min-h-[460px]"
      >
        <div
          style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
          className="relative transition-transform duration-150 ease-out py-4"
        >
          {/* Recognizable Hull Envelope */}
          <div
            className={`relative rounded-[110px_45px_45px_110px] border-2 p-8 shadow-2xl backdrop-blur-2xl transition-all duration-300 min-w-[1380px] max-w-[1680px] ${
              isNight
                ? "bg-slate-900/80 border-slate-700/80 shadow-black/80 ring-1 ring-white/5"
                : "bg-white/95 border-slate-300 shadow-slate-300/60 ring-1 ring-black/5"
            }`}
          >
            {/* Outer Bow / Stern Orientation */}
            <div className="absolute left-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-1 text-slate-500 font-mono text-[10px] uppercase font-bold tracking-widest pointer-events-none">
              <span>BOW</span>
              <span className="w-1.5 h-6 bg-sky-500/50 rounded-full" />
              <span>FWD</span>
            </div>

            <div className="absolute right-6 top-1/2 -translate-y-1/2 flex flex-col items-center gap-1 text-slate-500 font-mono text-[10px] uppercase font-bold tracking-widest pointer-events-none">
              <span>AFT</span>
              <span className="w-1.5 h-6 bg-emerald-500/50 rounded-full" />
              <span>STERN</span>
            </div>

            {/* Compass Rose */}
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

            {/* The 4 Topological Tracks wrapped around the Structural Skeleton */}
            <div className="space-y-3 px-12 py-2">
              {/* TRACK 1: PORT OUTER TRACK (Balcony / Ocean View) */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono text-sky-400 font-semibold uppercase">
                  <span>Track 1: Port Outer Track (Balconies & Ocean Views)</span>
                  <span className="text-slate-500">{grammarModel.tracksSummary.portOuterCount} Cabins</span>
                </div>

                <div className="flex items-center gap-3">
                  {/* Bow Cap */}
                  {grammarModel.bowWedgeCap.slice(0, 2).length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-sky-950/30 border border-sky-500/30 rounded-xl">
                      {grammarModel.bowWedgeCap.slice(0, 2).map(renderCell)}
                    </div>
                  )}

                  {/* Sequential Runs separated by Structural Cores */}
                  {grammarModel.zoneBlocks.map((block, idx) => {
                    if (block.isStructuralCore) {
                      return (
                        <div
                          key={idx}
                          className="w-12 h-16 rounded-xl border border-dashed border-blue-500/40 bg-blue-950/20 flex flex-col items-center justify-center text-[9px] font-mono text-blue-400 shrink-0"
                          title={block.title}
                        >
                          <Layers className="w-3.5 h-3.5 mb-0.5" />
                          <span>Core</span>
                        </div>
                      );
                    }
                    return (
                      <div key={idx} className="flex items-center gap-1 flex-1 justify-between">
                        {block.portOuterTrack.map(renderCell)}
                      </div>
                    );
                  })}

                  {/* Stern Cap */}
                  {grammarModel.sternTransomCap.slice(0, 2).length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-amber-950/30 border border-amber-500/30 rounded-xl">
                      {grammarModel.sternTransomCap.slice(0, 2).map(renderCell)}
                    </div>
                  )}
                </div>
              </div>

              {/* TRACK 2: PORT INNER TRACK (Interior Staterooms facing Port Corridor) */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono text-indigo-400 font-semibold uppercase">
                  <span>Track 2: Port Inner Track (Interior Hallway)</span>
                  <span className="text-slate-500">{grammarModel.tracksSummary.portInnerCount} Cabins</span>
                </div>

                <div className="flex items-center gap-3">
                  {grammarModel.zoneBlocks.map((block, idx) => {
                    if (block.isStructuralCore) {
                      return (
                        <div
                          key={idx}
                          className="w-12 h-16 rounded-xl border border-dashed border-blue-500/40 bg-blue-950/20 flex flex-col items-center justify-center text-[9px] font-mono text-blue-400 shrink-0"
                        >
                          <span className="font-bold text-[10px]">{block.zoneId === "LIFT_CORE_A" ? "A" : "B"}</span>
                        </div>
                      );
                    }
                    return (
                      <div key={idx} className="flex items-center gap-1 flex-1 justify-between">
                        {block.portInnerTrack.map(renderCell)}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* CENTRAL STRUCTURAL SKELETON SPINE (Elevator Cores, Atrium Voids, Service Lockers) */}
              <div
                className={`rounded-2xl p-3.5 border grid grid-cols-5 gap-3 items-stretch min-h-[110px] ${
                  isNight ? "bg-slate-950/90 border-white/10" : "bg-slate-100 border-slate-300"
                }`}
              >
                {/* 1. Forward Bow Wedge */}
                <div className="rounded-xl p-2.5 bg-sky-950/20 border border-sky-500/20 flex flex-col justify-between">
                  <span className="text-[8.5px] font-mono uppercase font-bold text-sky-400">BOW WEDGE</span>
                  <div className="text-xs font-bold text-sky-300">Forward Residential Cap</div>
                  <div className="text-[9px] font-mono text-slate-500">Dual Transverse Hallways</div>
                </div>

                {/* 2. Forward Lift Core A */}
                <div className="rounded-xl p-2.5 bg-blue-950/30 border border-blue-500/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-[8.5px] font-mono uppercase font-bold text-blue-400">LIFT CORE A</span>
                    <Layers className="w-3.5 h-3.5 text-blue-400" />
                  </div>
                  <div className="text-xs font-bold text-blue-300">6 Panoramic Elevators + Stairs</div>
                  <div className="text-[9px] font-mono text-emerald-400">Connects Decks 4 — 19</div>
                </div>

                {/* 3. Midship Atrium / Galleria Void */}
                <div className="rounded-xl p-2.5 bg-indigo-950/20 border border-indigo-500/20 flex flex-col justify-between items-center text-center">
                  <span className="text-[8.5px] font-mono uppercase font-bold text-indigo-400">MIDSHIP VOID</span>
                  <div className="text-xs font-bold text-indigo-300">Open Galleria & Panoramic Lift Core</div>
                  <div className="text-[9px] font-mono text-slate-500">Central Spatial Anchor</div>
                </div>

                {/* 4. Aft Lift Core B */}
                <div className="rounded-xl p-2.5 bg-blue-950/30 border border-blue-500/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-[8.5px] font-mono uppercase font-bold text-blue-400">LIFT CORE B</span>
                    <Layers className="w-3.5 h-3.5 text-blue-400" />
                  </div>
                  <div className="text-xs font-bold text-blue-300">4 Aft Elevators + Service Risers</div>
                  <div className="text-[9px] font-mono text-emerald-400">Connects Decks 5 — 18</div>
                </div>

                {/* 5. Stern Transom Cap */}
                <div className="rounded-xl p-2.5 bg-amber-950/20 border border-amber-500/20 flex flex-col justify-between">
                  <span className="text-[8.5px] font-mono uppercase font-bold text-amber-400">STERN TRANSOM</span>
                  <div className="text-xs font-bold text-amber-300">Aft Wake Balconies & Suites</div>
                  <div className="text-[9px] font-mono text-slate-500">Scenic Aft Panorama</div>
                </div>
              </div>

              {/* TRACK 3: STARBOARD INNER TRACK (Interior Staterooms facing Starboard Corridor) */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono text-indigo-400 font-semibold uppercase">
                  <span>Track 3: Starboard Inner Track (Interior Hallway)</span>
                  <span className="text-slate-500">{grammarModel.tracksSummary.starboardInnerCount} Cabins</span>
                </div>

                <div className="flex items-center gap-3">
                  {grammarModel.zoneBlocks.map((block, idx) => {
                    if (block.isStructuralCore) {
                      return (
                        <div
                          key={idx}
                          className="w-12 h-16 rounded-xl border border-dashed border-blue-500/40 bg-blue-950/20 flex flex-col items-center justify-center text-[9px] font-mono text-blue-400 shrink-0"
                        >
                          <span className="font-bold text-[10px]">{block.zoneId === "LIFT_CORE_A" ? "A" : "B"}</span>
                        </div>
                      );
                    }
                    return (
                      <div key={idx} className="flex items-center gap-1 flex-1 justify-between">
                        {block.starboardInnerTrack.map(renderCell)}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* TRACK 4: STARBOARD OUTER TRACK (Balcony / Ocean View) */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono text-emerald-400 font-semibold uppercase">
                  <span>Track 4: Starboard Outer Track (Balconies & Ocean Views)</span>
                  <span className="text-slate-500">{grammarModel.tracksSummary.starboardOuterCount} Cabins</span>
                </div>

                <div className="flex items-center gap-3">
                  {/* Bow Cap */}
                  {grammarModel.bowWedgeCap.slice(2, 4).length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-sky-950/30 border border-sky-500/30 rounded-xl">
                      {grammarModel.bowWedgeCap.slice(2, 4).map(renderCell)}
                    </div>
                  )}

                  {/* Sequential Runs separated by Structural Cores */}
                  {grammarModel.zoneBlocks.map((block, idx) => {
                    if (block.isStructuralCore) {
                      return (
                        <div
                          key={idx}
                          className="w-12 h-16 rounded-xl border border-dashed border-blue-500/40 bg-blue-950/20 flex flex-col items-center justify-center text-[9px] font-mono text-blue-400 shrink-0"
                          title={block.title}
                        >
                          <Layers className="w-3.5 h-3.5 mb-0.5" />
                          <span>Core</span>
                        </div>
                      );
                    }
                    return (
                      <div key={idx} className="flex items-center gap-1 flex-1 justify-between">
                        {block.starboardOuterTrack.map(renderCell)}
                      </div>
                    );
                  })}

                  {/* Stern Cap */}
                  {grammarModel.sternTransomCap.slice(2, 4).length > 0 && (
                    <div className="flex items-center gap-1 p-1 bg-amber-950/30 border border-amber-500/30 rounded-xl">
                      {grammarModel.sternTransomCap.slice(2, 4).map(renderCell)}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Bottom Information Architecture Summary Bar */}
      <div
        className={`p-6 border-t space-y-6 z-20 backdrop-blur-xl shrink-0 ${
          isNight ? "bg-slate-900/90 border-white/10" : "bg-white/95 border-slate-200"
        }`}
      >
        {/* Row A: Semantic Space Types & Epistemic Legends */}
        <div className="grid grid-cols-3 gap-6 text-xs pb-4 border-b border-white/5">
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 font-mono block">
              Semantic Space Types
            </span>
            <div className="flex items-center gap-3 flex-wrap text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-indigo-500" />
                <span className="text-slate-300">Interior (Track 2 & 3)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-sky-500" />
                <span className="text-slate-300">Ocean View</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-emerald-500" />
                <span className="text-slate-300">Balcony (Track 1 & 4)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-amber-500" />
                <span className="text-slate-300">Suite / Yacht Club</span>
              </div>
            </div>
          </div>

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
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 font-mono block">
              Spatial Grammar Structure
            </span>
            <div className="flex items-center gap-3 flex-wrap text-[11px] font-mono text-slate-300">
              <div className="flex items-center gap-1.5">
                <Layers className="w-3 h-3 text-blue-400" />
                <span>4 Parallel Tracks</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Sparkles className="w-3 h-3 text-indigo-400" />
                <span>Structural Lift Cores</span>
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

        {/* Row C: Level Context Quick Jump */}
        <div className="grid grid-cols-4 gap-4 text-xs">
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

          <div
            className={`p-3.5 rounded-2xl border space-y-2 ${
              isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
            }`}
          >
            <span className="text-[10px] text-slate-500 uppercase font-mono font-semibold block">
              Primary Runs
            </span>
            <div className="flex items-center gap-1.5">
              <span className="px-2 py-1 bg-sky-500/20 text-sky-400 rounded-lg text-[11px] font-semibold">
                Forward Quarter
              </span>
              <span className="px-2 py-1 bg-sky-500/20 text-sky-400 rounded-lg text-[11px] font-semibold">
                Midship Spine
              </span>
              <span className="px-2 py-1 bg-sky-500/20 text-sky-400 rounded-lg text-[11px] font-semibold">
                Aft Transom
              </span>
            </div>
          </div>

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
                <span>Lift Core A</span>
              </div>
              <div className="flex items-center gap-1.5 text-blue-300">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                <span>Lift Core B</span>
              </div>
            </div>
          </div>

          <div
            className={`p-3.5 rounded-2xl border space-y-2 ${
              isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
            }`}
          >
            <span className="text-[10px] text-slate-500 uppercase font-mono font-semibold block">
              Orientation Grammar
            </span>
            <div className="text-xs font-mono text-emerald-300 flex items-center gap-2">
              <Compass className="w-3.5 h-3.5 text-emerald-400" />
              <span>Bow (Left) $\rightarrow$ Stern (Right)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
