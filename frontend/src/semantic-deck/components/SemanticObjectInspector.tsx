import React from "react";
import { SemanticObject } from "../types";
import { getCategoryStyle, getEpistemicStyle } from "../semanticEngine";
import {
  X,
  ShieldCheck,
  Accessibility,
  Footprints,
  Compass,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  FileText,
  AlertCircle,
  HelpCircle,
  Link,
  Layers,
  Sparkles,
} from "lucide-react";

interface SemanticObjectInspectorProps {
  object: SemanticObject | null;
  onClose: () => void;
  onSelectObjectId: (id: string) => void;
}

export default function SemanticObjectInspector({
  object,
  onClose,
  onSelectObjectId,
}: SemanticObjectInspectorProps) {
  if (!object) return null;

  const catStyle = getCategoryStyle(object.category);
  const epiStyle = getEpistemicStyle(object.epistemic_state);

  return (
    <div className="w-96 h-full bg-slate-900/90 backdrop-blur-2xl border-l border-white/10 flex flex-col justify-between p-6 select-none z-30 overflow-y-auto no-scrollbar text-slate-300">
      <div className="space-y-6">
        {/* Top Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase border ${epiStyle.badgeClass}`}>
                {epiStyle.label}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${catStyle.badgeBg}`}>
                {object.category_label}
              </span>
              {object.accessible && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/20 text-sky-300 border border-sky-400/30 flex items-center gap-1">
                  <Accessibility className="w-3 h-3" /> PRM (H)
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              {object.label}
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Deck {object.deck} • {object.side} Side • {object.zone.replace("_", " ")}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Epistemic Provenance Card */}
        <div className="p-4 bg-slate-950/60 rounded-2xl border border-white/5 space-y-2.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <span>Epistemic Grounding</span>
            <span className="text-emerald-400 font-mono">
              {(object.confidence * 100).toFixed(0)}% Confidence
            </span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Statements:</span>
              <span className="text-sky-300">{object.statements.join(", ")}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Evidence Records:</span>
              <span className="text-slate-200">{object.evidence_links.length} Artifacts</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Review State:</span>
              <span className="text-emerald-400">{object.review_state}</span>
            </div>
          </div>

          {object.evidence_links.length > 0 && (
            <div className="pt-2 border-t border-white/5 space-y-1">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">
                Primary Artifact Locator
              </span>
              <div className="p-2 rounded-xl bg-slate-900/80 text-[11px] font-mono text-slate-300 flex items-center justify-between">
                <span>{object.evidence_links[0].artifact_id}</span>
                <span className="text-sky-400">P.{object.evidence_links[0].page ?? 1}</span>
              </div>
            </div>
          )}
        </div>

        {/* Known Topological Relations */}
        <div className="p-4 bg-slate-950/60 rounded-2xl border border-white/5 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <span>Known Semantic Relations</span>
            <span className="text-sky-400 font-mono text-[10px]">Graph Edges</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            {object.known_relations.neighbor_fore && (
              <button
                onClick={() => onSelectObjectId(object.known_relations.neighbor_fore!)}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-white/5 border border-white/5 text-left transition-colors"
              >
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowLeft className="w-3 h-3" /> Fore (Forward)
                </div>
                <div className="font-mono font-bold text-sky-300 mt-0.5">
                  Cabin {object.known_relations.neighbor_fore}
                </div>
              </button>
            )}

            {object.known_relations.neighbor_aft && (
              <button
                onClick={() => onSelectObjectId(object.known_relations.neighbor_aft!)}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-white/5 border border-white/5 text-left transition-colors"
              >
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowRight className="w-3 h-3" /> Aft (Behind)
                </div>
                <div className="font-mono font-bold text-sky-300 mt-0.5">
                  Cabin {object.known_relations.neighbor_aft}
                </div>
              </button>
            )}

            {object.known_relations.across_corridor && (
              <button
                onClick={() => onSelectObjectId(object.known_relations.across_corridor!)}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-white/5 border border-white/5 text-left transition-colors col-span-2"
              >
                <div className="text-slate-500 text-[10px]">Across Corridor</div>
                <div className="font-mono font-bold text-sky-300 mt-0.5">
                  Cabin {object.known_relations.across_corridor}
                </div>
              </button>
            )}

            {object.known_relations.overhead && (
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 col-span-2">
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowUp className="w-3 h-3 text-emerald-400" /> Ceiling Overhead (Deck {object.deck + 1})
                </div>
                <div className="font-medium text-slate-200 mt-0.5">
                  {object.known_relations.overhead}
                </div>
              </div>
            )}

            {object.known_relations.underfoot && (
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 col-span-2">
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowDown className="w-3 h-3 text-blue-400" /> Floor Underfoot (Deck {object.deck - 1})
                </div>
                <div className="font-medium text-slate-200 mt-0.5">
                  {object.known_relations.underfoot}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Unknown Relations (First-Class Visual Citizen) */}
        {object.unknown_relations.length > 0 && (
          <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-700/40 space-y-2.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <span className="flex items-center gap-1.5 text-slate-400">
                <HelpCircle className="w-3.5 h-3.5" />
                Unknown Relations ({object.unknown_relations.length})
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Explicit Uncertainty</span>
            </div>

            {object.unknown_relations.map((unk, uIdx) => (
              <div key={uIdx} className="p-3 bg-slate-900/60 rounded-xl border border-dashed border-slate-700 space-y-1 text-xs">
                <div className="font-mono text-slate-300 font-semibold">{unk.field}</div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{unk.reason}</p>
                <div className="pt-1 text-[10px] font-mono text-sky-400 flex items-center gap-1">
                  <span>Required Document:</span>
                  <span className="underline">{unk.required_document}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer Navigation Action */}
      <div className="pt-4 border-t border-white/5">
        <div className="p-3 bg-slate-950/80 rounded-2xl border border-white/5 flex items-center justify-between text-xs">
          <span className="text-slate-500 font-mono">Nearest Elevator:</span>
          <span className="font-semibold text-sky-300 font-mono">
            {object.known_relations.nearest_elevator || "Midship Core"}
          </span>
        </div>
      </div>
    </div>
  );
}
