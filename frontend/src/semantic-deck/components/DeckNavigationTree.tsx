import React from "react";
import { VesselKnowledgeGraph } from "../types";
import { useTheme } from "../themeContext";
import {
  Ship,
  ChevronDown,
  Layers,
  ShieldCheck,
  FileText,
  Workflow,
  Sparkles,
} from "lucide-react";

interface DeckNavigationTreeProps {
  currentVessel: VesselKnowledgeGraph;
  activeDeckLevel: number;
  onSelectVessel: (vesselId: string) => void;
  onSelectDeck: (deckLevel: number) => void;
  onOpenEvidenceExplorer?: () => void;
}

export default function DeckNavigationTree({
  currentVessel,
  activeDeckLevel,
  onSelectVessel,
  onSelectDeck,
  onOpenEvidenceExplorer,
}: DeckNavigationTreeProps) {
  const { theme } = useTheme();
  const isNight = theme === "night";

  const registeredVessels = [
    { id: "msc-bellissima", name: "MSC Bellissima", class: "Meraviglia Class", operator: "MSC Cruises" },
    { id: "ms-andorinha", name: "MS Andorinha", class: "Douro River Class", operator: "Tauck River" },
  ];

  return (
    <div
      className={`w-72 h-full border-r flex flex-col justify-between p-4 select-none z-30 transition-colors duration-200 ${
        isNight ? "bg-slate-900/90 border-white/10 text-slate-300" : "bg-white/95 border-slate-200 text-slate-700"
      }`}
    >
      <div className="space-y-4">
        {/* Canonical Model Selector */}
        <div
          className={`p-3 rounded-2xl border space-y-2 ${
            isNight ? "bg-slate-950/70 border-white/5" : "bg-slate-50 border-slate-200"
          }`}
        >
          <div className="flex items-center justify-between text-[10px] font-semibold uppercase tracking-wider text-slate-500 font-mono">
            <span>Canonical Model</span>
            <span className="text-emerald-400 font-mono">W3C Graph</span>
          </div>

          <div className="relative">
            <select
              value={currentVessel.vessel_id}
              onChange={(e) => onSelectVessel(e.target.value)}
              className={`w-full appearance-none rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:border-sky-400 cursor-pointer pr-8 border transition-colors ${
                isNight
                  ? "bg-slate-900 border-white/10 text-white"
                  : "bg-white border-slate-200 text-slate-900"
              }`}
            >
              {registeredVessels.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.class})
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-2.5 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
          </div>

          <div className="text-[11px] text-slate-400 font-mono flex items-center justify-between">
            <span>{currentVessel.operator}</span>
            <span>{currentVessel.epistemic_summary.total_entities} Semantic Spaces</span>
          </div>
        </div>

        {/* Storey Levels (BOT) Tree */}
        <div className="space-y-1.5">
          <div className="px-2 py-1 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-slate-400 font-mono">
            <span>Storey Levels (BOT)</span>
            <span className="text-sky-400 text-[10px] font-mono">
              {(currentVessel.levels || []).length} Levels
            </span>
          </div>

          <div className="space-y-1 max-h-[calc(100vh-370px)] overflow-y-auto no-scrollbar">
            {(currentVessel.levels || []).map((level) => {
              const isActive = level.level_index === activeDeckLevel;

              return (
                <button
                  key={level.level_index}
                  onClick={() => onSelectDeck(level.level_index)}
                  className={`w-full px-3 py-2 rounded-2xl text-left transition-all duration-150 flex items-center justify-between group ${
                    isActive
                      ? isNight
                        ? "bg-gradient-to-r from-sky-500/20 to-blue-600/30 border border-sky-400/50 text-white shadow-lg shadow-sky-500/20"
                        : "bg-sky-50 border border-sky-400 text-sky-900 shadow-sm"
                      : isNight
                      ? "text-slate-300 hover:bg-white/5 hover:text-white border border-transparent"
                      : "text-slate-700 hover:bg-slate-100 hover:text-slate-900 border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <div
                      className={`w-7 h-7 rounded-xl flex items-center justify-center font-mono font-bold text-xs ${
                        isActive
                          ? "bg-sky-400 text-slate-950 shadow-md font-extrabold"
                          : isNight
                          ? "bg-slate-800 text-slate-300 group-hover:bg-slate-700"
                          : "bg-slate-200 text-slate-700 group-hover:bg-slate-300"
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

      {/* Truth Grounding Telemetry Card */}
      <div
        className={`p-3.5 rounded-2xl border space-y-2 text-xs font-mono ${
          isNight ? "bg-slate-950/80 border-white/5" : "bg-slate-50 border-slate-200"
        }`}
      >
        <div className="flex items-center justify-between text-[10px] uppercase font-bold text-slate-400">
          <span>Truth Grounding</span>
          <span className="text-emerald-400 font-semibold">
            {(currentVessel.epistemic_summary.mean_confidence * 100).toFixed(0)}% Verified
          </span>
        </div>

        <div className="grid grid-cols-2 gap-1.5 text-[10px]">
          <div className={`p-1.5 rounded-lg ${isNight ? "bg-slate-900" : "bg-white border border-slate-200"}`}>
            <span className="text-slate-500 block text-[9px]">Direct</span>
            <span className="font-bold text-emerald-400 text-xs">
              {currentVessel.epistemic_summary.direct_evidence_count}
            </span>
          </div>
          <div className={`p-1.5 rounded-lg ${isNight ? "bg-slate-900" : "bg-white border border-slate-200"}`}>
            <span className="text-slate-500 block text-[9px]">Derived</span>
            <span className="font-bold text-sky-400 text-xs">
              {currentVessel.epistemic_summary.derived_count}
            </span>
          </div>
          <div className={`p-1.5 rounded-lg ${isNight ? "bg-slate-900" : "bg-white border border-slate-200"}`}>
            <span className="text-slate-500 block text-[9px]">Unknown</span>
            <span className="font-bold text-slate-400 text-xs">
              {currentVessel.epistemic_summary.unknown_count}
            </span>
          </div>
          <div className={`p-1.5 rounded-lg ${isNight ? "bg-slate-900" : "bg-white border border-slate-200"}`}>
            <span className="text-slate-500 block text-[9px]">Conflict</span>
            <span className="font-bold text-amber-400 text-xs">
              {currentVessel.epistemic_summary.conflict_count}
            </span>
          </div>
        </div>

        <button
          onClick={onOpenEvidenceExplorer}
          className={`w-full mt-1 px-3 py-1.5 rounded-xl border text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-all ${
            isNight
              ? "bg-slate-900 hover:bg-slate-800 text-sky-300 border-white/10"
              : "bg-white hover:bg-slate-100 text-sky-700 border-slate-300 shadow-sm"
          }`}
        >
          <FileText className="w-3.5 h-3.5 text-sky-400" />
          Evidence Explorer
        </button>
      </div>
    </div>
  );
}
