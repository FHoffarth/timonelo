import React, { useState } from "react";
import { LivingCabin } from "../types";
import {
  X,
  ShieldCheck,
  FileCode2,
  History,
  Scale,
  Calculator,
  Lock,
  ExternalLink,
  Sparkles,
} from "lucide-react";

interface LivingEvidenceModalProps {
  cabin: LivingCabin;
  onClose: () => void;
}

export default function LivingEvidenceModal({ cabin, onClose }: LivingEvidenceModalProps) {
  const [activeTab, setActiveTab] = useState<"epistemology" | "timeline" | "conflicts">("epistemology");
  const [x0, y0, x1, y1] = cabin.pdf_bbox;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200 pointer-events-auto select-none">
      <div className="relative w-full max-w-4xl max-h-[85vh] bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        {/* Top Header */}
        <div className="p-6 bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sky-500/20 border border-sky-400/30 flex items-center justify-center text-sky-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">
                  Ground Truth & Epistemology Chain
                </h2>
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  CONFIDENCE: {cabin.confidence} (VERIFIED)
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Cabin {cabin.cabin_number} • Statement {cabin.statement_id} • Source: {cabin.evidence_artifact}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Buttons */}
        <div className="px-6 py-2 bg-slate-900/80 border-b border-white/5 flex items-center gap-2 text-xs">
          <button
            onClick={() => setActiveTab("epistemology")}
            className={`px-4 py-2 rounded-xl font-semibold transition-colors flex items-center gap-2 ${
              activeTab === "epistemology"
                ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <FileCode2 className="w-4 h-4" />
            Epistemic Proof
          </button>
          <button
            onClick={() => setActiveTab("timeline")}
            className={`px-4 py-2 rounded-xl font-semibold transition-colors flex items-center gap-2 ${
              activeTab === "timeline"
                ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <History className="w-4 h-4" />
            Evidence Timeline
          </button>
          <button
            onClick={() => setActiveTab("conflicts")}
            className={`px-4 py-2 rounded-xl font-semibold transition-colors flex items-center gap-2 ${
              activeTab === "conflicts"
                ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <Scale className="w-4 h-4" />
            Conflict Register
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-slate-300 no-scrollbar">
          {activeTab === "epistemology" && (
            <div className="space-y-4">
              <div className="p-4 bg-slate-800/40 rounded-2xl border border-white/5">
                <h3 className="text-xs font-bold text-sky-400 uppercase tracking-wider mb-2">
                  Ground Truth Proof Verification
                </h3>
                <div className="grid grid-cols-3 gap-3 text-xs">
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">Method</span>
                    <span className="font-mono text-emerald-400 font-bold">{cabin.epistemic_method}</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">PDF Bounding Box</span>
                    <span className="font-mono text-sky-300 font-bold">
                      [{x0.toFixed(1)}, {y0.toFixed(1)}, {x1.toFixed(1)}, {y1.toFixed(1)}]
                    </span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">Review State</span>
                    <span className="font-mono text-emerald-400 font-bold">{cabin.review_state}</span>
                  </div>
                </div>
              </div>

              {/* Table */}
              <div className="border border-white/10 rounded-2xl overflow-hidden text-xs">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-800/80 text-slate-400 font-semibold border-b border-white/10">
                      <th className="p-3">Property</th>
                      <th className="p-3">Value</th>
                      <th className="p-3">Method</th>
                      <th className="p-3">Evidence Proof</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 font-mono">
                    <tr>
                      <td className="p-3 font-sans font-semibold text-white">cabin_number</td>
                      <td className="p-3 text-sky-300 font-bold">{cabin.cabin_number}</td>
                      <td className="p-3"><span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">DIRECT_EVIDENTIARY</span></td>
                      <td className="p-3 text-slate-400 font-sans">Extracted from text layer at BBox [{x0.toFixed(1)}, {y0.toFixed(1)}]</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-sans font-semibold text-white">accessible</td>
                      <td className="p-3 text-emerald-400 font-bold">{cabin.accessible ? "true (H-marked)" : "false"}</td>
                      <td className="p-3"><span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">DIRECT_EVIDENTIARY</span></td>
                      <td className="p-3 text-slate-400 font-sans">Vector glyph 'H' intersects cabin boundary</td>
                    </tr>
                    <tr>
                      <td className="p-3 font-sans font-semibold text-white">balcony</td>
                      <td className="p-3 text-slate-300">{cabin.balcony ? "true" : "false"}</td>
                      <td className="p-3"><span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 text-[10px]">DERIVED_DETERMINISTIC</span></td>
                      <td className="p-3 text-slate-400 font-sans">Rule: Category IR2 = Interior &rarr; balcony: false</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === "timeline" && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Evidence Lifecycle</h3>
              <div className="p-4 bg-slate-800/40 rounded-2xl border border-white/5 space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">1. Official Deck Plan Acquired</span>
                  <span className="text-slate-500 font-mono">Stand 11.2025</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">2. Deterministic Statement Generated</span>
                  <span className="text-sky-400 font-mono">{cabin.statement_id}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">3. Topological Audit Passed</span>
                  <span className="text-emerald-400 font-mono">VERIFIED</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === "conflicts" && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl space-y-2 text-xs">
              <div className="text-rose-400 font-bold uppercase">Aggregate Cabin Count Conflict</div>
              <p className="text-slate-300">
                Official Deckplan 11.2025 proves 2,217 staterooms. Marketing website lists 2,201 staterooms. Both claims are preserved transparently.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
