import React, { useState } from 'react';
import {
  UserCheck,
  ShieldCheck,
  Award,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  Zap,
  Globe,
  Plane,
  Building,
  Ship,
} from 'lucide-react';
import { PRECOMPUTED_BRIEFINGS, type PersonalBriefingData } from '../generated/personal_intelligence';

export const PersonalTravelBriefing: React.FC = () => {
  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const briefing: PersonalBriefingData = PRECOMPUTED_BRIEFINGS[selectedIdx] || PRECOMPUTED_BRIEFINGS[0];

  return (
    <section id="personal-intelligence" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 text-purple-900 border border-purple-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <UserCheck className="w-3.5 h-3.5 text-purple-700" />
            Personal Travel Intelligence · Chapter III
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Persönliches Reise-Briefing.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Nicht nur das Schiff verstehen, sondern <span className="italic font-normal">Ihre</span> individuelle Situation: Staatsbürgerschaft, Vielflieger- und Clubstatus, Visaregeln und maßgeschneiderte Prioritäten.
          </p>
        </div>

        {/* Persona Profile Switcher */}
        <div className="flex flex-wrap gap-2 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          {PRECOMPUTED_BRIEFINGS.map((b, idx) => (
            <button
              key={b.briefingId}
              onClick={() => setSelectedIdx(idx)}
              className={`px-3.5 py-2 text-xs font-medium rounded-lg transition-all text-left ${
                selectedIdx === idx
                  ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <div>{b.travellerName} ({b.nationality})</div>
              <div className="text-[10px] text-slate-400 font-normal">
                {b.loyaltyPrograms[0]?.programName.replace('Voyagers Club', '')} {b.loyaltyPrograms[0]?.currentTier}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Briefing Card */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
        {/* Briefing Top Bar */}
        <div className="bg-slate-900 text-white px-6 md:px-8 py-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs text-purple-400 uppercase tracking-wider font-mono flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
              <span>Persönliche Entscheidungsgrundlage</span>
            </div>
            <h3 className="text-xl md:text-2xl font-serif font-normal text-white mt-1">
              {briefing.travellerName} · {briefing.cruiseShip} ({briefing.cruiseRoute})
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-mono">
              Konfidenz: {briefing.confidenceOverall}
            </span>
            <span className="px-3 py-1 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full text-xs font-semibold">
              100% Deterministisch
            </span>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 md:p-10 space-y-8">
          {/* 1. Documents & Visa Requirements */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-blue-600" />
              1. Dokumente, Passgültigkeit & Visaregeln
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {briefing.visaAndDocumentsStatus.map((v) => (
                <div key={v.destinationCountry} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900 text-sm">{v.destinationCountry}</span>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[11px] font-semibold rounded">
                      {v.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed">{v.details}</p>
                  <div className="text-[11px] text-slate-400 font-mono pt-1">
                    Passrestgültigkeit: mind. {v.passportValidityRequiredMonths} Monate gefordert
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Loyalty Status & Unlocked Benefits */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Award className="w-4 h-4 text-amber-500" />
              2. Aktivierte Statusvorteile & Meilenprogramme
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {briefing.loyaltyPrograms.map((l, idx) => (
                <div key={idx} className="p-4 bg-white border border-slate-200 rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="text-xs font-mono text-slate-400 uppercase">{l.programName}</div>
                    <div className="text-sm font-semibold text-slate-900 mt-0.5">{l.currentTier}</div>
                    <ul className="mt-3 space-y-1.5 text-xs text-slate-700">
                      {l.unlockedBenefitsOnTrip.map((b, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          <span>{b}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="mt-3 pt-2.5 border-t border-slate-100 text-[10px] text-slate-500 font-mono leading-relaxed">
                    {l.potentialTierProgress}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. Important Actions & Personalized Risks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-slate-100 pt-6">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                3. Wichtigste persönliche Handlungsschritte
              </h4>
              <ul className="space-y-2 text-xs text-slate-800">
                {briefing.importantActions.map((a, idx) => (
                  <li key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2">
                    <span className="font-mono text-slate-400 font-semibold">{idx + 1}.</span>
                    <span>{a}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-900 mb-3 flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                4. Persönliche Risiken (Negative Intelligence)
              </h4>
              <ul className="space-y-2 text-xs text-rose-950">
                {briefing.potentialRisks.map((r, idx) => (
                  <li key={idx} className="p-3 bg-rose-50/80 border border-rose-200 rounded-xl leading-relaxed flex items-start gap-2">
                    <span className="font-mono font-bold text-rose-700 shrink-0">!</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* 5. Status Opportunities Footer */}
          <div className="p-4 bg-purple-50/80 border border-purple-200 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-purple-900 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-purple-700" />
                Status-Chancen & Meilenfortschritt
              </div>
              <ul className="mt-1 space-y-1 text-xs text-purple-950">
                {briefing.statusOpportunities.map((o, idx) => (
                  <li key={idx}>+ {o}</li>
                ))}
              </ul>
            </div>
            <div className="text-[11px] text-purple-700 font-mono shrink-0">
              Briefing-ID: {briefing.briefingId}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
