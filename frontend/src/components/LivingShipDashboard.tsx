import React, { useState } from 'react';
import {
  Anchor,
  Compass,
  Ship,
  Wind,
  Waves,
  Sun,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Radio,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  MapPin,
  Footprints,
} from 'lucide-react';
import {
  LIVE_VOYAGE_STATES,
  type LiveVoyageStateData,
  type OperationalImpactData,
} from '../generated/living_ship';

export const LivingShipDashboard: React.FC = () => {
  const [selectedShipName, setSelectedShipName] = useState<string>('MSC Bellissima');
  const liveState: LiveVoyageStateData =
    LIVE_VOYAGE_STATES.find((s) => s.shipName === selectedShipName) || LIVE_VOYAGE_STATES[0];

  return (
    <section id="living-ship" className="py-16 px-4 max-w-6xl mx-auto border-t border-slate-200">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-900 border border-emerald-200 rounded-full text-xs font-semibold uppercase tracking-wider mb-3">
            <Radio className="w-3.5 h-3.5 text-emerald-700 animate-pulse" />
            Living Ship · Digital Twin of the Voyage (Chapter V Final)
          </div>
          <h2 className="font-serif text-3xl md:text-5xl text-slate-900 font-normal tracking-tight">
            Das lebendige Schiff. Echtzeit-Verständnis der Brücke.
          </h2>
          <p className="text-slate-600 mt-2 max-w-2xl text-sm md:text-base">
            AIS zeigt nur, wo ein Schiff ist. Bridge Officer Tim erklärt, was das für Sie bedeutet: Gangway-Freigabe, Windverhältnisse und staufreie Wege.
          </p>
        </div>

        {/* Ship Switcher */}
        <div className="flex flex-wrap gap-1.5 p-1.5 bg-slate-100 rounded-xl border border-slate-200 self-start">
          <button
            onClick={() => setSelectedShipName('MSC Bellissima')}
            className={`px-3 py-1.5 text-xs rounded-lg transition-all font-medium ${
              selectedShipName === 'MSC Bellissima'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            MSC Bellissima (Yokohama)
          </button>
          <button
            onClick={() => setSelectedShipName('MS Andorinha')}
            className={`px-3 py-1.5 text-xs rounded-lg transition-all font-medium ${
              selectedShipName === 'MS Andorinha'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200 font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            MS Andorinha (Douro)
          </button>
        </div>
      </div>

      {/* Main Luxury Living Digital Twin Container */}
      <div className="bg-slate-950 text-white border border-slate-800 rounded-3xl p-6 md:p-10 shadow-2xl space-y-10 relative overflow-hidden">
        {/* Subtle Ambient Lights */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-600/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-600/5 rounded-full blur-3xl pointer-events-none" />

        {/* 1. VESSEL & TELEMETRY LIVE STRIP */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-6 bg-slate-900/90 border border-slate-800 rounded-2xl">
          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Schiff & Status</span>
            <div className="text-sm font-semibold text-white flex items-center gap-1.5">
              <Ship className="w-4 h-4 text-amber-400" />
              <span>{liveState.shipName}</span>
            </div>
            <span className="text-xs text-emerald-400 font-mono">
              {liveState.currentStatus.split('(')[0].trim()}
            </span>
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Position & Anleger</span>
            <div className="text-xs text-slate-200 font-mono leading-tight flex items-start gap-1">
              <MapPin className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
              <span>{liveState.currentLocation}</span>
            </div>
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Wetter & Seegang</span>
            <div className="text-xs text-slate-200 leading-tight">
              {liveState.weatherSummary}
            </div>
            <span className="text-[11px] text-slate-400 font-mono block">
              {liveState.seaStateDescription} · {liveState.windForceBeaufort} Bft
            </span>
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Gangway & All Aboard</span>
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 text-[11px] font-mono rounded ${
                liveState.gangwayOpen ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
              }`}>
                {liveState.gangwayOpen ? 'Gangway Geöffnet' : 'Auf See / Geschlossen'}
              </span>
            </div>
            {liveState.allAboardTime && (
              <span className="text-xs text-amber-400 font-mono font-semibold block">
                All Aboard: {liveState.allAboardTime}
              </span>
            )}
          </div>
        </div>

        {/* 2. PASSENGER TRANSLATION LAYER (WHAT DOES THIS MEAN FOR ME?) */}
        <div className="space-y-4">
          <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Passenger Translation Layer · Maritime Fakten in praktisches Verständnis
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {liveState.operationalChanges.map((imp) => (
              <div
                key={imp.impactId}
                className="p-5 bg-white/5 border border-white/10 rounded-2xl flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-mono mb-2">
                    <span className="text-amber-400 font-semibold">{imp.changeTitle}</span>
                    <span className="text-[10px] text-slate-400">Verifiziert</span>
                  </div>
                  <p className="text-xs text-slate-400 italic mb-2">
                    Maritimer Fakt: „{imp.rawMaritimeFact}“
                  </p>
                  <p className="text-xs text-slate-200 leading-relaxed font-medium">
                    Bedeutung für Sie: {imp.passengerTranslation}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-1 text-xs">
                  <div className="text-emerald-300 font-mono flex items-start gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                    <span>Empfehlung: {imp.recommendedAction}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. BRIDGE OBSERVATIONS & RECOMMENDED ACTIONS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Bridge Observations */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="text-xs font-mono uppercase text-blue-400 font-semibold flex items-center gap-2">
              <Radio className="w-3.5 h-3.5" />
              <span>Bridge Officer Tim Live-Beobachtungen</span>
            </div>
            <div className="space-y-2.5">
              {liveState.botObservations.map((obs, i) => (
                <div key={i} className="p-3 bg-white/5 rounded-xl text-xs text-slate-200 leading-relaxed">
                  {obs}
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Passenger Actions */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="text-xs font-mono uppercase text-emerald-400 font-semibold flex items-center gap-2">
              <Footprints className="w-3.5 h-3.5" />
              <span>Empfohlene Tages-Schritte</span>
            </div>
            <div className="space-y-2.5">
              {liveState.recommendedPassengerActions.map((act, i) => (
                <div key={i} className="p-3 bg-white/5 rounded-xl text-xs text-slate-200 leading-relaxed flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{act}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 4. FOUNDATION COMPLETE & BRIDGE SIGN-OFF */}
        <div className="pt-6 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 italic max-w-2xl">
            » {liveState.bridgeSignOff} «
          </div>
          <div className="text-xs md:text-sm text-emerald-400 font-serif font-medium tracking-wide flex items-center gap-2 shrink-0">
            <Anchor className="w-4 h-4 text-emerald-400" />
            <span>Digital Twin aktiv · Ich bleibe auf der Brücke.</span>
          </div>
        </div>
      </div>
    </section>
  );
};
