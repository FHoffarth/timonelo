import React from "react";
import { ShieldCheck, Calculator, HelpCircle, AlertTriangle } from "lucide-react";

export default function EpistemicLegendBar() {
  return (
    <div className="px-6 py-2.5 bg-slate-900/90 backdrop-blur-xl border-b border-white/10 flex items-center justify-between text-xs text-slate-400 select-none z-20 flex-wrap gap-4">
      {/* 1. Category Dimension (Content = Hue) */}
      <div className="flex items-center gap-4">
        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Content (Category):
        </span>
        <div className="flex items-center gap-3 text-[11px]">
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

      <div className="h-4 w-px bg-white/10 hidden md:block" />

      {/* 2. Epistemic Dimension (Knowledge = Border / Pattern) */}
      <div className="flex items-center gap-4">
        <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Knowledge (Epistemic State):
        </span>
        <div className="flex items-center gap-3 text-[11px]">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-emerald-300 font-mono">DIRECT (Solid)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm border border-dashed border-sky-400 bg-sky-500/30" />
            <span className="text-sky-300 font-mono">DERIVED (Dashed)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm border border-dotted border-slate-500 opacity-60" />
            <span className="text-slate-400 font-mono">UNKNOWN (Translucent)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rotate-45 bg-amber-400" />
            <span className="text-amber-300 font-mono">CONFLICT (Stripe)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
