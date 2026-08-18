import React, { useState } from "react";
import { SemanticEntity } from "../types";
import { getClassificationColorToken, getEpistemicPatternToken } from "../apiClient";
import { CabinIntelligenceEngine } from "../../intelligence/CabinIntelligenceEngine";
import ExplainabilityCard from "../../explainability/ExplainabilityCard";
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
  Code2,
  ExternalLink,
  Volume2,
  Info,
  ChevronDown,
  ChevronUp,
  Workflow,
} from "lucide-react";

interface SemanticObjectInspectorProps {
  entity: SemanticEntity | null;
  onClose: () => void;
  onSelectEntityId: (id: string) => void;
  onOpenStandardsInspector: (entity: SemanticEntity) => void;
}

export default function SemanticObjectInspector({
  entity,
  onClose,
  onSelectEntityId,
  onOpenStandardsInspector,
}: SemanticObjectInspectorProps) {
  const [expandedScoreKey, setExpandedScoreKey] = useState<string | null>("quiet");
  const [showFullExplainability, setShowFullExplainability] = useState<boolean>(false);

  if (!entity) return null;

  const colorToken = getClassificationColorToken(entity.classification);
  const patternToken = getEpistemicPatternToken(entity.epistemic_state);

  const isCabin = entity.classification.startsWith("STATEROOM");
  const cabinIntel = isCabin ? CabinIntelligenceEngine.evaluateCabin(entity) : null;

  return (
    <div className="w-96 h-full bg-slate-900/95 backdrop-blur-2xl border-l border-white/10 flex flex-col justify-between p-6 select-none z-30 overflow-y-auto no-scrollbar text-slate-300">
      <div className="space-y-6">
        {/* Top Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase border ${patternToken.badgeClass}`}>
                {patternToken.label}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${colorToken.badge}`}>
                {entity.classification_label}
              </span>
              {entity.accessible && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-500/20 text-sky-300 border border-sky-400/30 flex items-center gap-1">
                  <Accessibility className="w-3 h-3" /> PRM (H)
                </span>
              )}
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              {entity.label}
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Deck {entity.level} ({entity.level_name}) • {entity.side} Side • {entity.zone.replace("_", " ")}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action: Inspect International Standards */}
        <button
          onClick={() => onOpenStandardsInspector(entity)}
          className="w-full px-4 py-2.5 rounded-2xl bg-gradient-to-r from-sky-500/20 to-blue-600/20 hover:from-sky-500/30 hover:to-blue-600/30 border border-sky-400/40 text-sky-200 text-xs font-semibold flex items-center justify-center gap-2 shadow-lg transition-all active:scale-95 cursor-pointer"
        >
          <Code2 className="w-4 h-4 text-sky-400" />
          Inspect W3C BOT / PROV-O / IndoorGML
        </button>

        {/* Cabin Intelligence Engine v1 Integration */}
        {cabinIntel && (
          <div className="p-4 bg-slate-950/80 rounded-2xl border border-gold/30 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-gold uppercase tracking-wider">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-gold" />
                Cabin Intelligence v1
              </span>
              <button
                onClick={() => setShowFullExplainability(!showFullExplainability)}
                className="px-2 py-0.5 rounded-md bg-gold/20 hover:bg-gold/30 text-gold border border-gold/40 text-[10px] font-mono font-bold flex items-center gap-1 transition-all cursor-pointer"
              >
                <Workflow className="w-3 h-3" />
                <span>{showFullExplainability ? "Hide Why? ▲" : "Why? (Evidence Trace) ▼"}</span>
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              {[cabinIntel.quiet_score, cabinIntel.motion_score, cabinIntel.walking_score, cabinIntel.privacy_score].map((sc) => {
                const isExp = expandedScoreKey === sc.key;
                return (
                  <div
                    key={sc.key}
                    onClick={() => setExpandedScoreKey(isExp ? null : sc.key)}
                    className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
                      isExp
                        ? "bg-slate-900 border-gold/50"
                        : "bg-slate-900/60 border-white/5 hover:border-white/20"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono text-slate-400">{sc.name.split(" ")[0]}</span>
                      <span className="font-mono text-xs font-bold text-white bg-slate-800 px-1.5 py-0.5 rounded">
                        {sc.score}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 line-clamp-1">{sc.grade}</div>
                    
                    {isExp && (
                      <div className="mt-2 pt-2 border-t border-white/10 space-y-1">
                        {sc.factors.map((f, i) => (
                          <div key={i} className="text-[9px] text-slate-300 leading-tight">
                            • {f}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {cabinIntel.all_reasoning.length > 0 && (
              <div className="p-2.5 rounded-xl bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-200 space-y-1">
                <div className="flex items-center gap-1 font-bold text-amber-300 text-[10px]">
                  <Info className="w-3 h-3 text-amber-400" /> Grounded Findings:
                </div>
                {cabinIntel.all_reasoning.map((r, i) => (
                  <p key={i} className="leading-snug text-[10px]">• {r}</p>
                ))}
              </div>
            )}

            {/* In-place Explainability Card on "Why?" click */}
            {showFullExplainability && (
              <div className="pt-2">
                <ExplainabilityCard
                  entity={entity}
                  vesselId="msc-bellissima"
                  defaultCategory={expandedScoreKey || "quiet"}
                  className="!p-4 !rounded-2xl border-gold/40"
                />
              </div>
            )}
          </div>
        )}

        {/* Epistemic Provenance Card */}
        <div className="p-4 bg-slate-950/60 rounded-2xl border border-white/5 space-y-2.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <span>Epistemic Grounding</span>
            <span className="text-emerald-400 font-mono">
              {(entity.confidence * 100).toFixed(0)}% Confidence
            </span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Statements:</span>
              <span className="text-sky-300 font-bold">{entity.statements.join(", ")}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Statement Count:</span>
              <span className="text-slate-200">{entity.statement_count} Verified</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Artifact Count:</span>
              <span className="text-slate-200">{entity.artifact_count} Held</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">Review State:</span>
              <span className="text-emerald-400">{entity.review_state}</span>
            </div>
          </div>

          {entity.evidence_links.length > 0 && (
            <div className="pt-2 border-t border-white/5 space-y-1">
              <span className="text-[10px] uppercase font-mono text-slate-500 font-bold">
                Primary Ground Truth Artifact
              </span>
              <div className="p-2.5 rounded-xl bg-slate-900/90 border border-white/10 text-xs">
                <div className="flex items-center justify-between font-bold text-white">
                  <span>{entity.evidence_links[0].artifact_id}</span>
                  <span className="text-sky-400">P.{entity.evidence_links[0].page ?? 1}</span>
                </div>
                <div className="text-[10px] text-slate-400 truncate">
                  {entity.evidence_links[0].source_title}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Known Topological Relations */}
        <div className="p-4 bg-slate-950/60 rounded-2xl border border-white/5 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <span>Known Topological Relations</span>
            <span className="text-sky-400 font-mono text-[10px]">W3C BOT Edges</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            {entity.relations.adjacent_fore && (
              <button
                onClick={() => onSelectEntityId(entity.relations.adjacent_fore!)}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-white/5 border border-white/5 text-left transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowLeft className="w-3 h-3" /> Fore (Forward)
                </div>
                <div className="font-mono font-bold text-sky-300 mt-0.5">
                  Space {entity.relations.adjacent_fore}
                </div>
              </button>
            )}

            {entity.relations.adjacent_aft && (
              <button
                onClick={() => onSelectEntityId(entity.relations.adjacent_aft!)}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-white/5 border border-white/5 text-left transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowRight className="w-3 h-3" /> Aft (Behind)
                </div>
                <div className="font-mono font-bold text-sky-300 mt-0.5">
                  Space {entity.relations.adjacent_aft}
                </div>
              </button>
            )}

            {entity.relations.adjacent_across && (
              <button
                onClick={() => onSelectEntityId(entity.relations.adjacent_across!)}
                className="p-2.5 rounded-xl bg-slate-900/80 hover:bg-white/5 border border-white/5 text-left transition-colors col-span-2 cursor-pointer"
              >
                <div className="text-slate-500 text-[10px]">Across Corridor</div>
                <div className="font-mono font-bold text-sky-300 mt-0.5">
                  Space {entity.relations.adjacent_across}
                </div>
              </button>
            )}

            {entity.relations.adjacent_overhead && (
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 col-span-2">
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowUp className="w-3 h-3 text-emerald-400" /> Ceiling Overhead (Level {entity.level + 1})
                </div>
                <div className="font-medium text-slate-200 mt-0.5">
                  {entity.relations.adjacent_overhead}
                </div>
              </div>
            )}

            {entity.relations.adjacent_underfoot && (
              <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5 col-span-2">
                <div className="flex items-center gap-1 text-slate-500 text-[10px]">
                  <ArrowDown className="w-3 h-3 text-blue-400" /> Floor Underfoot (Level {entity.level - 1})
                </div>
                <div className="font-medium text-slate-200 mt-0.5">
                  {entity.relations.adjacent_underfoot}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Unknown Fields (First-Class Citizen) */}
        {entity.unknown_fields.length > 0 && (
          <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-700/40 space-y-2.5">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
              <span className="flex items-center gap-1.5 text-slate-400">
                <HelpCircle className="w-3.5 h-3.5" />
                Unknown Fields ({entity.unknown_fields.length})
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Explicit Uncertainty</span>
            </div>

            {entity.unknown_fields.map((unk, uIdx) => (
              <div key={uIdx} className="p-3 bg-slate-900/60 rounded-xl border border-dashed border-slate-700 space-y-1 text-xs">
                <div className="font-mono text-slate-300 font-semibold">{unk.field_name}</div>
                <p className="text-[11px] text-slate-400 leading-relaxed">{unk.epistemic_reason}</p>
                <div className="pt-1 text-[10px] font-mono text-sky-400 flex items-center gap-1">
                  <span>Required Artifact:</span>
                  <span className="underline">{unk.required_artifact_class}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer Navigation Action */}
      <div className="pt-4 border-t border-white/5">
        <div className="p-3 bg-slate-950/80 rounded-2xl border border-white/5 flex items-center justify-between text-xs">
          <span className="text-slate-500 font-mono">Vertical Core Link:</span>
          <span className="font-semibold text-sky-300 font-mono">
            {entity.relations.connected_vertical_core || "Midship Core"}
          </span>
        </div>
      </div>
    </div>
  );
}
