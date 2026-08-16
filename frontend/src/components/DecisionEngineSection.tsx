import React, { useState } from 'react';
import { Compass, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck, RefreshCw } from 'lucide-react';
import { PRECOMPUTED_DECISIONS, type DecisionCardData } from '../generated/decisions';

interface DecisionEngineSectionProps {
  onSelectShip?: (slug: string) => void;
}

export const DecisionEngineSection: React.FC<DecisionEngineSectionProps> = ({ onSelectShip }) => {
  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const decision: DecisionCardData = PRECOMPUTED_DECISIONS[selectedIdx] || PRECOMPUTED_DECISIONS[0];

  return (
    <section className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-amber-700" />
            Deterministic Decision Engine · Chapter III
          </div>
          <h2 className="font-serif text-3xl md:text-4xl text-slate-900 font-normal tracking-tight">
            Verlässliche Schiffsentscheidungen.
          </h2>
          <p className="text-slate-600 mt-1 max-w-2xl text-sm md:text-base">
            Keine KI-Improvisation. 100% deterministisch berechnet aus Generalplänen, Lärmprofilen und Werftdaten.
          </p>
        </div>

        {/* Tab Selection */}
        <div className="flex gap-2 p-1 bg-slate-100 rounded-lg border border-slate-200 self-start">
          {PRECOMPUTED_DECISIONS.map((d, idx) => (
            <button
              key={d.decisionId}
              onClick={() => setSelectedIdx(idx)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                selectedIdx === idx
                  ? 'bg-white text-slate-900 shadow-sm border border-slate-200'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {d.candidateEntity.replace('MSC ', '')}
            </button>
          ))}
        </div>
      </div>

      {/* Decision Card Container */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        {/* Header Bar */}
        <div className="bg-slate-900 text-white px-6 py-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <div>
              <div className="text-xs text-slate-400 uppercase tracking-wider font-mono">Vergleichsentscheidung</div>
              <div className="text-base font-semibold text-white">
                {decision.targetEntity} <span className="text-slate-400 font-normal">gegen</span> {decision.candidateEntity}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-semibold">
              {decision.verdict}
            </span>
            <span className="text-xs font-mono text-slate-400">
              Konfidenz: <span className="text-white font-semibold">{decision.confidenceScore}%</span>
            </span>
          </div>
        </div>

        {/* Card Body (The 5-Point Standard) */}
        <div className="p-6 md:p-8 space-y-6">
          {/* 1. Warum */}
          <div className="border-b border-slate-100 pb-5">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">1. Warum diese Empfehlung?</div>
            <p className="font-serif text-lg md:text-xl text-slate-900 italic font-normal leading-relaxed">
              &ldquo;{decision.warum}&rdquo;
            </p>
          </div>

          {/* 2 & 3: Gründe und Unterschiede */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-b border-slate-100 pb-6">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                2. Die 3 wichtigsten Gründe
              </div>
              <ul className="space-y-2.5 text-sm text-slate-700">
                {decision.gruendeTop3.map((g, idx) => (
                  <li key={idx} className="flex items-start gap-2.5">
                    <span className="font-mono text-xs text-slate-400 mt-0.5">{idx + 1}.</span>
                    <span>{g}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                <RefreshCw className="w-4 h-4 text-blue-600" />
                3. Die 2 baulichen Unterschiede
              </div>
              <ul className="space-y-2.5 text-sm text-slate-700">
                {decision.unterschiede2.map((u, idx) => (
                  <li key={idx} className="flex items-start gap-2.5">
                    <span className="font-mono text-xs text-slate-400 mt-0.5">{idx + 1}.</span>
                    <span>{u}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* 4 & 5: Risiko und Nächster Schritt */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-1">
            <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl">
              <div className="text-xs font-semibold uppercase tracking-wider text-amber-900 mb-1.5 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                4. Das konkrete Risiko (Trade-off)
              </div>
              <p className="text-sm text-amber-950 font-normal leading-relaxed">
                {decision.risiko1}
              </p>
            </div>

            <div className="p-4 bg-slate-900 text-white rounded-xl flex flex-col justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                  5. Nächster empfohlener Schritt
                </div>
                <p className="text-sm text-slate-200 font-normal">
                  {decision.naechsterSchritt}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs text-slate-400">
                <span className="font-mono">{decision.decisionId}</span>
                <span className="text-emerald-400 font-medium">100% Deterministisch</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
