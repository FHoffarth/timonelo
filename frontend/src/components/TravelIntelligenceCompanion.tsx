import React, { useState } from 'react';
import { Compass, Clock, AlertTriangle, CheckCircle2, ArrowRight, ShieldAlert, Sparkles, Navigation } from 'lucide-react';
import { TRAVEL_ACTIONS_REGISTRY, type TravelActionData } from '../generated/travel_actions';

const PHASES = [
  { id: 'EMBARKATION_DAY', label: 'Einschiffungstag', sub: 'Ankunft & Boarding' },
  { id: 'SEA_DAY', label: 'Seetag', sub: 'Pooldeck & Entspannung' },
  { id: 'PORT_DAY', label: 'Hafentag', sub: 'Gangway & Landgang' },
  { id: 'PRE_CRUISE', label: 'Vor der Reise', sub: 'Check-in & Vorbereitung' },
];

export const TravelIntelligenceCompanion: React.FC = () => {
  const [selectedPhase, setSelectedPhase] = useState<string>('EMBARKATION_DAY');

  const filteredActions = TRAVEL_ACTIONS_REGISTRY.filter((a) => a.phase === selectedPhase);

  return (
    <section className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-900 border border-emerald-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-emerald-700" />
            Live Travel Companion · Chapter III
          </div>
          <h2 className="font-serif text-3xl md:text-4xl text-slate-900 font-normal tracking-tight">
            Was sollte ich <span className="italic font-normal">JETZT</span> tun?
          </h2>
          <p className="text-slate-600 mt-1 max-w-2xl text-sm md:text-base">
            Preskriptive Entscheidungsintelligenz für jede Phase Ihrer Kreuzfahrt. Basierend auf Negative Intelligence: Schlangen, Lärm und Zeitfresser proaktiv vermeiden.
          </p>
        </div>

        {/* Phase Switcher Tabs */}
        <div className="flex flex-wrap gap-2 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          {PHASES.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedPhase(p.id)}
              className={`px-3.5 py-2 text-xs font-medium rounded-lg transition-all text-left ${
                selectedPhase === p.id
                  ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <div>{p.label}</div>
              <div className="text-[10px] text-slate-400 font-normal">{p.sub}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Action Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredActions.map((action) => (
          <div
            key={action.actionId}
            className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden flex flex-col justify-between"
          >
            <div>
              {/* Card Header */}
              <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between gap-4">
                <div className="flex items-center gap-2.5">
                  <Clock className="w-4 h-4 text-amber-400" />
                  <span className="font-mono text-xs text-amber-300 font-medium">{action.timeWindow}</span>
                </div>
                <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-[11px] font-semibold">
                  {action.urgency}
                </span>
              </div>

              {/* Card Content */}
              <div className="p-6 space-y-5">
                <div>
                  <h3 className="font-serif text-xl text-slate-900 font-normal tracking-tight">
                    {action.headline}
                  </h3>
                  <p className="text-slate-700 text-sm mt-2 leading-relaxed">
                    {action.whatToDoNow}
                  </p>
                </div>

                {/* Negative Intelligence Callout (The Anti-Regret Box) */}
                <div className="p-4 bg-rose-50/80 border border-rose-200 rounded-xl">
                  <div className="text-xs font-semibold uppercase tracking-wider text-rose-900 mb-1 flex items-center gap-1.5">
                    <ShieldAlert className="w-4 h-4 text-rose-600" />
                    Negative Intelligence (Zeitfresser & Fallen vermeiden)
                  </div>
                  <p className="text-xs text-rose-950 leading-relaxed">
                    {action.negativeIntelligenceToAvoid}
                  </p>
                </div>

                {/* 3 Reasons */}
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Warum diese Entscheidung?
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-600">
                    {action.reasonsTop3.map((r, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Concrete Next Steps Footer */}
            <div className="p-5 bg-slate-50 border-t border-slate-100">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2 flex items-center gap-1.5">
                <Navigation className="w-3.5 h-3.5 text-blue-600" />
                Konkrete Schritte
              </div>
              <ol className="space-y-1 text-xs text-slate-700 font-mono">
                {action.concreteSteps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-slate-400 font-semibold">{idx + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
