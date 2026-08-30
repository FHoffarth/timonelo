import React, { useState } from "react";
import { ExplainableCabinIntelligence, ExplainableScore } from "./types";
import { ExplainabilityEngine } from "./ExplainabilityEngine";
import { SemanticEntity } from "../semantic-deck/types";
import {
  ShieldCheck,
  Volume2,
  Compass,
  Footprints,
  EyeOff,
  Accessibility,
  FileText,
  CheckCircle2,
  XCircle,
  Workflow,
  Sparkles,
} from "lucide-react";

interface ExplainabilityCardProps {
  entity: SemanticEntity;
  vesselId?: string;
  className?: string;
  defaultCategory?: string;
}

export const ExplainabilityCard: React.FC<ExplainabilityCardProps> = ({
  entity,
  vesselId = "msc-bellissima",
  className = "",
  defaultCategory = "quiet",
}) => {
  const intel: ExplainableCabinIntelligence = ExplainabilityEngine.explainCabin(entity, vesselId);
  const [activeKey, setActiveKey] = useState<string>(defaultCategory);
  const [activeTab, setActiveTab] = useState<"walkthrough" | "evidence" | "sources">("walkthrough");

  const currentScore: ExplainableScore = intel.scores[activeKey] || intel.scores.quiet;

  const getScoreBadge = (score: number | null) => {
    if (score === null) return "bg-slate-50 text-slate-500 border-slate-300 dark:bg-slate-800 dark:text-slate-400";
    if (score >= 88) return "bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-400";
    if (score >= 75) return "bg-blue-50 text-blue-700 border-blue-300 dark:bg-blue-950/60 dark:text-blue-400";
    if (score >= 60) return "bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950/60 dark:text-amber-400";
    return "bg-rose-50 text-rose-700 border-rose-300 dark:bg-rose-950/60 dark:text-rose-400";
  };

  const getCategoryIcon = (key: string) => {
    switch (key) {
      case "quiet": return <Volume2 className="w-3.5 h-3.5" />;
      case "motion": return <Compass className="w-3.5 h-3.5" />;
      case "walking": return <Footprints className="w-3.5 h-3.5" />;
      case "privacy": return <EyeOff className="w-3.5 h-3.5" />;
      case "accessibility": return <Accessibility className="w-3.5 h-3.5" />;
      default: return <Sparkles className="w-3.5 h-3.5" />;
    }
  };

  return (
    <div className={`p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-white/10 shadow-xl space-y-6 ${className}`}>
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-[#C58A46]/10 text-[#C58A46] border border-[#C58A46]/30">
              EXPLAINABILITY ENGINE (EVIDENCE → RULE → SCORE)
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-300">
              ZERO-AI / DETERMINISTIC
            </span>
          </div>
          <h3 className="font-display text-2xl font-bold text-slate-900 dark:text-white">
            Cabin {intel.cabin_id} Decision Trace
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {intel.deck_name} • Scores remain unavailable until every required fact is admitted.
          </p>
        </div>

        {/* Global Confidence Pill — only when a backed confidence exists (P0-H2) */}
        {intel.global_epistemic_confidence !== null && (
          <div className="flex items-center gap-2 p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-white/10">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400 font-bold">Source Confidence</div>
              <div className="font-mono text-sm font-bold text-slate-800 dark:text-white">
                {intel.global_epistemic_confidence === null ? "Unavailable" : "Computed confidence available"}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        {Object.values(intel.scores).map((sc) => {
          const isActive = sc.key === activeKey;
          return (
            <button
              key={sc.key}
              onClick={() => setActiveKey(sc.key)}
              className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer select-none ${
                isActive
                  ? "bg-[#0C1B2A] text-white shadow-md"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
            >
              {getCategoryIcon(sc.key)}
              <span>{sc.name.split(" ")[0]}</span>
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-bold ${
                isActive ? "bg-white/20 text-white" : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
              }`}>
                {sc.final_score ?? "—"}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Dimension Header */}
      <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-[10px] uppercase font-mono text-slate-400 font-bold">Inspected Dimension</div>
          <h4 className="font-display text-xl font-bold text-slate-900 dark:text-white">
            {currentScore.name}
          </h4>
        </div>

        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-xl text-sm font-mono font-bold border ${getScoreBadge(currentScore.final_score)}`}>
            {currentScore.final_score === null
              ? "Score unavailable"
              : `Score: ${currentScore.final_score} / 100 (${currentScore.grade})`}
          </span>
        </div>
      </div>

      {/* Sub Tabs: Walkthrough vs Evidence vs Sources */}
      <div className="flex items-center gap-4 border-b border-slate-200 dark:border-white/10 pb-2 text-xs font-semibold">
        <button
          onClick={() => setActiveTab("walkthrough")}
          className={`pb-1 transition-colors cursor-pointer ${
            activeTab === "walkthrough" ? "text-[#C58A46] border-b-2 border-[#C58A46]" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Arithmetic Walkthrough ({currentScore.steps.length} Steps)
        </button>
        <button
          onClick={() => setActiveTab("evidence")}
          className={`pb-1 transition-colors cursor-pointer ${
            activeTab === "evidence" ? "text-[#C58A46] border-b-2 border-[#C58A46]" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Evidence Classification ({currentScore.positive_evidence.length + currentScore.negative_evidence.length})
        </button>
        <button
          onClick={() => setActiveTab("sources")}
          className={`pb-1 transition-colors cursor-pointer ${
            activeTab === "sources" ? "text-[#C58A46] border-b-2 border-[#C58A46]" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Primary Sources ({currentScore.sources.length})
        </button>
      </div>

      {/* TAB 1: Arithmetic Walkthrough */}
      {activeTab === "walkthrough" && (
        <div className="space-y-3">
          {currentScore.steps.map((step) => (
            <div
              key={step.step_number}
              className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 shadow-xs space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-mono font-bold flex items-center justify-center text-slate-500">
                    {step.step_number}
                  </span>
                  <span className="font-bold text-xs text-slate-900 dark:text-white">
                    {step.rule_title}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">({step.rule_id})</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-lg text-xs font-mono font-bold ${
                    step.delta > 0 ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400" :
                    step.delta < 0 ? "bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400" :
                    "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                  }`}>
                    {step.delta > 0 ? `+${step.delta}` : step.delta}
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-400">
                    = {step.running_total}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 pl-7">
                {step.rationale}
              </p>

              {/* Grounded Evidence Chain Trace */}
              {step.provenance.graph_edge && (
                <div className="ml-7 p-2 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-white/5 text-[10px] font-mono space-y-1">
                  <div className="flex items-center gap-1.5 text-slate-500">
                    <Workflow className="w-3 h-3 text-[#C58A46]" />
                    <span className="text-slate-400">Graph Edge:</span>
                    <span className="text-sky-400 font-bold">{step.provenance.graph_edge}</span>
                  </div>
                  {(step.provenance.artifact_id || step.provenance.source_title || step.provenance.page != null) && (
                    <div className="flex items-center justify-between text-slate-400">
                      {(step.provenance.source_title || step.provenance.artifact_id) && (
                        <span>Artifact: {step.provenance.source_title || step.provenance.artifact_id}</span>
                      )}
                      {step.provenance.page != null && (
                        <span className="text-emerald-400 font-bold">PDF Page {step.provenance.page}</span>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: Evidence Classification */}
      {activeTab === "evidence" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Positive Evidence */}
          <div className="p-4 rounded-2xl bg-emerald-50/40 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/40 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-800 dark:text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Positive Factors (+Boosts)</span>
            </div>
            <div className="space-y-2">
              {currentScore.positive_evidence.map((ev, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-emerald-100 dark:border-emerald-900/40 text-xs space-y-1">
                  <div className="font-semibold text-slate-800 dark:text-slate-200">{ev.raw_finding}</div>
                  {(ev.source_title || ev.artifact_id) && (
                    <div className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400">
                      {ev.source_title || ev.artifact_id}
                      {ev.page != null ? ` • Page ${ev.page}` : ""}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Negative Evidence */}
          <div className="p-4 rounded-2xl bg-rose-50/40 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-800/40 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-rose-800 dark:text-rose-300">
              <XCircle className="w-4 h-4 text-rose-500" />
              <span>Negative Factors (-Penalties)</span>
            </div>
            <div className="space-y-2">
              {currentScore.negative_evidence.length > 0 ? (
                currentScore.negative_evidence.map((ev, i) => (
                  <div key={i} className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-rose-100 dark:border-rose-900/40 text-xs space-y-1">
                    <div className="font-semibold text-slate-800 dark:text-slate-200">{ev.raw_finding}</div>
                    {(ev.source_title || ev.artifact_id) && (
                      <div className="text-[10px] font-mono text-rose-600 dark:text-rose-400">
                        {ev.source_title || ev.artifact_id}
                        {ev.page != null ? ` • Page ${ev.page}` : ""}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-400 italic">No negative penalties detected for this dimension.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Primary Sources */}
      {activeTab === "sources" && (
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-white/10 space-y-2">
          <div className="text-xs font-bold text-slate-800 dark:text-white mb-2">
            Referenced Sources
          </div>
          <div className="space-y-2">
            {currentScore.sources.length > 0 ? (
              currentScore.sources.map((src, i) => (
                <div key={i} className="flex items-center gap-2 text-xs font-mono text-slate-700 dark:text-slate-300">
                  <FileText className="w-4 h-4 text-[#C58A46]" />
                  <span>{src}</span>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 italic">
                No source document is linked to these rules.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[11px] text-slate-400 font-mono border-t border-slate-100 dark:border-white/5">
        <span>Rule-based scoring · sources shown where linked</span>
      </div>
    </div>
  );
};

export default ExplainabilityCard;
