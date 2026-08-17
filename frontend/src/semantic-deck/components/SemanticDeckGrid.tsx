import React, { useRef, useEffect } from "react";
import { SemanticDeck, SemanticObject } from "../types";
import { getCategoryStyle, getEpistemicStyle } from "../semanticEngine";
import { Accessibility, ShieldCheck, Calculator, HelpCircle, AlertTriangle, Sparkles, Navigation2 } from "lucide-react";

interface SemanticDeckGridProps {
  deck: SemanticDeck;
  selectedObject: SemanticObject | null;
  hoveredObject: SemanticObject | null;
  onSelectObject: (obj: SemanticObject) => void;
  onHoverObject: (obj: SemanticObject | null) => void;
}

export default function SemanticDeckGrid({
  deck,
  selectedObject,
  hoveredObject,
  onSelectObject,
  onHoverObject,
}: SemanticDeckGridProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const selectedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to selected object
  useEffect(() => {
    if (selectedRef.current) {
      selectedRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
        inline: "center",
      });
    }
  }, [selectedObject?.id]);

  // Group objects into Port, Center, Starboard corridors
  const portObjects = deck.objects.filter((o) => o.side === "PORT");
  const centerObjects = deck.objects.filter((o) => o.side === "CENTER");
  const starboardObjects = deck.objects.filter((o) => o.side === "STARBOARD");

  const renderCell = (obj: SemanticObject) => {
    const isSelected = selectedObject?.id === obj.id;
    const isHovered = hoveredObject?.id === obj.id;

    // Check if this object is a neighbor of the selected object
    const isNeighbor =
      selectedObject &&
      selectedObject.deck === obj.deck &&
      (selectedObject.known_relations.neighbor_fore === obj.id ||
        selectedObject.known_relations.neighbor_aft === obj.id ||
        selectedObject.known_relations.across_corridor === obj.id);

    const catStyle = getCategoryStyle(obj.category);
    const epiStyle = getEpistemicStyle(obj.epistemic_state);

    return (
      <div
        key={obj.id}
        ref={isSelected ? selectedRef : null}
        id={`semantic-cell-${obj.id}`}
        onClick={() => onSelectObject(obj)}
        onMouseEnter={() => onHoverObject(obj)}
        onMouseLeave={() => onHoverObject(null)}
        className={`relative group cursor-pointer transition-all duration-200 rounded-xl p-3 flex flex-col justify-between select-none min-h-[92px] w-full border ${
          catStyle.bg
        } ${epiStyle.borderClass} ${
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
                isSelected ? "text-white" : catStyle.text
              }`}
            >
              {obj.id}
            </span>
            {obj.accessible && (
              <span
                className="px-1 py-0.2 rounded bg-sky-500/20 text-sky-300 text-[10px] font-bold"
                title="PRM Accessible Stateroom"
              >
                H
              </span>
            )}
          </div>

          {/* Epistemic State Glyph */}
          <div className="flex items-center">
            {obj.epistemic_state === "DIRECT" && (
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm" title="Direct Evidentiary Proof" />
            )}
            {obj.epistemic_state === "DERIVED" && (
              <span className="w-2 h-2 rounded-sm border border-sky-400 bg-sky-500/40" title="Derived Deterministic" />
            )}
            {obj.epistemic_state === "UNKNOWN" && (
              <span className="w-2 h-2 rounded-full border border-dashed border-slate-500 text-[8px] flex items-center justify-center text-slate-400">
                ?
              </span>
            )}
            {obj.epistemic_state === "CONFLICT" && (
              <span className="w-2 h-2 rotate-45 bg-amber-400" title="Conflict Recorded" />
            )}
          </div>
        </div>

        {/* Middle: Category Label */}
        <div className="my-1">
          <div className="text-[11px] font-medium text-slate-300 truncate leading-tight">
            {obj.category_label}
          </div>
          <div className="text-[10px] text-slate-500 font-mono">
            {obj.zone.replace("_", " ")}
          </div>
        </div>

        {/* Bottom Bar: Known Relation indicator */}
        <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-white/5 font-mono">
          <span>Seq #{obj.sequence_index}</span>
          {obj.evidence_links.length > 0 && (
            <span className="text-slate-500">
              {obj.evidence_links[0].artifact_id.split("-")[0]}
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
        {/* Deck Header & Topological Overview */}
        <div className="flex items-center justify-between p-6 bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-3xl">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="px-3 py-1 rounded-xl bg-sky-500/20 text-sky-300 font-mono font-bold text-xs border border-sky-400/30">
                DECK LEVEL {deck.deck_level}
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                {deck.deck_name}
              </h2>
            </div>
            <p className="text-xs text-slate-400">
              Schematic Topological View • {deck.objects.length} Verified Semantic Objects • Uniform Cell Geometry
            </p>
          </div>

          <div className="flex items-center gap-6 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
              <span>
                {deck.objects.filter((o) => o.epistemic_state === "DIRECT").length} Direct
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-sm border border-sky-400 bg-sky-500/30" />
              <span>
                {deck.objects.filter((o) => o.epistemic_state === "DERIVED").length} Derived
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full border border-dashed border-slate-500" />
              <span>
                {deck.objects.filter((o) => o.epistemic_state === "UNKNOWN").length} Unknown
              </span>
            </div>
          </div>
        </div>

        {/* Schematic Corridors (Port, Center, Starboard) */}
        <div className="space-y-6">
          {/* 1. Portside Corridor */}
          {portObjects.length > 0 && (
            <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-2 text-sky-400">
                  <span className="w-2 h-2 rounded-full bg-red-500" />
                  Portside Corridor (Odd Staterooms)
                </span>
                <span className="font-mono text-slate-500">{portObjects.length} Staterooms</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {portObjects.map(renderCell)}
              </div>
            </div>
          )}

          {/* 2. Central Interior & Public Corridor */}
          {centerObjects.length > 0 && (
            <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-2 text-indigo-400">
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  Central Residential & Public Promenade
                </span>
                <span className="font-mono text-slate-500">{centerObjects.length} Objects</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {centerObjects.map(renderCell)}
              </div>
            </div>
          )}

          {/* 3. Starboard Corridor */}
          {starboardObjects.length > 0 && (
            <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5 space-y-3">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-2 text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                  Starboard Corridor (Even Staterooms)
                </span>
                <span className="font-mono text-slate-500">{starboardObjects.length} Staterooms</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                {starboardObjects.map(renderCell)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
