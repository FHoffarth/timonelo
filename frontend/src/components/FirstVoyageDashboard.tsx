import React, { useState } from 'react';
import {
  Compass,
  Anchor,
  ShieldCheck,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Sparkles,
  Award,
  Layers,
  ChevronRight,
  HeartHandshake,
  Activity,
} from 'lucide-react';
import {
  FIRST_VOYAGE_DATA,
  type FirstVoyageDashboardData,
  type StageTimelineDetailData,
} from '../generated/first_voyage';

export const FirstVoyageDashboard: React.FC = () => {
  const data: FirstVoyageDashboardData = FIRST_VOYAGE_DATA;
  const [selectedStageKey, setSelectedStageKey] = useState<'preparation' | 'embarkation' | 'home'>('preparation');

  const stage: StageTimelineDetailData =
    data.stages[selectedStageKey] || data.stages.preparation;

  return (
    <section id="first-voyage" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-900 border border-blue-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-blue-700" />
            First Voyage Simulation · Doorstep to Homecoming (Sprint 11)
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Vollkommene Reisesicherheit. Von Anfang bis Ende.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Ein einziger, ruhiger Begleiter von der ersten Flugidee bis zur Haustür: Keine Unsicherheit, keine Hektik, 100% verifizierte Evidenz.
          </p>
        </div>
      </div>

      {/* Main Container */}
      <div className="bg-slate-950 text-white border border-slate-800 rounded-3xl p-6 md:p-10 shadow-2xl space-y-10 relative overflow-hidden">
        {/* Ambient Glows */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* 1. JOURNEY READINESS HEALTH SCORE (82%) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 bg-slate-900/90 border border-slate-800 rounded-2xl">
          <div className="flex flex-col justify-between border-b md:border-b-0 md:border-r border-slate-800 pb-4 md:pb-0 md:pr-6">
            <div>
              <div className="text-[11px] font-mono uppercase text-slate-400 font-semibold flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-400" />
                Operational Readiness Score
              </div>
              <div className="text-4xl md:text-5xl font-serif font-bold text-emerald-400 mt-2">
                {data.readiness.totalScore}%
              </div>
              <div className="text-xs text-slate-300 font-mono mt-1">
                {data.readiness.statusLabel}
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-3 italic">
              » Kein Gamification-Score, sondern rein operative Einsatzbereitschaft. «
            </p>
          </div>

          <div className="space-y-2 md:col-span-2">
            <div className="text-xs font-semibold text-white uppercase font-mono tracking-wider">
              Verifizierte Meilensteine & Punktabzüge:
            </div>
            <div className="space-y-1.5 text-xs">
              {data.readiness.verifiedItems.map((item, idx) => (
                <div key={idx} className="flex items-start gap-2 text-emerald-300">
                  <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                  <span>{item}</span>
                </div>
              ))}
              {data.readiness.deductions.map((ded, idx) => (
                <div key={idx} className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl space-y-1 text-amber-200 mt-2">
                  <div className="flex items-center justify-between font-semibold">
                    <span>[-{ded.pointsDeducted}%] {ded.itemName}</span>
                    <span className="text-[10px] font-mono uppercase">Offener Schritt</span>
                  </div>
                  <p className="text-xs text-slate-300">{ded.reason}</p>
                  <p className="text-[11px] text-amber-300 font-mono">💡 {ded.actionToResolve}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 2. CHRONOLOGICAL STAGE LIFECYCLE SIMULATOR */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Chronologische Reisephasen-Simulation</span>
            </div>

            {/* Stage Selector */}
            <div className="flex flex-wrap gap-1.5 p-1 bg-slate-900 rounded-xl border border-slate-800">
              <button
                onClick={() => setSelectedStageKey('preparation')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                  selectedStageKey === 'preparation'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                T-12 Vorbereitung
              </button>
              <button
                onClick={() => setSelectedStageKey('embarkation')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                  selectedStageKey === 'embarkation'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                Einschiffung Shanghai
              </button>
              <button
                onClick={() => setSelectedStageKey('home')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                  selectedStageKey === 'home'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                Heimkehr nach Frankfurt
              </button>
            </div>
          </div>

          {/* Active Stage Details Card */}
          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-3">
              <div>
                <h3 className="text-xl font-serif text-white">{stage.title}</h3>
                <p className="text-xs text-slate-300 mt-0.5">Ziel: {stage.objective}</p>
              </div>
              <span className="text-xs font-mono px-3 py-1 bg-amber-500/20 text-amber-300 rounded-lg self-start">
                {stage.duration}
              </span>
            </div>

            <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 leading-relaxed">
              <span className="text-amber-400 font-semibold">Morgen-Briefing der Brücke: </span>
              {stage.botBriefing}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
              <div className="space-y-2">
                <div className="text-[11px] uppercase font-mono text-emerald-400 font-semibold">
                  Erledigte Meilensteine:
                </div>
                <ul className="space-y-1 text-xs text-slate-300">
                  {stage.completed.map((c, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <div className="text-[11px] uppercase font-mono text-amber-400 font-semibold">
                  Anstehende Handlungen:
                </div>
                <ul className="space-y-1 text-xs text-slate-300">
                  {stage.outstanding.map((o, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <ChevronRight className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                      <span>{o}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="p-3 bg-rose-950/30 border border-rose-900/40 rounded-xl text-xs text-rose-300 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>Anti-Regret Leitlinie: {stage.antiRegret}</span>
            </div>
          </div>
        </div>

        {/* 3. ANTI-REGRET REGISTER */}
        <div className="space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
              Anti-Regret Register · Systematische Vermeidung von Reise-Reue
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.antiRegrets.map((reg, idx) => (
              <div key={idx} className="p-5 bg-white/5 border border-white/10 rounded-2xl space-y-2">
                <div className="text-xs font-mono font-semibold uppercase text-amber-400">
                  Phase: {reg.stageName}
                </div>
                <p className="text-xs text-rose-300 leading-relaxed">
                  <span className="font-semibold">Typische Falle:</span> {reg.trap}
                </p>
                <p className="text-xs text-emerald-300 leading-relaxed pt-1 border-t border-white/10">
                  <span className="font-semibold">Vermeidungs-Regel:</span> {reg.prevention}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 4. PRODUCT QUALITY AUDIT (98.5% UX SCORE) */}
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="text-[11px] font-mono uppercase text-blue-400 font-semibold flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5" />
              Internal Product Quality & UX Health Audit
            </div>
            <div className="text-sm font-semibold text-white">
              UX Score: {data.audit.totalUxScore}% · {data.audit.clarityVerdict}
            </div>
            <p className="text-xs text-slate-400 max-w-2xl">
              {data.audit.summary}
            </p>
          </div>
          <div className="text-xs font-mono text-slate-400 shrink-0 self-start md:self-auto">
            Unnötige Klicks: {data.audit.unnecessaryClicksCount} · Fragen: {data.audit.unnecessaryQuestionsAsked}
          </div>
        </div>

        {/* 5. FINAL FAREWELL */}
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 italic max-w-2xl">
            » {data.finalFarewell} «
          </div>
          <div className="text-xs md:text-sm text-amber-400 font-serif font-medium tracking-wide flex items-center gap-2 shrink-0">
            <Anchor className="w-4 h-4 text-amber-400" />
            <span>Ich bleibe auf der Brücke.</span>
          </div>
        </div>
      </div>
    </section>
  );
};
