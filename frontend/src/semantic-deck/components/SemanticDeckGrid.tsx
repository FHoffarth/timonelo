import React, { useRef, useEffect } from "react";
import { SemanticLevel, SemanticEntity } from "../types";
import { getClassificationColorToken, getEpistemicPatternToken } from "../apiClient";
import { Accessibility, ShieldCheck, Calculator, HelpCircle, AlertTriangle } from "lucide-react";

interface SemanticDeckGridProps {
  level: SemanticLevel;
  selectedEntity: SemanticEntity | null;
  hoveredEntity: SemanticEntity | null;
  onSelectEntity: (entity: SemanticEntity) => void;
  onHoverEntity: (entity: SemanticEntity | null) => void;
}

export default function SemanticDeckGrid({
  level,
  selectedEntity,
  hoveredEntity,
  onSelectEntity,
  onHoverEntity,
}: SemanticDeckGridProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const selectedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to selected entity
  useEffect(() => {
    if (selectedRef.current) {
      selectedRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });
    }
  }, [selectedEntity?.id]);

  // Group entities into Port, Center, Starboard corridors
  const portSpaces = (level.spaces || []).filter((s) => s.side === "PORT");
  const centerSpaces = (level.spaces || []).filter((s) => s.side === "CENTER");
  const starboardSpaces = (level.spaces || []).filter((s) => s.side === "STARBOARD");

  const renderCell = (space: SemanticEntity) => {
    const isSelected = selectedEntity?.id === space.id;
    const isHovered = hoveredEntity?.id === space.id;

    // Check if this space is an immediate neighbor of the selected entity
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
        id={`semantic-cell-${space.id}`}
        onClick={() => onSelectEntity(space)}
        onMouseEnter={() => onHoverEntity(space)}
        onMouseLeave={() => onHoverEntity(null)}
        className={`relative group cursor-pointer transition-all duration-200 rounded-xl p-3 flex flex-col justify-between select-none min-h-[96px] w-full border ${
          colorToken.bg
        } ${patternToken.borderClass} ${
          isSelected
            ? "ring-2 ring-sky-400 shadow-xl shadow-sky-500/20 scale-[1.03] z-20"
            : isNeighbor
            ? "ring-1 ring-emerald-400/80 shadow-md shadow-emerald-500/10 scale-[1.01] z-10"
            : isHovered
            ? "scale-[1.02] shadow-lg z-10"
            : ""
        }`}
      >
        {/* Top Header: ID & Epistemic Indicator */}
        <div className="flex items-start justify-between gap-1">
          <div className="flex items-center gap-1.5">
            <span
              className={`font-mono font-bold text-sm tracking-tight ${
                isSelected ? "text-white" : colorToken.text
              }`}
            >
              {space.id}
            </span>
            {space.accessible && (
              <span
                className="px-1 py-0.2 rounded bg-sky-500/20 text-sky-300 text-[10px] font-bold"
                title="PRM Accessible Space"
              >
                H
              </span>
            )}
          </div>

          {/* Epistemic State Glyph */}
          <div className="flex items-center">
            {space.epistemic_state === "DIRECT" && (
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm" title="Direct Evidentiary Proof" />
            )}
            {space.epistemic_state === "DERIVED" && (
              <span className="w-2 h-2 rounded-sm border border-sky-400 bg-sky-500/40" title="Derived Deterministic" />
            )}
            {space.epistemic_state === "UNKNOWN" && (
              <span className="w-2 h-2 rounded-full border border-dashed border-slate-500 text-[8px] flex items-center justify-center text-slate-400">
                ?
              </span>
            )}
            {space.epistemic_state === "CONFLICT" && (
              <span className="w-2 h-2 rotate-45 bg-amber-400" title="Conflict Recorded" />
            )}
          </div>
        </div>

        {/* Middle: Classification Label */}
        <div className="my-1">
          <div className="text-[11px] font-medium text-slate-200 truncate leading-tight">
            {space.classification_label}
          </div>
          <div className="text-[10px] text-slate-400 font-mono">
            {space.zone.replace("_", " ")}
          </div>
        </div>

        {/* Bottom Bar: Sequence and Artifact Count */}
        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-white/5 font-mono">
          <span>Seq #{space.sequence_order}</span>
          {space.evidence_links && space.evidence_links.length > 0 && (
            <span className="text-slate-400">
              {space.evidence_links[0].artifact_id?.split("-")[0] || "NO-ARTIFACT"}
            </span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div
      ref={containerRef}
      className="relative flex-1 h-full overflow-y-auto overflow-x-auto p-8 bg-slate-950 no-scrollbar select-none"
    >
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Level Header & Epistemic Overview */}
        <div className="flex items-center justify-between p-6 bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-3xl">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="px-3 py-1 rounded-xl bg-sky-500/20 text-sky-300 font-mono font-bold text-xs border border-sky-400/30">
                LEVEL {level.level_index}
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                {level.level_name}
              </h2>
            </div>
            <p className="text-xs text-slate-400">
              Canonical Schematic View • {level.spaces_count} Verified Semantic Spaces • Uniform Cell Geometry
            </p>
          </div>

          <div className="flex items-center gap-6 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
              <span>{level.epistemic_breakdown.direct} Direct</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-sm border border-sky-400 bg-sky-500/30" />
              <span>{level.epistemic_breakdown.derived} Derived</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full border border-dashed border-slate-500" />
              <span>{level.epistemic_breakdown.unknown} Unknown</span>
            </div>
          </div>
        </div>

        {/* Schematic Corridors (Port, Center, Starboard) */}
        <div className="space-y-6">
          {/* 1. Portside Spaces */}
          {portSpaces.length > 0 && (
            <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-2 text-sky-400">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  Portside Corridor
                </span>
                <span className="font-mono text-slate-500">{portSpaces.length} Spaces</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {portSpaces.map(renderCell)}
              </div>
            </div>
          )}

          {/* 2. Central Interior & Public Promenade */}
          {centerSpaces.length > 0 && (
            <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-2 text-indigo-400">
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  Central Residential & Public Promenade
                </span>
                <span className="font-mono text-slate-500">{centerSpaces.length} Spaces</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {centerSpaces.map(renderCell)}
              </div>
            </div>
          )}

          {/* 3. Starboard Spaces */}
          {starboardSpaces.length > 0 && (
            <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-2 text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  Starboard Corridor
                </span>
                <span className="font-mono text-slate-500">{starboardSpaces.length} Spaces</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {starboardSpaces.map(renderCell)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
