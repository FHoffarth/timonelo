import React from "react";
import { LIVING_DECKS } from "../livingEngine";
import { LivingViewMode } from "../types";
import { Layers, Box, Compass, Sparkles } from "lucide-react";

interface LivingDeckSelectorProps {
  activeDeck: number;
  viewMode: LivingViewMode;
  onSelectDeck: (deckNum: number) => void;
  onToggleViewMode: (mode: LivingViewMode) => void;
}

export default function LivingDeckSelector({
  activeDeck,
  viewMode,
  onSelectDeck,
  onToggleViewMode,
}: LivingDeckSelectorProps) {
  return (
    <div className="absolute left-6 top-24 bottom-16 z-20 flex flex-col pointer-events-auto select-none">
      {/* View Mode Toggle Switch */}
      <div className="mb-3 p-1.5 bg-slate-900/85 backdrop-blur-xl border border-white/10 rounded-2xl flex items-center gap-1 shadow-2xl">
        <button
          onClick={() => onToggleViewMode("single_deck")}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
            viewMode === "single_deck"
              ? "bg-sky-500 text-white shadow-lg shadow-sky-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
          }`}
        >
          <Compass className="w-3.5 h-3.5" />
          Living Deck
        </button>
        <button
          onClick={() => onToggleViewMode("exploded_stack")}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
            viewMode === "exploded_stack"
              ? "bg-sky-500 text-white shadow-lg shadow-sky-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
          }`}
        >
          <Box className="w-3.5 h-3.5" />
          Exploded Stack
        </button>
      </div>

      {/* Vertical Elevator Deck Stack */}
      <div className="flex-1 w-52 bg-slate-900/85 backdrop-blur-xl border border-white/10 rounded-3xl p-2.5 flex flex-col gap-1.5 overflow-y-auto no-scrollbar shadow-2xl">
        <div className="px-2 py-1 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-slate-400 border-b border-white/5 pb-2">
          <span>Official Decks</span>
          <span className="text-sky-400 font-mono">11 Levels</span>
        </div>

        {LIVING_DECKS.map((d) => {
          const isActive = activeDeck === d.deck_number && viewMode === "single_deck";
          return (
            <button
              key={d.deck_number}
              onClick={() => {
                onSelectDeck(d.deck_number);
                onToggleViewMode("single_deck");
              }}
              className={`group w-full px-3 py-2 rounded-2xl text-left transition-all duration-200 flex items-center justify-between ${
                isActive
                  ? "bg-gradient-to-r from-sky-500/20 to-blue-600/30 border border-sky-400/40 text-white shadow-lg shadow-sky-500/20"
                  : "text-slate-300 hover:bg-white/5 hover:text-white border border-transparent"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-7 h-7 rounded-xl flex items-center justify-center font-mono font-bold text-xs transition-colors ${
                    isActive
                      ? "bg-sky-400 text-slate-950 shadow-md"
                      : "bg-slate-800/80 text-slate-300 group-hover:bg-slate-700"
                  }`}
                >
                  {d.deck_number}
                </div>
                <div className="flex flex-col">
                  <span className="text-xs font-semibold truncate leading-tight">
                    {d.deck_name}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {d.cabins_count > 0 ? `${d.cabins_count} Staterooms` : `${d.public_areas.length} Venues`}
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
  );
}
