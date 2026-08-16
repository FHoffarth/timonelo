import React, { useState } from 'react';
import {
  Compass,
  Anchor,
  Radio,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Eye,
  ShieldCheck,
} from 'lucide-react';
import {
  PRECOMPUTED_BOT_BRIEFINGS,
  type BridgeBriefingData,
} from '../generated/bridge_briefing';

export const BridgeBriefingCard: React.FC = () => {
  const [selectedPhase, setSelectedPhase] = useState<'pre12' | 'embarkation' | 'seaday' | 'yokohama'>('pre12');
  const briefing: BridgeBriefingData =
    PRECOMPUTED_BOT_BRIEFINGS[selectedPhase] || PRECOMPUTED_BOT_BRIEFINGS.pre12;

  return (
    <section id="bridge-briefing" className="py-12 px-4 max-w-6xl mx-auto">
      {/* Container with Maritime Bridge Logbook Style */}
      <div className="relative bg-slate-900 text-white rounded-3xl p-6 md:p-10 shadow-xl border border-slate-800 overflow-hidden">
        {/* Subtle Decorative Maritime Radar Rings */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

        {/* Top Header Row */}
        <div className="relative flex flex-col md:flex-row md:items-center justify-between pb-6 mb-6 border-b border-slate-800 gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Compass className="w-6 h-6 animate-[spin_30s_linear_infinite]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400 font-semibold flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  Bridge Officer Tim (BOT) · Logbuch
                </span>
                <span className="text-slate-500 text-xs">|</span>
                <span className="text-xs text-slate-400 font-mono">{briefing.dateDisplay}</span>
              </div>
              <h3 className="text-xl md:text-2xl font-serif font-normal text-white mt-0.5">
                Bridge Briefing
              </h3>
            </div>
          </div>

          {/* Day / Phase Selector */}
          <div className="flex flex-wrap gap-1.5 p-1 bg-slate-800/80 rounded-xl border border-slate-700/60 self-start md:self-auto">
            <button
              onClick={() => setSelectedPhase('pre12')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                selectedPhase === 'pre12'
                  ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              T-12 Tage
            </button>
            <button
              onClick={() => setSelectedPhase('embarkation')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                selectedPhase === 'embarkation'
                  ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Einschiffung
            </button>
            <button
              onClick={() => setSelectedPhase('seaday')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                selectedPhase === 'seaday'
                  ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Seetag
            </button>
            <button
              onClick={() => setSelectedPhase('yokohama')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                selectedPhase === 'yokohama'
                  ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Hafentag Tokio
            </button>
          </div>
        </div>

        {/* Greeting & Phase Banner */}
        <div className="relative mb-8">
          <div className="text-lg md:text-xl font-serif text-slate-100 font-normal">
            {briefing.greetingLine}
          </div>
          <div className="text-xs font-mono text-slate-400 mt-1">
            {briefing.phaseContext}
          </div>
        </div>

        {/* Proactive Notices ("Mir ist etwas aufgefallen...") */}
        {briefing.proactiveNotices.length > 0 && (
          <div className="relative mb-8 space-y-3">
            {briefing.proactiveNotices.map((notice) => (
              <div
                key={notice.noticeId}
                className="p-4 md:p-5 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex items-start gap-3.5"
              >
                <div className="p-2 rounded-xl bg-amber-500/20 text-amber-300 shrink-0 mt-0.5">
                  <Eye className="w-4 h-4" />
                </div>
                <div className="space-y-1">
                  <div className="text-xs font-semibold text-amber-300 uppercase font-mono tracking-wider">
                    {notice.headline}
                  </div>
                  <div className="text-xs md:text-sm text-slate-200 leading-relaxed">
                    {notice.content}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Daily Focus Points */}
        <div className="relative mb-8">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono mb-4 flex items-center gap-2">
            <Radio className="w-3.5 h-3.5 text-blue-400" />
            Heutige Fokuspunkte & Empfehlungen
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {briefing.dailyFocusPoints.map((point, idx) => (
              <div
                key={idx}
                className="p-4 bg-white/5 border border-white/10 rounded-2xl flex flex-col justify-between"
              >
                <div className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-amber-400/20 text-amber-300 text-xs font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <p className="text-xs text-slate-200 leading-relaxed">
                    {point}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Maritime Insight & Signature Sign-Off */}
        <div className="relative pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 italic max-w-xl">
            » {briefing.maritimeInsight} «
          </div>
          <div className="text-xs md:text-sm text-amber-400 font-serif font-medium tracking-wide flex items-center gap-2 shrink-0">
            <Anchor className="w-4 h-4 text-amber-400" />
            <span>{briefing.signOff}</span>
          </div>
        </div>
      </div>
    </section>
  );
};
