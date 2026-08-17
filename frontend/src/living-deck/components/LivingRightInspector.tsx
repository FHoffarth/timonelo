import React from "react";
import { LivingCabin } from "../types";
import {
  X,
  Navigation2,
  FileCheck2,
  Accessibility,
  Footprints,
  Compass,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  MapPin,
  Lock,
} from "lucide-react";

interface LivingRightInspectorProps {
  cabin: LivingCabin | null;
  onClose: () => void;
  onStartRoute: (cabinNum: string, target: string) => void;
  onOpenEvidence: (cabin: LivingCabin) => void;
  onSelectCabinNumber: (cNum: string) => void;
}

export default function LivingRightInspector({
  cabin,
  onClose,
  onStartRoute,
  onOpenEvidence,
  onSelectCabinNumber,
}: LivingRightInspectorProps) {
  if (!cabin) return null;

  const [x0, y0, x1, y1] = cabin.pdf_bbox;

  return (
    <div className="absolute right-6 top-24 bottom-16 w-96 z-30 pointer-events-auto flex flex-col bg-slate-900/90 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-right-8 duration-300 select-none">
      {/* Header Banner */}
      <div className="p-5 pb-4 bg-gradient-to-b from-sky-500/10 to-transparent border-b border-white/5 flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              Ground Truth 0.99
            </span>
            {cabin.accessible && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/20 text-sky-300 border border-sky-400/30 flex items-center gap-1">
                <Accessibility className="w-3 h-3" />
                PRM Accessible (H)
              </span>
            )}
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            Cabin {cabin.cabin_number}
          </h2>
          <p className="text-xs text-slate-400 font-medium">
            Deck {cabin.deck} ({cabin.deck_name}) • {cabin.category}
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body Scroll */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 no-scrollbar text-sm text-slate-300">
        {/* Actions */}
        <div className="grid grid-cols-2 gap-2.5">
          <button
            onClick={() => onStartRoute(cabin.cabin_number, "Marketplace Buffet")}
            className="px-4 py-2.5 rounded-2xl font-semibold text-xs bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center justify-center gap-2 shadow-lg shadow-sky-500/20 transition-all active:scale-95"
          >
            <Navigation2 className="w-4 h-4 fill-slate-950" />
            Route to Buffet
          </button>
          <button
            onClick={() => onOpenEvidence(cabin)}
            className="px-4 py-2.5 rounded-2xl font-semibold text-xs bg-slate-800 hover:bg-slate-700 text-white border border-white/10 flex items-center justify-center gap-2 transition-all active:scale-95"
          >
            <FileCheck2 className="w-4 h-4 text-sky-400" />
            Ground Truth & Evidence
          </button>
        </div>

        {/* Epistemic Provenance Card */}
        <div className="p-3.5 bg-slate-800/50 rounded-2xl border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Epistemic Provenance
            </h3>
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono text-[10px]">
              {cabin.epistemic_method}
            </span>
          </div>

          <div className="space-y-1.5 text-xs font-mono text-slate-300">
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Statement ID:</span>
              <span className="text-sky-300">{cabin.statement_id}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Artifact:</span>
              <span className="text-slate-200">{cabin.evidence_artifact}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">PDF Locator:</span>
              <span className="text-slate-300 text-[11px]">
                BBox [{x0.toFixed(1)}, {y0.toFixed(1)}, {x1.toFixed(1)}, {y1.toFixed(1)}]
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Review State:</span>
              <span className="text-emerald-400 font-semibold">{cabin.review_state}</span>
            </div>
          </div>
        </div>

        {/* Spatial Topology / Adjacencies */}
        <div className="p-3.5 bg-slate-800/50 rounded-2xl border border-white/5 space-y-2.5">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span>Spatial Adjacencies</span>
            <span className="text-[10px] text-sky-400 font-mono">Topology Proof</span>
          </h3>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
              <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                <ArrowLeft className="w-3 h-3" /> Neighbor Left
              </div>
              <div className="font-mono font-semibold text-slate-200 mt-0.5">
                {parseInt(cabin.cabin_number) - 2}
              </div>
            </div>

            <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
              <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                <ArrowRight className="w-3 h-3" /> Neighbor Right
              </div>
              <div className="font-mono font-semibold text-slate-200 mt-0.5">
                {parseInt(cabin.cabin_number) + 2}
              </div>
            </div>

            <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5 col-span-2">
              <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                <ArrowUp className="w-3 h-3 text-emerald-400" /> Ceiling Above (Deck {cabin.deck + 1})
              </div>
              <div className="font-semibold text-slate-200 mt-0.5">
                {cabin.deck === 14 ? "Marketplace Buffet Forward Dining (Deck 15)" : `Stateroom ${cabin.deck + 1}${cabin.cabin_number.slice(2)}`}
              </div>
            </div>

            <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5 col-span-2">
              <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                <ArrowDown className="w-3 h-3 text-blue-400" /> Floor Below (Deck {cabin.deck - 1})
              </div>
              <div className="font-semibold text-slate-200 mt-0.5">
                {`Stateroom ${cabin.deck - 1}${cabin.cabin_number.slice(2)} (Deck ${cabin.deck - 1})`}
              </div>
            </div>
          </div>
        </div>

        {/* Proximity & Distance Matrix */}
        <div className="p-3.5 bg-slate-800/50 rounded-2xl border border-white/5 space-y-2">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Nearest Amenities & Distance
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>Midship Panoramic Elevators</span>
              </div>
              <span className="font-mono text-cyan-300 font-semibold">16.2m (~17s)</span>
            </div>

            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40">
              <div className="flex items-center gap-2">
                <Footprints className="w-4 h-4 text-emerald-400" />
                <span>Marketplace Buffet (Deck 15)</span>
              </div>
              <span className="font-mono text-emerald-300 font-semibold">111.1m (~1.9min)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
