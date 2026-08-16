import React, { useState } from 'react';
import {
  Compass,
  Anchor,
  Clock,
  CheckCircle2,
  AlertCircle,
  Eye,
  Calendar,
  Sparkles,
  Layers,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import {
  CONTEXT_BRIEFINGS,
  type ContextBriefingData,
} from '../generated/context_engine';

export const ContextBriefingDashboard: React.FC = () => {
  const [selectedPhaseKey, setSelectedPhaseKey] = useState<'pre12' | 't3'>('pre12');
  const briefing: ContextBriefingData =
    CONTEXT_BRIEFINGS[selectedPhaseKey] || CONTEXT_BRIEFINGS.pre12;

  return (
    <section id="context-briefing" className="py-12 px-4 max-w-6xl mx-auto">
      {/* Bridge Officer Tim Proactive Context Dashboard */}
      <div className="bg-slate-900 text-white rounded-3xl p-6 md:p-10 shadow-xl border border-slate-800 space-y-8 relative overflow-hidden">
        {/* Subtle Ambient Glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Top Header & Simulation Switcher */}
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Compass className="w-6 h-6 animate-[spin_30s_linear_infinite]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400 font-semibold flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  Context Engine · Bridge Officer Tim
                </span>
                <span className="text-slate-500 text-xs">|</span>
                <span className="text-xs text-slate-400 font-mono">{briefing.dateDisplay}</span>
              </div>
              <h3 className="text-xl md:text-2xl font-serif font-normal text-white mt-0.5">
                Proactive Journey Assessment
              </h3>
            </div>
          </div>

          {/* Phase Simulation Selector */}
          <div className="flex flex-wrap gap-1.5 p-1 bg-slate-800/80 rounded-xl border border-slate-700/60 self-start md:self-auto">
            <button
              onClick={() => setSelectedPhaseKey('pre12')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                selectedPhaseKey === 'pre12'
                  ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              T-12 Tage (Vorbereitung)
            </button>
            <button
              onClick={() => setSelectedPhaseKey('t3')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-all ${
                selectedPhaseKey === 't3'
                  ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              T-3 Tage (Check-in offen)
            </button>
          </div>
        </div>

        {/* Morning Greeting & Proactive Status */}
        <div className="space-y-2">
          <div className="text-lg md:text-xl font-serif text-slate-100">
            {briefing.greetingLine}
          </div>
          <p className="text-xs md:text-sm text-slate-300 leading-relaxed font-sans">
            {briefing.statusHeadline}
          </p>
        </div>

        {/* BOT Noticed Observations */}
        {briefing.proactiveBotNotices.length > 0 && (
          <div className="space-y-3">
            {briefing.proactiveBotNotices.map((notice, idx) => (
              <div
                key={idx}
                className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex items-start gap-3 text-xs text-amber-200 leading-relaxed"
              >
                <Eye className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{notice}</span>
              </div>
            ))}
          </div>
        )}

        {/* Top 3 Outstanding Priorities Grid */}
        <div className="space-y-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 font-mono flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              Heutige Top-Prioritäten (Fokus auf maximal 3 Handlungen)
            </span>
            <span className="text-slate-500 text-[11px]">Priority Engine Capped</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {briefing.topPriorities.map((task, i) => (
              <div
                key={task.taskId}
                className="p-5 bg-white/5 border border-white/10 rounded-2xl flex flex-col justify-between space-y-3 hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 text-[10px] font-mono font-bold rounded-md uppercase">
                      {task.priority.split('(')[0].trim()}
                    </span>
                    <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      {task.deadlineDisplay}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-white leading-snug">
                    {task.title}
                  </h4>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    {task.reason}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 text-[11px] text-amber-400 font-medium flex items-center gap-1">
                  <ChevronRight className="w-3.5 h-3.5" />
                  <span>{task.recommendedAction}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Memory Layer (Completed Milestones) & Bridge Sign-off */}
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1.5">
            <div className="text-[11px] font-mono uppercase text-slate-400 font-semibold flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Memory Layer · Bereits gesichert
            </div>
            <div className="flex flex-wrap gap-2">
              {briefing.completedMilestones.map((m, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs rounded-lg flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                  {m}
                </span>
              ))}
            </div>
          </div>

          <div className="text-xs md:text-sm text-amber-400 font-serif font-medium tracking-wide flex items-center gap-2 shrink-0 self-start md:self-auto">
            <Anchor className="w-4 h-4 text-amber-400" />
            <span>{briefing.signOffPhrase}</span>
          </div>
        </div>
      </div>
    </section>
  );
};
