import React from "react";
import { CabinData, VenueData } from "../types";
import { Compass, Gauge, ShieldCheck, Sparkles, Layers, Activity } from "lucide-react";

interface BottomStatusBarProps {
  activeDeck: number;
  deckName: string;
  selectedCabin: CabinData | null;
  selectedVenue: VenueData | null;
  onOpenEpistemology: () => void;
}

export default function BottomStatusBar({
  activeDeck,
  deckName,
  selectedCabin,
  selectedVenue,
  onOpenEpistemology,
}: BottomStatusBarProps) {
  const xMetric = selectedCabin ? (selectedCabin.x * 315.83).toFixed(1) : "157.9";
  const yMetric = selectedCabin ? (selectedCabin.y * 43.0).toFixed(1) : "0.0";
  const zMetric = selectedCabin ? selectedCabin.elevation_m.toFixed(1) : "25.0";

  return (
    <div className="absolute bottom-4 inset-x-6 z-20 pointer-events-auto flex items-center justify-between px-5 py-2.5 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl text-xs text-slate-300">
      {/* Ship Telemetry & Coordinates */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-bold text-white tracking-wide uppercase text-[11px]">
            MSC BELLISSIMA
          </span>
          <span className="text-slate-500 font-mono">IMO 9760524</span>
        </div>

        <div className="h-4 w-px bg-white/10" />

        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-slate-500">DECK:</span>
          <span className="text-sky-400 font-bold">{activeDeck}</span>
          <span className="text-slate-400">({deckName})</span>
        </div>

        <div className="h-4 w-px bg-white/10 hidden md:block" />

        <div className="items-center gap-2 font-mono text-[11px] hidden md:flex">
          <span className="text-slate-500">COORDS:</span>
          <span className="text-slate-200 font-semibold">
            X={xMetric}m, Y={yMetric}m, Z={zMetric}m
          </span>
        </div>
      </div>

      {/* Center Target Object */}
      <div className="hidden lg:flex items-center gap-2 font-semibold">
        <span className="text-slate-500 text-[11px]">ACTIVE OBJECT:</span>
        <span className="text-white px-2.5 py-0.5 rounded-lg bg-white/5 border border-white/10">
          {selectedCabin ? `Cabin ${selectedCabin.cabin_number}` : (selectedVenue ? selectedVenue.name : "None")}
        </span>
      </div>

      {/* Epistemology Trigger & Performance Counter */}
      <div className="flex items-center gap-4">
        {selectedCabin && (
          <button
            onClick={onOpenEpistemology}
            className="px-3 py-1 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-400/30 font-semibold text-[11px] flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
            Ground Truth (0.99)
          </button>
        )}

        <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[11px]">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>60 FPS</span>
        </div>
      </div>
    </div>
  );
}
