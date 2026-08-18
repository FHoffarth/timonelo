import React from "react";
import { VesselKnowledgeGraph } from "../types";
import { Ship, ChevronDown } from "lucide-react";

import { knowledgeRepository } from "../../knowledge";

interface DeckNavigationStackProps {
  currentVessel: VesselKnowledgeGraph;
  activeDeckLevel: number;
  onSelectVessel: (vesselId: string) => void;
  onSelectDeck: (deckLevel: number) => void;
}

export default function DeckNavigationStack({
  currentVessel,
  activeDeckLevel,
  onSelectVessel,
  onSelectDeck,
}: DeckNavigationStackProps) {
  const bellissima = knowledgeRepository.getShip("msc-bellissima");
  const registeredVessels = [
    { id: bellissima.vessel_id, name: bellissima.vessel_name, class: bellissima.technical_specifications.class },
    { id: "ms-andorinha", name: "MS Andorinha", class: "Douro River Custom Class" },
  ];

  return (
    <div className="w-64 h-full bg-slate-900/80 backdrop-blur-2xl border-r border-white/10 flex flex-col justify-between p-4 select-none z-30">
      <div className="space-y-4">
        {/* Vessel Selector Dropdown */}
        <div className="p-3 bg-slate-950/60 rounded-2xl border border-white/5 space-y-2">
          <div className="flex items-center justify-between text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
            <span>Canonical Model</span>
            <span className="text-emerald-400 font-mono">W3C Graph</span>
          </div>

          <div className="relative">
            <select
              value={currentVessel.vessel_id}
              onChange={(e) => onSelectVessel(e.target.value)}
              className="w-full appearance-none bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-sky-400 cursor-pointer pr-8"
            >
              {registeredVessels.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.class})
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-2.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          </div>

          <div className="text-[11px] text-slate-400 font-mono">
            {currentVessel.operator} • {currentVessel.epistemic_summary.total_entities} Spaces
          </div>
        </div>

        {/* Vertical Elevator Level Stack */}
        <div className="space-y-1.5">
          <div className="px-2 py-1 flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            <span>Storey Levels (BOT)</span>
            <span className="text-sky-400 font-mono text-[10px]">
              {(currentVessel.levels || []).length} Levels
            </span>
          </div>

          <div className="space-y-1 max-h-[calc(100vh-340px)] overflow-y-auto no-scrollbar">
            {(currentVessel.levels || []).map((level) => {
              const isActive = level.level_index === activeDeckLevel;

              return (
                <button
                  key={level.level_index}
                  onClick={() => onSelectDeck(level.level_index)}
                  className={`w-full px-3 py-2.5 rounded-2xl text-left transition-all duration-200 flex items-center justify-between group ${
                    isActive
                      ? "bg-gradient-to-r from-sky-500/20 to-blue-600/30 border border-sky-400/40 text-white shadow-lg shadow-sky-500/20"
                      : "text-slate-300 hover:bg-white/5 hover:text-white border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <div
                      className={`w-7 h-7 rounded-xl flex items-center justify-center font-mono font-bold text-xs ${
                        isActive
                          ? "bg-sky-400 text-slate-950 shadow-md"
                          : "bg-slate-800 text-slate-300 group-hover:bg-slate-700"
                      }`}
                    >
                      {level.level_index}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold truncate leading-tight">
                        {level.level_name}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {level.spaces_count} Verified Spaces
                      </span>
                    </div>
                  </div>

                  {isActive && (
                    <div className="w-2 h-2 rounded-full bg-sky-400 animate-pulse shadow-sm" />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Epistemic Summary Telemetry Card */}
      <div className="p-3 bg-slate-950/80 rounded-2xl border border-white/5 space-y-1.5 text-xs font-mono">
        <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase font-bold">
          <span>Truth Grounding</span>
          <span className="text-emerald-400 font-semibold">
            {(currentVessel.epistemic_summary.mean_confidence * 100).toFixed(0)}% Verified
          </span>
        </div>
        <div className="grid grid-cols-2 gap-1.5 text-[10px]">
          <div className="p-1.5 bg-slate-900 rounded-lg text-slate-300">
            <span className="text-slate-500 block">Direct</span>
            <span className="font-bold text-emerald-400">
              {currentVessel.epistemic_summary.direct_evidence_count}
            </span>
          </div>
          <div className="p-1.5 bg-slate-900 rounded-lg text-slate-300">
            <span className="text-slate-500 block">Derived</span>
            <span className="font-bold text-sky-400">
              {currentVessel.epistemic_summary.derived_count}
            </span>
          </div>
          <div className="p-1.5 bg-slate-900 rounded-lg text-slate-300">
            <span className="text-slate-500 block">Unknown</span>
            <span className="font-bold text-slate-400">
              {currentVessel.epistemic_summary.unknown_count}
            </span>
          </div>
          <div className="p-1.5 bg-slate-900 rounded-lg text-slate-300">
            <span className="text-slate-500 block">Conflicts</span>
            <span className="font-bold text-amber-400">
              {currentVessel.epistemic_summary.conflict_count}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
