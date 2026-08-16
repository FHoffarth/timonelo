import React, { useState } from 'react';
import {
  Compass,
  Anchor,
  Clock,
  Sparkles,
  Utensils,
  Sun,
  Coffee,
  Shield,
  Layers,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  Lock,
  MessageSquare,
  LifeBuoy,
} from 'lucide-react';
import {
  CRUISE_ASSISTANT_DATA,
  type CruiseAssistantDashboardData,
  type QuickActionData,
} from '../generated/assistant_engine';

export const BridgeOfficerTimDashboard: React.FC = () => {
  const data: CruiseAssistantDashboardData = CRUISE_ASSISTANT_DATA;
  const [activeQuickTab, setActiveQuickTab] = useState<'lunch' | 'sunset' | 'coffee' | 'muster'>('lunch');
  const [showTwoHours, setShowTwoHours] = useState<boolean>(true);

  const selectedAction: QuickActionData =
    data.quickActions[activeQuickTab] || data.quickActions.lunch;

  return (
    <section id="cruise-assistant" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-amber-700" />
            Cruise Concierge · Chapter III Sprint 10
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Bridge Officer Tim · Persönlicher Concierge.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Keine langen Suchen, keine Vermutungen an Bord: Ein Klick liefert die ruhigste Bar, das staufreie Mittagessen oder die optimale Sonnenuntergangslage.
          </p>
        </div>
      </div>

      {/* Main Luxury Command Console Container */}
      <div className="bg-slate-950 text-white border border-slate-800 rounded-3xl p-6 md:p-10 shadow-2xl space-y-10 relative overflow-hidden">
        {/* Subtle Ambient Radial Lights */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* 1. TODAY'S DAILY MISSION */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-amber-400">
                Tages-Mission der Brücke · {data.dailyMission.phaseName}
              </span>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              {data.dailyMission.estimatedDurationDisplay}
            </span>
          </div>

          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl space-y-4">
            <div>
              <h3 className="text-xl font-serif text-white font-normal">
                {data.dailyMission.missionTitle}
              </h3>
              <p className="text-xs text-slate-300 font-mono mt-1">
                Fokus: {data.dailyMission.currentObjective}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="space-y-2">
                <div className="text-[11px] uppercase font-mono text-emerald-400 font-semibold">
                  Empfohlene Vorgehensweise:
                </div>
                <ul className="space-y-1.5 text-xs text-slate-200">
                  {data.dailyMission.recommendedActions.map((act, i) => (
                    <li key={i} className="leading-relaxed">
                      {act}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <div className="text-[11px] uppercase font-mono text-rose-400 font-semibold">
                  Typische Fehler (Meiden):
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {data.dailyMission.negativeIntelligenceAvoid.map((av, i) => (
                    <li key={i} className="leading-relaxed">
                      {av}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* 2. QUICK ACTIONS / ASK BOT */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
              <span>Schnell-Aktionen · Fragen an Bridge Officer Tim</span>
            </div>

            {/* Action Switcher Tabs */}
            <div className="flex flex-wrap gap-1.5 p-1 bg-slate-900 rounded-xl border border-slate-800">
              <button
                onClick={() => setActiveQuickTab('lunch')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 ${
                  activeQuickTab === 'lunch'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <Utensils className="w-3 h-3" />
                <span>Mittagessen</span>
              </button>
              <button
                onClick={() => setActiveQuickTab('sunset')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 ${
                  activeQuickTab === 'sunset'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <Sun className="w-3 h-3" />
                <span>Sonnenuntergang</span>
              </button>
              <button
                onClick={() => setActiveQuickTab('coffee')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 ${
                  activeQuickTab === 'coffee'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <Coffee className="w-3 h-3" />
                <span>Ruhiger Espresso</span>
              </button>
              <button
                onClick={() => setActiveQuickTab('muster')}
                className={`px-3 py-1.5 text-xs rounded-lg transition-all flex items-center gap-1.5 ${
                  activeQuickTab === 'muster'
                    ? 'bg-amber-500 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <Shield className="w-3 h-3" />
                <span>Musterstation F</span>
              </button>
            </div>
          </div>

          {/* Quick Action Answer Display */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="text-xs md:text-sm text-slate-200 leading-relaxed font-sans">
              <span className="text-amber-400 font-semibold">Bridge Officer Tim: </span>
              {selectedAction.opening}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
              {selectedAction.venues.map((venue, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-white/5 border border-white/10 rounded-xl flex flex-col justify-between space-y-2"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-white">{venue.name}</span>
                      <span className="text-xs font-mono text-amber-400">{venue.deck}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">{venue.desc}</p>
                  </div>
                  <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-white/10">
                    Gehzeit: {venue.time}
                  </div>
                </div>
              ))}
            </div>

            <div className="text-xs text-slate-400 italic pt-2">
              💡 {selectedAction.conclusion}
            </div>
          </div>
        </div>

        {/* 3. DECISION ASSISTANT ("ICH HABE 2 STUNDEN ZEIT...") */}
        <div className="space-y-4">
          <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Entscheidungs-Assistent · »{data.freeTimeBundle.queryText}«</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.freeTimeBundle.recommendedOptions.map((opt) => (
              <div
                key={opt.optionId}
                className={`p-5 rounded-2xl flex flex-col justify-between space-y-3 transition-all ${
                  opt.isRestricted
                    ? 'bg-rose-950/20 border border-rose-900/40 text-slate-400'
                    : opt.optionId === data.freeTimeBundle.topRecommendationId
                    ? 'bg-amber-500/10 border border-amber-500/30'
                    : 'bg-white/5 border border-white/10'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-amber-400">{opt.deckLocation}</span>
                    {opt.isRestricted ? (
                      <span className="px-2 py-0.5 bg-rose-500/20 text-rose-300 text-[10px] font-mono rounded flex items-center gap-1">
                        <Lock className="w-2.5 h-2.5" /> Eingeschränkt
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 text-[10px] font-mono rounded">
                        Verfügbar
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-semibold text-white leading-snug">
                    {opt.title}
                  </h4>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    {opt.reasoning}
                  </p>
                  {opt.isRestricted && opt.restrictionNote && (
                    <p className="text-[11px] text-rose-300 mt-2 italic">
                      Hinweis: {opt.restrictionNote}
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-400 space-y-1">
                  <div>Gehdistanz: {opt.walkingEffort}</div>
                  <div>Atmosphäre: {opt.crowdLevel}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. CONCIERGE SIGNATURE SIGN-OFF */}
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 italic">
            » Certainly. I've already prepared a recommendation for exactly that situation. «
          </div>
          <div className="text-xs md:text-sm text-amber-400 font-serif font-medium tracking-wide flex items-center gap-2 shrink-0">
            <Anchor className="w-4 h-4 text-amber-400" />
            <span>Ich bleibe auf der Brücke. Melden Sie sich jederzeit.</span>
          </div>
        </div>
      </div>
    </section>
  );
};
