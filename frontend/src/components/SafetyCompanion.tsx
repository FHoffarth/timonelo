import React, { useState } from 'react';
import {
  ShieldCheck,
  LifeBuoy,
  Footprints,
  ArrowDown,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Compass,
  MapPin,
  Clock,
  Layers,
} from 'lucide-react';
import { PRECOMPUTED_SAFETY_PLANS, type SafetyPlanData } from '../generated/safety_intelligence';

export const SafetyCompanion: React.FC = () => {
  const [selectedContext, setSelectedContext] = useState<'cabin' | 'buffet' | 'theatre'>('cabin');
  const plan: SafetyPlanData = PRECOMPUTED_SAFETY_PLANS[selectedContext] || PRECOMPUTED_SAFETY_PLANS.cabin;

  return (
    <section id="safety-intelligence" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-900 border border-emerald-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
            Safety Intelligence & Context Navigation · Chapter III
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Sicherheit & Orientierung ohne Hektik.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Wissen, wo der eigene Sammelplatz liegt, wie man im Ernstfall staufrei dorthin gelangt und welche typischen Fehler vor dem Auslaufen vermieden werden sollten.
          </p>
        </div>

        {/* Context Location Switcher */}
        <div className="flex flex-wrap gap-1.5 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          <button
            onClick={() => setSelectedContext('cabin')}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
              selectedContext === 'cabin'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Von Kabine 14122
          </button>
          <button
            onClick={() => setSelectedContext('buffet')}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
              selectedContext === 'buffet'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Vom Buffet (Deck 15)
          </button>
          <button
            onClick={() => setSelectedContext('theatre')}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
              selectedContext === 'theatre'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Vom Theater (Deck 6)
          </button>
        </div>
      </div>

      {/* Main Safety Card */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
        {/* Top Summary Banner */}
        <div className="bg-slate-900 text-white px-6 md:px-8 py-6 flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-serif text-3xl font-bold">
              {plan.assignedMusterStation.stationCode}
            </div>
            <div>
              <div className="text-xs text-emerald-400 uppercase tracking-wider font-mono">
                Zugewiesene Musterstation
              </div>
              <h3 className="text-xl md:text-2xl font-serif text-white font-normal mt-0.5">
                Musterstation {plan.assignedMusterStation.stationCode} · Deck {plan.assignedMusterStation.deck}
              </h3>
              <div className="text-xs text-slate-400">
                {plan.assignedMusterStation.venueName} ({plan.assignedMusterStation.side.split('(')[0]})
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="p-3 bg-white/5 border border-white/10 rounded-xl text-center min-w-[90px]">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Gehzeit</div>
              <div className="text-base font-semibold text-white">~{plan.estimatedWalkingTimeMin} min</div>
            </div>
            <div className="p-3 bg-white/5 border border-white/10 rounded-xl text-center min-w-[90px]">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Distanz</div>
              <div className="text-base font-semibold text-white">{plan.distanceMeters} m</div>
            </div>
            <div className="p-3 bg-white/5 border border-white/10 rounded-xl text-center min-w-[90px]">
              <div className="text-[10px] text-slate-400 uppercase font-mono">Deckwechsel</div>
              <div className="text-base font-semibold text-white">{plan.deckChanges} Decks</div>
            </div>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 md:p-10 space-y-8">
          {/* 1. Step-by-Step Deck Routing */}
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Footprints className="w-4 h-4 text-blue-600" />
                Empfohlene Route von: {plan.startLocation}
              </span>
              <span className="text-emerald-700 font-mono text-[11px] bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                ✓ {plan.safetyDrillStatus}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {plan.primaryRouteSteps.map((step) => (
                <div key={step.stepNumber} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-mono font-bold flex items-center justify-center">
                        {step.stepNumber}
                      </span>
                      <span className="text-xs font-mono text-slate-500">
                        Deck {step.deck}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-slate-900 mb-1">
                      {step.transitElement}
                    </div>
                    <p className="text-xs text-slate-700 leading-relaxed">
                      {step.instruction}
                    </p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-200/60 text-[11px] text-slate-500 italic">
                    💡 {step.orientationHint}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Negative Intelligence & Lifeboat Allocation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-slate-100 pt-6">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-rose-900 mb-3 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                Negative Intelligence (Was NICHT tun):
              </div>
              <ul className="space-y-2 text-xs text-rose-950">
                {plan.negativeIntelligenceRules.map((rule, idx) => (
                  <li key={idx} className="p-3 bg-rose-50/80 border border-rose-200 rounded-xl flex items-start gap-2 leading-relaxed">
                    <span className="font-mono font-bold text-rose-700 shrink-0">!</span>
                    <span>{rule}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-4">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
                  <LifeBuoy className="w-4 h-4 text-blue-600" />
                  Rettungsmittel & Kapazitätsbereich
                </div>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2 text-xs text-slate-700">
                  <div>
                    <span className="font-semibold text-slate-900">Zuständiger Kabinenbereich:</span> {plan.assignedMusterStation.capacityZones}
                  </div>
                  <div>
                    <span className="font-semibold text-slate-900">Zugeordnete Rettungsboote:</span> Boote #{plan.assignedMusterStation.primaryLifeboatNumbers.join(', #')}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono pt-1">
                    Evidenz: {plan.assignedMusterStation.evidenceSource}
                  </div>
                </div>
              </div>

              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <div className="text-xs text-emerald-950">
                  <span className="font-semibold">Muster Drill vor dem Auslaufen:</span> Schauen Sie das 4-minütige Sicherheitsvideo auf dem Kabinenfernseher an und lassen Sie Ihre Cruise Card einmal an Station F scannen.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
