import React, { useState } from "react";
import { CabinIntelligence, CabinIntelligenceEngine, ScoreItem } from "./CabinIntelligenceEngine";
import { SemanticEntity } from "../semantic-deck/types";
import {
  ShieldCheck,
  Volume2,
  Compass,
  Footprints,
  EyeOff,
  Accessibility,
  Users,
  Heart,
  Sparkles,
  Info,
  Layers,
} from "lucide-react";

interface CabinIntelligenceCardProps {
  entity: SemanticEntity;
  vesselId?: string;
  className?: string;
}

export const CabinIntelligenceCard: React.FC<CabinIntelligenceCardProps> = ({
  entity,
  vesselId = "msc-bellissima",
  className = "",
}) => {
  const intel: CabinIntelligence = CabinIntelligenceEngine.evaluateCabin(entity, vesselId);
  const [expandedKey, setExpandedKey] = useState<string | null>("quiet");

  const scoreItems: ScoreItem[] = [
    intel.quiet_score,
    intel.motion_score,
    intel.walking_score,
    intel.privacy_score,
    intel.accessibility_score,
    intel.family_score,
    intel.couple_score,
  ];

  const getScoreColor = (score: number | null) => {
    if (score === null) return "text-slate-500 bg-slate-50 border-slate-200 dark:bg-slate-800 dark:border-slate-700";
    if (score >= 88) return "text-emerald-600 bg-emerald-50 border-emerald-200 dark:bg-emerald-950/50 dark:border-emerald-800 dark:text-emerald-400";
    if (score >= 75) return "text-blue-600 bg-blue-50 border-blue-200 dark:bg-blue-950/50 dark:border-blue-800 dark:text-blue-400";
    if (score >= 60) return "text-amber-600 bg-amber-50 border-amber-200 dark:bg-amber-950/50 dark:border-amber-800 dark:text-amber-400";
    return "text-rose-600 bg-rose-50 border-rose-200 dark:bg-rose-950/50 dark:border-rose-800 dark:text-rose-400";
  };

  const getIcon = (key: string) => {
    switch (key) {
      case "quiet": return <Volume2 className="w-4 h-4 text-emerald-500" />;
      case "motion": return <Compass className="w-4 h-4 text-blue-500" />;
      case "walking": return <Footprints className="w-4 h-4 text-purple-500" />;
      case "privacy": return <EyeOff className="w-4 h-4 text-indigo-500" />;
      case "accessibility": return <Accessibility className="w-4 h-4 text-teal-500" />;
      case "family": return <Users className="w-4 h-4 text-amber-500" />;
      case "couple": return <Heart className="w-4 h-4 text-rose-500" />;
      default: return <Sparkles className="w-4 h-4 text-gold" />;
    }
  };

  return (
    <div className={`p-6 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-white/10 shadow-xl space-y-6 ${className}`}>
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-gold/10 text-gold border border-gold/30">
              CABIN INTELLIGENCE V1
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-300">
              EVIDENCE-GATED
            </span>
          </div>
          <h3 className="font-display text-2xl font-bold text-slate-900 dark:text-white">
            Cabin {intel.cabin_id} Intelligence Dossier
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {intel.deck_number == null
              ? "Cabin location and classification unavailable"
              : `${intel.deck_name} (Deck ${intel.deck_number}) • ${intel.classification ?? "Unavailable"} • ${intel.side ?? "Unknown side"}`}
          </p>
        </div>

        {/* Epistemic Confidence Pill */}
        <div className="flex items-center gap-2 p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-white/10">
          <ShieldCheck className="w-5 h-5 text-emerald-500" />
          <div>
            <div className="text-[10px] uppercase font-mono text-slate-400 font-bold">Epistemic Confidence</div>
            <div className="font-mono text-sm font-bold text-slate-800 dark:text-white">
              {intel.epistemic_confidence == null ? "Unavailable" : "Computed confidence available"}
            </div>
          </div>
        </div>
      </div>

      {/* Grid of Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {scoreItems.map((item) => {
          const isExpanded = expandedKey === item.key;
          const colorClass = getScoreColor(item.score);

          return (
            <div
              key={item.key}
              onClick={() => setExpandedKey(isExpanded ? null : item.key)}
              className={`p-4 rounded-2xl border transition-all cursor-pointer select-none ${
                isExpanded
                  ? "bg-slate-50 dark:bg-slate-800/90 border-[#C58A46] shadow-md ring-1 ring-[#C58A46]/30"
                  : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-white/10 hover:border-slate-300"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800">
                    {getIcon(item.key)}
                  </div>
                  <span className="font-semibold text-xs text-slate-800 dark:text-slate-200">
                    {item.name}
                  </span>
                </div>
                <span className={`px-2 py-0.5 rounded-lg text-xs font-mono font-bold border ${colorClass}`}>
                  {item.score ?? "—"}
                </span>
              </div>

              <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                {item.summary}
              </p>

              {/* Collapsible Factor Breakdown */}
              {isExpanded && (
                <div className="mt-3 pt-3 border-t border-slate-200 dark:border-white/10 space-y-1.5">
                  <div className="text-[10px] font-mono uppercase font-bold text-slate-400">
                    Admitted rule factors:
                  </div>
                  {item.factors.map((f, fIdx) => (
                    <div key={fIdx} className="flex items-start gap-1.5 text-[11px] text-slate-700 dark:text-slate-300 leading-snug">
                      <span className="text-gold font-bold">•</span>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>{item.grade}</span>
                <span>{isExpanded ? "Less ▲" : "Why? ▼"}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Explanations & Reasoning Summary Box */}
      {intel.all_reasoning.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/80 dark:border-amber-800/50 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-900 dark:text-amber-300">
            <Info className="w-4 h-4 text-amber-600" />
            <span>Key Maritime Intelligence Findings</span>
          </div>
          <div className="space-y-1 pl-6">
            {intel.all_reasoning.map((r, rIdx) => (
              <p key={rIdx} className="text-xs text-amber-800 dark:text-amber-200 leading-relaxed list-item">
                {r}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Provenance Footer */}
      <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-[11px] text-slate-400 font-mono border-t border-slate-100 dark:border-white/5">
        <div className="flex items-center gap-2">
          <Layers className="w-3.5 h-3.5 text-slate-400" />
          <span>{intel.provenance_sources.length > 0
            ? `Sources: ${intel.provenance_sources.join(" • ")}`
            : "No admitted source chain available"}</span>
        </div>
        <span className="text-slate-500 font-bold">Rules run only on admitted inputs</span>
      </div>
    </div>
  );
};

export default CabinIntelligenceCard;
