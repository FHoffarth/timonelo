import React, { useState } from 'react';
import {
  Plane,
  Building,
  Anchor,
  ShieldAlert,
  Clock,
  Compass,
  CreditCard,
  PhoneCall,
  Zap,
  MapPin,
  CheckCircle2,
} from 'lucide-react';
import { DESTINATIONS_REGISTRY, type DestinationData } from '../generated/destinations';

export const DestinationIntelligenceSection: React.FC = () => {
  const [selectedSlug, setSelectedSlug] = useState<string>('genoa');
  const dest: DestinationData =
    DESTINATIONS_REGISTRY.find((d) => d.portSlug === selectedSlug) || DESTINATIONS_REGISTRY[0];

  return (
    <section id="destination-intelligence" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-900 border border-blue-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <MapPin className="w-3.5 h-3.5 text-blue-700" />
            Destination Intelligence · Chapter III
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Logistik im Starthafen vor dem Boarding.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            Eine Kreuzfahrt beginnt am Flughafen der Zielstadt. Timonelo liefert einsatzbereite Fakten zu Terminals, Transfers, Hotelzonen und lokalen Kostenfallen.
          </p>
        </div>

        {/* City Switcher */}
        <div className="flex flex-wrap gap-2 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          {DESTINATIONS_REGISTRY.map((d) => (
            <button
              key={d.portSlug}
              onClick={() => setSelectedSlug(d.portSlug)}
              className={`px-3.5 py-2 text-xs font-medium rounded-lg transition-all text-left ${
                selectedSlug === d.portSlug
                  ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <div>{d.cityName}</div>
              <div className="text-[10px] text-slate-400 font-normal">{d.country}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Destination Overview Box */}
      <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden mb-8">
        {/* Destination Top Bar */}
        <div className="bg-slate-900 text-white px-6 md:px-8 py-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs text-blue-400 uppercase tracking-wider font-mono">
              Hafenstadt & Kreuzfahrt-Hub
            </div>
            <h3 className="text-2xl md:text-3xl font-serif font-normal text-white mt-0.5">
              {dest.cityName}, {dest.country}
            </h3>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 bg-white/10 text-white text-xs font-mono rounded-lg border border-white/10">
              {dest.timezone}
            </span>
            <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 text-xs font-mono rounded-lg border border-emerald-500/30">
              {dest.currency.split('·')[0]}
            </span>
          </div>
        </div>

        {/* Essential Logistics Grid */}
        <div className="p-6 md:p-8 grid grid-cols-2 md:grid-cols-4 gap-4 border-b border-slate-100 bg-slate-50/50">
          <div className="p-3.5 bg-white rounded-xl border border-slate-200/80">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              Strom & Stecker
            </div>
            <div className="text-xs text-slate-800 font-mono font-medium">{dest.powerPlugs}</div>
          </div>

          <div className="p-3.5 bg-white rounded-xl border border-slate-200/80">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
              <CreditCard className="w-3.5 h-3.5 text-blue-500" />
              ÖPNV-Ticket
            </div>
            <div className="text-xs text-slate-800 font-medium">{dest.localTransportCard}</div>
          </div>

          <div className="p-3.5 bg-white rounded-xl border border-slate-200/80">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
              <PhoneCall className="w-3.5 h-3.5 text-rose-500" />
              Notruf (Polizei / Notarzt)
            </div>
            <div className="text-xs text-slate-800 font-mono font-medium">
              Polizei: {dest.emergencyPhonePolice} · Notarzt: {dest.emergencyPhoneMedical}
            </div>
          </div>

          <div className="p-3.5 bg-white rounded-xl border border-slate-200/80">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-emerald-500" />
              eSIM / Mobilfunk
            </div>
            <div className="text-xs text-slate-800 leading-snug">{dest.simEsimRecommendation}</div>
          </div>
        </div>

        {/* Main Content: Airports & Cruise Terminal */}
        <div className="p-6 md:p-8 space-y-8">
          {/* 1. Airport Connections */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-4 flex items-center gap-2">
              <Plane className="w-4 h-4 text-blue-600" />
              Flughafen-Anbindung & Transfer zum Kreuzfahrtterminal
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {dest.airports.map((a) => (
                <div key={a.iataCode} className="p-5 bg-white border border-slate-200 rounded-2xl space-y-3">
                  <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
                    <div>
                      <span className="font-mono text-xs px-2 py-0.5 bg-slate-900 text-white rounded font-semibold mr-2">
                        {a.iataCode}
                      </span>
                      <span className="text-sm font-semibold text-slate-900">{a.airportName}</span>
                    </div>
                    <span className="text-xs font-mono text-slate-500">{a.distanceToTerminalKm} km Distanz</span>
                  </div>
                  <div className="text-xs text-slate-700 leading-relaxed">
                    <span className="font-semibold text-slate-900">Bester Transfer:</span> {a.bestTransitMode}
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-500 font-mono pt-1">
                    <span>Fahrzeit: ~{a.typicalDurationMin} min</span>
                    <span>Kosten: {a.estimatedCostRange}</span>
                  </div>
                  <div className="p-3 bg-amber-50/80 border border-amber-200 rounded-xl text-xs text-amber-950">
                    <span className="font-semibold">Vorsicht:</span> {a.negativeIntelligence}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Official Cruise Terminal Layout */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-4 flex items-center gap-2">
              <Anchor className="w-4 h-4 text-emerald-600" />
              Offizielles Kreuzfahrtterminal & Liegeplätze
            </h4>
            {dest.terminals.map((t, idx) => (
              <div key={idx} className="p-6 bg-slate-50 border border-slate-200 rounded-2xl space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="text-base font-semibold text-slate-900">{t.terminalName}</div>
                  <div className="text-xs text-slate-500 font-mono">
                    {t.distanceToCityCenterKm} km zum Stadtzentrum · {t.nearestMetroOrTrain}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-700">
                  <div className="p-3.5 bg-white rounded-xl border border-slate-200">
                    <div className="font-semibold text-slate-900 mb-1">Gepäckannahme (Porter Dropoff):</div>
                    {t.porterDropoffLocation}
                  </div>
                  <div className="p-3.5 bg-white rounded-xl border border-slate-200">
                    <div className="font-semibold text-slate-900 mb-1">Sicherheitskontrolle & Besonderheiten:</div>
                    {t.securityLaneNotes}
                  </div>
                </div>

                <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-950">
                  <span className="font-semibold">Negative Intelligence:</span> {t.negativeIntelligence}
                </div>
              </div>
            ))}
          </div>

          {/* 3. Hotel Zones & City Negative Intelligence */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
                <Building className="w-4 h-4 text-slate-700" />
                Empfohlene Hotelzonen (Vorabend)
              </h4>
              <ul className="space-y-2 text-xs text-slate-700">
                {dest.recommendedHotelZones.map((z, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-3 bg-white border border-slate-200 rounded-xl">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{z}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wider text-rose-900 mb-3 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                Top 3 Lokale Touristenfallen & Risiken
              </h4>
              <ul className="space-y-2 text-xs text-rose-950">
                {dest.negativeIntelligenceTop3.map((n, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-3 bg-rose-50/80 border border-rose-200 rounded-xl leading-relaxed">
                    <span className="font-mono font-bold text-rose-700 shrink-0">{idx + 1}.</span>
                    <span>{n}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
