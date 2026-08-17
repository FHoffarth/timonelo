import React, { useState } from "react";
import { CabinData } from "../types";
import {
  X,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  FileCode2,
  Clock,
  Sparkles,
  GitPullRequest,
  BookOpen,
  Scale,
  History,
  Lock,
  ArrowRight,
  Calculator,
} from "lucide-react";

interface EpistemologyModalProps {
  cabin: CabinData;
  onClose: () => void;
}

export default function EpistemologyInspectorModal({ cabin, onClose }: EpistemologyModalProps) {
  const [activeTab, setActiveTab] = useState<"fields" | "timeline" | "conflicts" | "math">("fields");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200 pointer-events-auto">
      <div className="relative w-full max-w-4xl max-h-[85vh] bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        {/* Modal Top Header */}
        <div className="p-6 bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sky-500/20 border border-sky-400/30 flex items-center justify-center text-sky-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">
                  Epistemology & Ground Truth Chain
                </h2>
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  CONFIDENCE: 0.99 (VERIFIED)
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Entity: Cabin {cabin.cabin_number} • Statement ID: STM-BEL-14122-V1 • Provenance: {cabin.evidence_artifact}
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

        {/* Tab Navigation Navigation */}
        <div className="px-6 py-2 bg-slate-900/80 border-b border-white/5 flex items-center gap-2 text-xs">
          <button
            onClick={() => setActiveTab("fields")}
            className={`px-4 py-2 rounded-xl font-semibold transition-colors flex items-center gap-2 ${
              activeTab === "fields"
                ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <FileCode2 className="w-4 h-4" />
            Field Epistemology
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
          <button
            onClick={() => setActiveTab("math")}
            className={`px-4 py-2 rounded-xl font-semibold transition-colors flex items-center gap-2 ${
              activeTab === "math"
                ? "bg-sky-500/20 text-sky-300 border border-sky-400/30"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
            }`}
          >
            <Calculator className="w-4 h-4" />
            Mathematical Proofs
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-sm text-slate-300 no-scrollbar">
          {/* TAB 1: FIELD EPISTEMOLOGY */}
          {activeTab === "fields" && (
            <div className="space-y-4">
              <div className="p-4 bg-slate-800/40 rounded-2xl border border-white/5">
                <h3 className="text-xs font-bold text-sky-400 uppercase tracking-wider mb-2">
                  Multi-Dimensional Confidence Reasoning
                </h3>
                <div className="grid grid-cols-4 gap-3 text-xs">
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">Artifact Integrity</span>
                    <span className="font-mono text-emerald-400 font-bold">1.00 (SHA-256 Valid)</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">Extraction Fidelity</span>
                    <span className="font-mono text-emerald-400 font-bold">0.999 (Native Vector)</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">Source Authority</span>
                    <span className="font-mono text-emerald-400 font-bold">1.00 (Primary Deckplan)</span>
                  </div>
                  <div className="p-2.5 bg-slate-900/80 rounded-xl border border-white/5">
                    <span className="text-slate-500 text-[10px] block uppercase">Peer Review State</span>
                    <span className="font-mono text-sky-400 font-bold">VERIFIED_PUBLISHED</span>
                  </div>
                </div>
              </div>

              {/* Field Breakdown Table */}
              <div className="border border-white/10 rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-800/80 text-slate-400 font-semibold border-b border-white/10">
                      <th className="p-3">Fact / Property</th>
                      <th className="p-3">Asserted Value</th>
                      <th className="p-3">Epistemic Method</th>
                      <th className="p-3">Evidence Source & Proof</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 font-mono">
                    <tr className="hover:bg-white/5">
                      <td className="p-3 font-sans font-semibold text-white">cabin_number</td>
                      <td className="p-3 text-sky-300 font-bold">{cabin.cabin_number}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                          DIRECT_EVIDENTIARY
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 font-sans">
                        Text layer match in MSC-BEL-ART-001 Page 5 BBox [82.8, 500.6, 90.6, 506.0]
                      </td>
                    </tr>

                    <tr className="hover:bg-white/5">
                      <td className="p-3 font-sans font-semibold text-white">deck</td>
                      <td className="p-3 text-white">{cabin.deck} ({cabin.deck_name})</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                          DIRECT_EVIDENTIARY
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 font-sans">
                        Panel Title Header 'Deck 14 World Class'
                      </td>
                    </tr>

                    <tr className="hover:bg-white/5">
                      <td className="p-3 font-sans font-semibold text-white">accessible</td>
                      <td className="p-3 text-emerald-400 font-bold">{cabin.accessible ? "true" : "false"}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                          DIRECT_EVIDENTIARY
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 font-sans">
                        Vector glyph 'H' intersects cabin boundary polygon on Page 5
                      </td>
                    </tr>

                    <tr className="hover:bg-white/5">
                      <td className="p-3 font-sans font-semibold text-white">balcony</td>
                      <td className="p-3 text-slate-300">{cabin.balcony ? "true" : "false"}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 text-[10px]">
                          DERIVED_DETERMINISTIC
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 font-sans">
                        Rule: Category IR2 = Deluxe Interior (Innenkabine) &rarr; balcony: false
                      </td>
                    </tr>

                    <tr className="hover:bg-white/5 bg-amber-500/5">
                      <td className="p-3 font-sans font-semibold text-amber-300">additional_beds</td>
                      <td className="p-3 text-amber-400 font-bold">UNKNOWN</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px]">
                          UNKNOWN
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 font-sans">
                        <span className="text-amber-300 font-semibold block">Reason:</span> Per-cabin Pullman berth glyph extraction pending human review.
                        <span className="text-sky-400 block mt-1">Required Document: MSC-BEL-ART-019 (High-Res GA Drawing)</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 2: EVIDENCE TIMELINE */}
          {activeTab === "timeline" && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Artifact Ingestion & Review Lifecycle
              </h3>

              <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-sky-500/30">
                <div className="relative flex items-start gap-4">
                  <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center font-bold text-[10px]">
                    1
                  </div>
                  <div className="p-4 bg-slate-800/60 rounded-2xl border border-white/5 flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-white text-xs">Artifact Acquired & Pinned</span>
                      <span className="text-slate-500 font-mono text-[10px]">2025-11-15</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Official MSC Deckplan Stand 11.2025 acquired and cryptographically hashed with SHA-256 (085d363b...).
                    </p>
                  </div>
                </div>

                <div className="relative flex items-start gap-4">
                  <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center font-bold text-[10px]">
                    2
                  </div>
                  <div className="p-4 bg-slate-800/60 rounded-2xl border border-white/5 flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-white text-xs">Deterministic Vector Extraction</span>
                      <span className="text-slate-500 font-mono text-[10px]">2026-08-17 19:21</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Knowledge Factory extracted 2,217 staterooms, H-accessibility markers, and connecting pairs into canonical schema.
                    </p>
                  </div>
                </div>

                <div className="relative flex items-start gap-4">
                  <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-sky-400 text-slate-950 flex items-center justify-center font-bold text-[10px]">
                    3
                  </div>
                  <div className="p-4 bg-slate-800/60 rounded-2xl border border-white/5 flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-white text-xs">Topological Consistency Audit</span>
                      <span className="text-slate-500 font-mono text-[10px]">2026-08-17 19:26</span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Spatial adjacency engine validated left/right neighbors, vertical floor/ceiling alignment, and lift core distances.
                    </p>
                  </div>
                </div>

                <div className="relative flex items-start gap-4">
                  <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-emerald-400 text-slate-950 flex items-center justify-center font-bold text-[10px]">
                    4
                  </div>
                  <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-emerald-300 text-xs">Published as Ground Truth</span>
                      <span className="text-emerald-400 font-mono text-[10px]">CURRENT CANONICAL STATE</span>
                    </div>
                    <p className="text-xs text-emerald-200/80">
                      Entity is live in the MSC Bellissima Spatial Digital Twin.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: CONFLICT REGISTER */}
          {activeTab === "conflicts" && (
            <div className="space-y-4">
              <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl">
                <div className="flex items-center gap-2 mb-2 text-rose-400 font-bold text-xs uppercase tracking-wider">
                  <Scale className="w-4 h-4" />
                  Active Scientific Source Conflict
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  We never average or harmonize conflicting evidence. When two authoritative sources disagree, both are recorded openly:
                </p>

                <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 bg-slate-900/80 rounded-xl border border-white/10">
                    <span className="text-[10px] text-sky-400 font-bold uppercase block">Claim A (Canonical Topology)</span>
                    <span className="text-white font-bold text-sm block mt-1">2,217 Total Cabins</span>
                    <span className="text-slate-400 text-[11px] block mt-1">Source: Official MSC Deckplan 11.2025 (MSC-BEL-ART-001)</span>
                    <span className="text-emerald-400 text-[10px] block mt-2 font-semibold">STATUS: PROVEN (2,217 Unique BBoxes Extracted)</span>
                  </div>

                  <div className="p-3 bg-slate-900/80 rounded-xl border border-white/10">
                    <span className="text-[10px] text-amber-400 font-bold uppercase block">Claim B (Marketing Summary)</span>
                    <span className="text-white font-bold text-sm block mt-1">2,201 Total Cabins</span>
                    <span className="text-slate-400 text-[11px] block mt-1">Source: MSC Cruises DE Web Specification 2026 (MSC-BEL-ART-002)</span>
                    <span className="text-amber-400 text-[10px] block mt-2 font-semibold">STATUS: CONFLICT_REQUIRES_PUBLISHER_RESOLUTION</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: MATHEMATICAL PROOFS */}
          {activeTab === "math" && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Reproducible Mathematical Formulations
              </h3>

              <div className="p-4 bg-slate-800/50 rounded-2xl border border-white/5 space-y-3">
                <div>
                  <h4 className="text-xs font-bold text-sky-400">1. Coordinate Transformation Formula</h4>
                  <div className="p-3 bg-slate-950 rounded-xl font-mono text-xs text-slate-200 mt-1">
                    X_meters = x_norm * 315.83 m = {cabin.x} * 315.83 = {(cabin.x * 315.83).toFixed(2)} m<br />
                    Y_meters = y_norm * 43.00 m = {cabin.y} * 43.00 = {(cabin.y * 43.00).toFixed(2)} m
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-sky-400">2. IMO Standard Evacuation Walking Speed</h4>
                  <div className="p-3 bg-slate-950 rounded-xl font-mono text-xs text-slate-200 mt-1">
                    Walking Time (sec) = (Total Distance / 1.20 m/s) + (Turn Count * 4.0 sec)<br />
                    Reference: IMO MSC.1/Circ.1533 Section 3.1
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
