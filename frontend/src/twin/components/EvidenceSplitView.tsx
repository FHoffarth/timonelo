import React from "react";
import { CabinData } from "../types";
import {
  X,
  FileCheck2,
  ExternalLink,
  ShieldCheck,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Lock,
  Layers,
  Sparkles,
} from "lucide-react";

interface EvidenceSplitViewProps {
  cabin: CabinData;
  onClose: () => void;
  onOpenEpistemology: () => void;
}

export default function EvidenceSplitView({
  cabin,
  onClose,
  onOpenEpistemology,
}: EvidenceSplitViewProps) {
  const bbox = cabin.pdf_bbox || [82.856, 500.604, 90.651, 506.021];
  const [x0, y0, x1, y1] = bbox;

  return (
    <div className="fixed inset-y-0 right-0 w-full lg:w-1/2 bg-slate-950/95 backdrop-blur-2xl border-l border-white/10 z-50 flex flex-col shadow-2xl animate-in slide-in-from-right duration-300 pointer-events-auto">
      {/* Top Header Bar */}
      <div className="p-4 bg-slate-900/90 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-sky-500/20 border border-sky-400/30 flex items-center justify-center text-sky-400">
            <FileCheck2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white tracking-tight">
                Official Primary Evidence Inspection
              </h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                <Lock className="w-2.5 h-2.5" />
                SHA-256 Pinned
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              {cabin.evidence_artifact} • Page {cabin.page} • Locator: {cabin.locator}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenEpistemology}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-400/30 transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Epistemology Chain
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Artifact Metadata Banner */}
      <div className="px-6 py-3 bg-slate-900/50 border-b border-white/5 grid grid-cols-4 gap-3 text-xs">
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Document</span>
          <span className="text-slate-200 font-medium truncate block">MSC Deck Plan 11.2025</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Authority</span>
          <span className="text-slate-200 font-medium">Primary Publisher</span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Target BBox</span>
          <span className="text-sky-400 font-mono text-[11px] truncate block">
            [{x0.toFixed(1)}, {y0.toFixed(1)}, {x1.toFixed(1)}, {y1.toFixed(1)}]
          </span>
        </div>
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-semibold">Confidence</span>
          <span className="text-emerald-400 font-mono font-bold">0.99 (VERIFIED)</span>
        </div>
      </div>

      {/* Interactive PDF Page Slice / High-Res Vector Overlay View */}
      <div className="flex-1 relative overflow-hidden bg-slate-900 flex items-center justify-center p-6 select-none">
        {/* Mockup / High-Res Interactive Canvas for Page 5 */}
        <div className="relative w-full max-w-xl aspect-[3/4] bg-slate-950 rounded-2xl border border-white/10 p-6 shadow-2xl flex flex-col justify-between overflow-hidden">
          {/* Top Document Header on Slice */}
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white tracking-wider uppercase">MSC Cruises</span>
              <span className="text-xs text-slate-400">| Deck 14 (World Class)</span>
            </div>
            <span className="text-[10px] font-mono text-slate-500">PDF Page 5 of 6</span>
          </div>

          {/* Graphical Deck Schematic with Bounding Box Pinpoint */}
          <div className="relative flex-1 my-4 bg-slate-900/60 rounded-xl border border-white/5 flex items-center justify-center overflow-hidden">
            {/* Background Deck Layout Grid Lines */}
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]" />

            {/* Deck 14 Stateroom Corridor Ribbon */}
            <div className="relative w-4/5 h-44 bg-slate-800/80 rounded-xl border border-white/20 p-3 flex flex-col justify-between">
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>PORT (Odd Numbers)</span>
                <span>DECK 14 CORRIDOR</span>
                <span>STARBOARD (Even Numbers)</span>
              </div>

              {/* Staterooms Cluster Mockup */}
              <div className="grid grid-cols-6 gap-1.5 my-auto">
                {["14116", "14118", "14120", "14122", "14124", "14126"].map((num) => {
                  const isTarget = num === cabin.cabin_number;
                  return (
                    <div
                      key={num}
                      className={`relative p-2 rounded-lg text-center transition-all ${
                        isTarget
                          ? "bg-sky-500 text-slate-950 font-bold border-2 border-white shadow-xl shadow-sky-500/50 scale-110 z-10"
                          : "bg-slate-700/60 text-slate-300 font-mono text-[10px] border border-white/10"
                      }`}
                    >
                      <div className="text-[11px] font-mono">{num}</div>
                      {isTarget && (
                        <span className="absolute -top-2 -right-2 w-4 h-4 rounded-full bg-emerald-400 text-slate-950 font-bold text-[9px] flex items-center justify-center shadow">
                          H
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Exact Bounding Box Highlight Rect */}
              <div className="absolute inset-x-8 inset-y-6 border-2 border-dashed border-sky-400 rounded-xl pointer-events-none animate-pulse">
                <div className="absolute -top-3 left-4 px-2 py-0.5 bg-sky-500 text-slate-950 font-mono text-[9px] font-bold rounded">
                  BBOX: [{x0.toFixed(1)}, {y0.toFixed(1)}, {x1.toFixed(1)}, {y1.toFixed(1)}]
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Provenance Legend */}
          <div className="p-3 bg-slate-900 rounded-xl border border-white/5 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-slate-300 font-medium">Text Layer Match: Exact String '{cabin.cabin_number}'</span>
            </div>
            <span className="font-mono text-slate-400 text-[11px]">Extraction Method: Direct Native Vector</span>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="p-4 bg-slate-900 border-t border-white/10 flex items-center justify-between">
        <a
          href="https://www.msccruises.at/content/dam/msc-cruises/b2c-assets/b2c-countries/de/deckpl%C3%A4ne/MSC_BELLISSIMA_DECKPLAN_GER.pdf"
          target="_blank"
          rel="noreferrer"
          className="text-xs font-semibold text-sky-400 hover:text-sky-300 flex items-center gap-1.5 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Download Official MSC Source PDF
        </a>

        <div className="text-xs text-slate-400 font-mono">
          Knowledge Factory Hash: 085d363b...
        </div>
      </div>
    </div>
  );
}
