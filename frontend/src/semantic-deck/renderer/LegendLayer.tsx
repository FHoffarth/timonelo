import React from "react";
import { RenderOverlayMode } from "./types";

interface LegendLayerProps {
  overlayMode: RenderOverlayMode;
  onSelectOverlayMode: (mode: RenderOverlayMode) => void;
  isNight?: boolean;
}

export const LegendLayer: React.FC<LegendLayerProps> = ({
  overlayMode,
  onSelectOverlayMode,
  isNight = false,
}) => {
  return (
    <div className={`absolute bottom-4 left-6 z-20 pointer-events-auto p-3 rounded-2xl border shadow-lg flex items-center gap-4 text-xs select-none backdrop-blur-md ${
      isNight ? "bg-slate-900/90 border-white/10 text-slate-300" : "bg-white/95 border-slate-200 text-slate-700"
    }`}>
      {/* Categories & Legend Keys */}
      <div className="flex items-center gap-3">
        <span className="text-[10px] font-mono uppercase font-bold text-slate-400">SCHEMATIC LABELS:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-xs bg-[#C58A46]" />
          <span className="text-[11px]">Suite</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-xs bg-[#3B82F6]" />
          <span className="text-[11px]">Balcony</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-xs bg-[#14B8A6]" />
          <span className="text-[11px]">Ocean View</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-xs bg-[#64748B]" />
          <span className="text-[11px]">Interior</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#10B981] border border-white" />
          <span className="text-[11px]">PRM (H)</span>
        </div>
      </div>

      <div className="h-4 w-px bg-slate-200 dark:bg-white/10 hidden sm:block" />

      {/* Overlay Mode Switcher */}
      <div className="hidden sm:flex items-center gap-1">
        <span className="text-[10px] font-mono uppercase font-bold text-slate-400 mr-1">OVERLAY:</span>
        {(["none", "epistemic"] as RenderOverlayMode[]).map((mode) => (
          <button
            key={mode}
            onClick={() => onSelectOverlayMode(mode)}
            className={`px-2 py-0.5 rounded-lg text-[10px] font-mono font-bold uppercase transition-colors cursor-pointer ${
              overlayMode === mode
                ? "bg-[#0C1B2A] text-white"
                : isNight
                ? "bg-slate-800 text-slate-400 hover:text-white"
                : "bg-slate-100 text-slate-600 hover:text-slate-900"
            }`}
          >
            {mode}
          </button>
        ))}
      </div>
    </div>
  );
};
