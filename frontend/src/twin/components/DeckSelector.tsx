import React from "react";
import { ALL_DECKS, DECKS_MAP } from "../twinEngine";
import { DeckData } from "../types";
import { Layers, Compass, ShieldCheck, Sparkles } from "lucide-react";

interface DeckSelectorProps {
  activeDeck: number;
  onSelectDeck: (deckNum: number) => void;
  viewMode: string;
  onToggleViewMode: (mode: any) => void;
}

export default function DeckSelector({
  activeDeck,
  onSelectDeck,
  viewMode,
  onToggleViewMode,
}: DeckSelectorProps) {
  // Sort descending from Top Deck 19 to Deck 5
  const sortedDecks = [...ALL_DECKS].sort((a, b) => b.deck_number - a.deck_number);

  return (
    <div className="absolute left-6 top-24 bottom-16 z-20 flex flex-col pointer-events-auto">
      {/* View Mode Toggle Switch */}
      <div className="mb-3 p-1.5 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl flex items-center gap-1 shadow-2xl">
        <button
          onClick={() => onToggleViewMode("3d_exterior")}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
            viewMode === "3d_exterior"
              ? "bg-sky-500 text-white shadow-lg shadow-sky-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
          }`}
        >
          <Compass className="w-3.5 h-3.5" />
          3D Ship
        </button>
        <button
          onClick={() => onToggleViewMode("deck_topdown")}
          className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 ${
            viewMode === "deck_topdown"
              ? "bg-sky-500 text-white shadow-lg shadow-sky-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Deck View
        </button>
      </div>

      {/* Vertical Elevator Deck Stack */}
      <div className="flex-1 w-52 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-3xl p-2.5 flex flex-col gap-1.5 overflow-y-auto no-scrollbar shadow-2xl">
        <div className="px-2 py-1 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-slate-400 border-b border-white/5 pb-2">
          <span>Decks & Levels</span>
          <span className="text-sky-400 font-mono">19 Total</span>
        </div>

        {sortedDecks.map((d) => {
          const isActive = activeDeck === d.deck_number;
          return (
            <button
              key={d.deck_number}
              onClick={() => onSelectDeck(d.deck_number)}
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
                    {d.cabins > 0 ? `${d.cabins} Cabins` : `${d.venues.length} Venues`}
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
