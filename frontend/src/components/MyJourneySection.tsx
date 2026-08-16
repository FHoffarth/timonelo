import React, { useState } from 'react';
import {
  Compass,
  Calendar,
  CheckCircle2,
  Clock,
  ShieldAlert,
  ArrowRight,
  Plane,
  Building,
  Anchor,
  Sparkles,
  Ship,
  MapPin,
} from 'lucide-react';
import { REFERENCE_JOURNEYS, type JourneyProfile, type JourneyCardData } from '../generated/journey';

interface MyJourneySectionProps {
  onSelectShip?: (slug: string) => void;
}

export const MyJourneySection: React.FC<MyJourneySectionProps> = ({ onSelectShip }) => {
  const [selectedJourneyIdx, setSelectedJourneyIdx] = useState<number>(0);
  const journey: JourneyProfile = REFERENCE_JOURNEYS[selectedJourneyIdx] || REFERENCE_JOURNEYS[0];
  const [selectedCardIdx, setSelectedCardIdx] = useState<number>(3); // Default to Terminal Arrival stage

  const card: JourneyCardData = journey.cards[selectedCardIdx] || journey.cards[0];

  return (
    <section id="my-journey" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Header & Journey Switcher */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-900 text-white rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Compass className="w-3.5 h-3.5 text-gold" />
            Personal Cruise Operating System · My Journey
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Ihre Reise als kontinuierlicher Begleiter.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Keine lose Zettelsammlung oder unübersichtliche PDFs. Timonelo führt Sie Schritt für Schritt von T-90 Tagen bis zur Heimkehr.
          </p>
        </div>

        {/* Journey Route Switcher */}
        <div className="flex flex-wrap gap-2 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          {REFERENCE_JOURNEYS.map((j, idx) => (
            <button
              key={j.id}
              onClick={() => {
                setSelectedJourneyIdx(idx);
                setSelectedCardIdx(3);
              }}
              className={`px-3.5 py-2 text-xs font-medium rounded-lg transition-all text-left ${
                selectedJourneyIdx === idx
                  ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center gap-1.5">
                <Ship className="w-3.5 h-3.5 text-slate-500" />
                <span>{j.title}</span>
              </div>
              <div className="text-[10px] text-slate-400 font-normal">{j.shipName} · Kabine {j.cabin}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Timeline Stepper */}
      <div className="mb-8 overflow-x-auto pb-3">
        <div className="flex items-center gap-2 min-w-max">
          {journey.cards.map((c, idx) => (
            <button
              key={c.cardId}
              onClick={() => setSelectedCardIdx(idx)}
              className={`px-4 py-2.5 rounded-xl text-xs font-medium transition-all flex items-center gap-2 border ${
                selectedCardIdx === idx
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${selectedCardIdx === idx ? 'bg-gold' : 'bg-slate-300'}`} />
              <span className="font-mono">{c.timeLabel}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Calm Mission Briefing Card */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden">
        {/* Mission Briefing Top Bar */}
        <div className="bg-slate-900 text-white px-6 md:px-8 py-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs text-gold uppercase tracking-wider font-mono flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Aktuelle Reisephase</span>
            </div>
            <h3 className="text-xl md:text-2xl font-serif font-normal text-white mt-1">
              {card.stageTitle}
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 bg-white/10 text-white/90 border border-white/20 rounded-full text-xs font-mono">
              Konfidenz: {card.confidenceScore}%
            </span>
            <span className="px-3 py-1 bg-gold/20 text-gold border border-gold/30 rounded-full text-xs font-semibold">
              100% Deterministisch
            </span>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 md:p-10 space-y-8">
          {/* 1. Primary Objective */}
          <div className="border-b border-slate-100 pb-6">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Aktuelles Missionsziel
            </div>
            <p className="font-serif text-2xl text-slate-900 font-normal leading-relaxed">
              {card.currentObjective}
            </p>
          </div>

          {/* 2. What to do now & What to prepare */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 border-b border-slate-100 pb-8">
            <div className="space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Was Sie JETZT tun sollten
              </div>
              <p className="text-sm text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
                {card.whatToDoNow}
              </p>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-blue-600" />
                Was Sie vorbereiten sollten
              </div>
              <p className="text-sm text-slate-800 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
                {card.whatToPrepare}
              </p>
            </div>
          </div>

          {/* 3. Negative Intelligence (The Anti-Regret Warning) */}
          <div className="p-5 bg-rose-50/90 border border-rose-200 rounded-2xl">
            <div className="text-xs font-semibold uppercase tracking-wider text-rose-900 mb-1.5 flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              Negative Intelligence · Was Sie unbedingt vermeiden sollten
            </div>
            <p className="text-sm text-rose-950 font-normal leading-relaxed">
              {card.negativeIntelligenceToAvoid}
            </p>
          </div>

          {/* 4. Upcoming Decision & Provenance Footer */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div className="p-5 bg-slate-900 text-white rounded-2xl flex flex-col justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                  Nächste anstehende Entscheidung
                </div>
                <p className="text-sm text-slate-100 font-normal">
                  {card.upcomingDecision}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 font-mono">
                Stage: {card.stage}
              </div>
            </div>

            <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                  Evidenz & Begründungsbasis
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {card.whyRecommendationExists}
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 font-mono truncate">
                Quellen: {card.evidenceSources.join(', ')}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
