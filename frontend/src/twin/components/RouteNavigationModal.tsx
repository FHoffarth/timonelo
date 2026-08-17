import React from "react";
import { RouteResult } from "../types";
import {
  Navigation2,
  X,
  Footprints,
  Clock,
  CornerDownRight,
  Accessibility,
  CheckCircle2,
} from "lucide-react";

interface RouteNavigationModalProps {
  route: RouteResult | null;
  accessibleOnly: boolean;
  onToggleAccessible: () => void;
  onClose: () => void;
}

export default function RouteNavigationModal({
  route,
  accessibleOnly,
  onToggleAccessible,
  onClose,
}: RouteNavigationModalProps) {
  if (!route) return null;

  return (
    <div className="absolute left-64 top-24 z-30 w-96 bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-3xl p-5 shadow-2xl pointer-events-auto animate-in fade-in zoom-in-95 duration-200">
      <div className="flex items-start justify-between border-b border-white/10 pb-4 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-2xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
            <Navigation2 className="w-5 h-5 fill-rose-400" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white leading-tight">
              Indoor Turn-by-Turn
            </h3>
            <p className="text-xs text-slate-400">
              {route.from} &rarr; {route.to}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2 p-3 bg-slate-800/60 rounded-2xl border border-white/5 text-center mb-4">
        <div>
          <span className="text-[10px] uppercase font-semibold text-slate-400 block">Distance</span>
          <span className="text-sm font-mono font-bold text-white">{route.total_distance_m}m</span>
        </div>
        <div>
          <span className="text-[10px] uppercase font-semibold text-slate-400 block">Walking Time</span>
          <span className="text-sm font-mono font-bold text-emerald-400">
            ~{route.estimated_walking_time_min} min
          </span>
        </div>
        <div>
          <span className="text-[10px] uppercase font-semibold text-slate-400 block">Turns</span>
          <span className="text-sm font-mono font-bold text-sky-400">{route.turn_count}</span>
        </div>
      </div>

      {/* Accessible Switch */}
      <div className="flex items-center justify-between p-2.5 bg-slate-800/40 rounded-xl mb-4 border border-white/5">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Accessibility className="w-4 h-4 text-sky-400" />
          Step-Free (Elevators Only)
        </div>
        <button
          onClick={onToggleAccessible}
          className={`w-10 h-6 rounded-full transition-colors relative p-0.5 ${
            accessibleOnly ? "bg-sky-500" : "bg-slate-700"
          }`}
        >
          <div
            className={`w-5 h-5 rounded-full bg-white transition-transform ${
              accessibleOnly ? "translate-x-4" : "translate-x-0"
            }`}
          />
        </button>
      </div>

      {/* Turn-by-Turn Instruction List */}
      <div className="space-y-2.5 max-h-60 overflow-y-auto no-scrollbar pr-1">
        {route.turn_by_turn_instructions.map((step, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-950/40 border border-white/5 text-xs text-slate-300"
          >
            <div className="w-5 h-5 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-mono font-bold text-[10px] shrink-0 mt-0.5">
              {idx + 1}
            </div>
            <div className="flex-1 leading-relaxed">{step}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
