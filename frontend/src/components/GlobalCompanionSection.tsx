import React, { useState } from 'react';
import {
  HeartHandshake,
  ShieldAlert,
  ShieldCheck,
  Compass,
  Sparkles,
  Plane,
  Building,
  Anchor,
  Ship,
  MapPin,
  Home,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  User,
  Clock,
} from 'lucide-react';
import {
  TRAVEL_MEMORY_FLO,
  COMPANION_8_PHASES,
  REGRET_SCENARIOS,
  type CompanionPhaseData,
} from '../generated/global_companion';

export const GlobalCompanionSection: React.FC = () => {
  const [activePhaseIdx, setActivePhaseIdx] = useState<number>(0);
  const [activeRegretScenario, setActiveRegretScenario] = useState<number>(0);

  const phase: CompanionPhaseData = COMPANION_8_PHASES[activePhaseIdx] || COMPANION_8_PHASES[0];
  const regretScenario = REGRET_SCENARIOS[activeRegretScenario] || REGRET_SCENARIOS[0];

  const phaseIcons = [
    <Home className="w-3.5 h-3.5" />,
    <Plane className="w-3.5 h-3.5" />,
    <Building className="w-3.5 h-3.5" />,
    <Compass className="w-3.5 h-3.5" />,
    <Anchor className="w-3.5 h-3.5" />,
    <Ship className="w-3.5 h-3.5" />,
    <MapPin className="w-3.5 h-3.5" />,
    <RotateCcw className="w-3.5 h-3.5" />,
  ];

  return (
    <section id="global-companion" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Brand Vision Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-50 text-amber-900 border border-amber-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-4">
          <HeartHandshake className="w-3.5 h-3.5 text-amber-700" />
          Global Companion & Regret Engine · Chapter III
        </div>
        <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight leading-tight">
          „Timonelo doesn't help you travel more. It helps you regret less.“
        </h2>
        <p className="text-slate-600 mt-3 text-sm md:text-base leading-relaxed">
          Vom Verlassen der Haustür bis zur Rückkehr nach Hause: Ein deterministischer Begleiter mit persönlicher Reise-Erfahrung (Travel Memory) und aktiver Reue-Risiko-Bewertung (Regret Score).
        </p>
      </div>

      {/* Top Grid: Travel Memory Card & Regret Score Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-12">
        {/* 1. Travel Memory Card (Flo) */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-3xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-serif text-sm">
                  {TRAVEL_MEMORY_FLO.preferredName[0]}
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">
                    Travel Memory · {TRAVEL_MEMORY_FLO.preferredName}
                  </h3>
                  <div className="text-[11px] text-slate-400 font-mono">
                    {TRAVEL_MEMORY_FLO.travelStyle}
                  </div>
                </div>
              </div>
              <span className="px-2.5 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-full text-xs font-semibold">
                MSC {TRAVEL_MEMORY_FLO.mscLoyaltyTier}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block mb-1">
                  Erfahrungs-Vorlieben:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {TRAVEL_MEMORY_FLO.likes.slice(0, 4).map((l, i) => (
                    <span key={i} className="px-2 py-1 bg-slate-50 border border-slate-200 rounded-lg text-slate-700">
                      ✓ {l}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px] block mb-1">
                  Abneigungen (Vermieden):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {TRAVEL_MEMORY_FLO.dislikes.slice(0, 3).map((d, i) => (
                    <span key={i} className="px-2 py-1 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
                      ✕ {d}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>Hotel: {TRAVEL_MEMORY_FLO.hotelPreference}</span>
            <span>Flug: {TRAVEL_MEMORY_FLO.airlineTier}</span>
          </div>
        </div>

        {/* 2. Regret Score Simulator */}
        <div className="lg:col-span-7 bg-slate-900 text-white rounded-3xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-mono uppercase tracking-wider text-amber-400 font-semibold">
                  Timonelo Regret Score Engine
                </span>
              </div>

              {/* Scenario Toggle */}
              <div className="flex gap-1.5 bg-white/10 p-1 rounded-xl">
                {REGRET_SCENARIOS.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveRegretScenario(idx)}
                    className={`px-2.5 py-1 text-xs rounded-lg transition-all ${
                      activeRegretScenario === idx
                        ? 'bg-white text-slate-900 font-semibold shadow-xs'
                        : 'text-slate-300 hover:text-white'
                    }`}
                  >
                    Szenario {idx === 0 ? 'A (Flug am selben Tag)' : 'B (Vortag + Hotel)'}
                  </button>
                ))}
              </div>
            </div>

            <div className="p-4 bg-white/5 border border-white/10 rounded-2xl mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-300 font-medium">{regretScenario.scenarioTitle}</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold ${
                    regretScenario.regretScorePct > 50
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}
                >
                  Regret Risk: {regretScenario.regretScorePct}%
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-300">
                {regretScenario.whyYouWillRegretThis.slice(0, 3).map((w, i) => (
                  <div key={i} className="flex items-start gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{w}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="text-xs text-emerald-300 bg-emerald-950/40 border border-emerald-500/20 p-3 rounded-xl">
            <span className="font-semibold text-white">Empfohlene Entscheidung:</span> {regretScenario.howToAvoidRegret}
          </div>
        </div>
      </div>

      {/* 8-Phase Itinerary Companion Stepper */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 md:p-8 shadow-sm">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-6 flex items-center gap-2">
          <Compass className="w-4 h-4 text-blue-600" />
          Die 8 chronologischen Phasen der Gesamtreise
        </div>

        {/* Stepper Navigation */}
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2 mb-8">
          {COMPANION_8_PHASES.map((p, idx) => (
            <button
              key={idx}
              onClick={() => setActivePhaseIdx(idx)}
              className={`p-3 rounded-2xl text-left border transition-all flex flex-col justify-between ${
                activePhaseIdx === idx
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono opacity-60">P{p.phaseNumber}</span>
                {phaseIcons[idx]}
              </div>
              <div className="text-xs font-semibold line-clamp-1">
                {p.phase.split('.')[1]?.trim() || p.phase}
              </div>
            </button>
          ))}
        </div>

        {/* Selected Phase Detail Card */}
        <div className="border border-slate-200 rounded-2xl p-6 md:p-8 bg-slate-50/50 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-200 pb-4">
            <div>
              <div className="text-xs font-mono text-blue-600 font-semibold uppercase tracking-wider">
                {phase.phase}
              </div>
              <h4 className="text-2xl font-serif text-slate-900 font-normal mt-0.5">
                {phase.headline}
              </h4>
            </div>
            <span className="text-xs font-mono px-3 py-1 bg-white border border-slate-200 rounded-full text-slate-600">
              Missionsziel: {phase.objectiveNow}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Practical Steps */}
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                Was jetzt zu tun ist:
              </div>
              <ul className="space-y-2 text-xs text-slate-700">
                {phase.whatToDoNow.map((step, idx) => (
                  <li key={idx} className="p-3 bg-white border border-slate-200 rounded-xl flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Negative Intelligence & Memory Adaptation */}
            <div className="space-y-4">
              <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-950">
                <div className="font-semibold text-rose-900 mb-1 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-rose-600" />
                  Negative Intelligence (Unbedingt vermeiden):
                </div>
                {phase.negativeIntelligenceToAvoid}
              </div>

              <div className="p-4 bg-purple-50 border border-purple-200 rounded-2xl text-xs text-purple-950">
                <div className="font-semibold text-purple-900 mb-1 flex items-center gap-1.5">
                  <User className="w-4 h-4 text-purple-600" />
                  Travel Memory Anpassung (Flo):
                </div>
                {phase.travelMemoryAdaptations[0]}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
