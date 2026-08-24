import { useState } from 'react';
import {
  MapPin,
  Compass,
  ShieldCheck,
  Plane,
  Footprints,
  ChevronRight,
  CheckCircle2,
} from 'lucide-react';
import { PORTS_REGISTRY, type CuratedPort } from '../ports';
import { useI18n } from '../i18n';

interface PortExplorerProps {
  initialPortSlug?: string;
  onSelectShip: (slug: string) => void;
}

export function PortExplorer({ initialPortSlug, onSelectShip }: PortExplorerProps) {
  const { t, isGerman } = useI18n();
  const [selectedPort, setSelectedPort] = useState<CuratedPort>(
    PORTS_REGISTRY.find((p) => p.slug === initialPortSlug) ?? PORTS_REGISTRY[0]
  );
  const headline = isGerman ? selectedPort.headlineDe : selectedPort.headlineEn;
  const story = isGerman ? selectedPort.storyDe : selectedPort.storyEn;
  const transit = isGerman ? selectedPort.transitNoteDe : selectedPort.transitNoteEn;
  const airport = isGerman ? selectedPort.airportTransitDe : selectedPort.airportTransitEn;
  const essentials = isGerman ? selectedPort.timEssentialsDe : selectedPort.timEssentialsEn;

  return (
    <div className="section-space">
      <div className="page-shell">
        {/* Header */}
        <div className="max-w-2xl mb-12">
          <p className="eyebrow text-gold">{t.ports.badge}</p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-ink font-normal mt-1 leading-tight">
            {t.ports.title}
          </h1>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-3 font-display italic">
            {t.ports.subtitle}
          </p>
        </div>

        {/* Port Selector Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-4 mb-10 border-b border-ink/8">
          {PORTS_REGISTRY.map((port) => (
            <button
              key={port.slug}
              onClick={() => setSelectedPort(port)}
              className={`px-4 py-2.5 rounded-xs text-xs font-medium transition-all cursor-pointer whitespace-nowrap flex items-center gap-2 ${
                selectedPort.slug === port.slug
                  ? 'bg-ink text-white shadow-xs'
                  : 'bg-white text-muted hover:text-ink hover:bg-paper border border-ink/6'
              }`}
            >
              <MapPin className="w-3.5 h-3.5 text-gold" />
              <span>{port.shortName}</span>
              {port.unLocode && (
                <span className="text-[10px] font-mono opacity-60">({port.unLocode})</span>
              )}
            </button>
          ))}
        </div>

        {/* PRIORITY 1: TIM'S ESSENTIALS FIRST */}
        <div className="mb-10 bg-[#0c1b2a] text-white p-6 sm:p-8 rounded-2xl shadow-md border border-amber-900/30">
          <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
            <Compass className="w-4 h-4 text-amber-400" />
            <span className="text-xs uppercase font-mono tracking-widest text-amber-300 font-semibold">
              {isGerman ? 'Heute auf der Brücke wichtig' : "Today's Bridge Essentials"}
            </span>
            <span className="text-slate-500 text-xs">·</span>
            <span className="text-xs text-slate-400 font-medium">
              {selectedPort.shortName}
              {selectedPort.unLocode ? ` (${selectedPort.unLocode})` : ''}
            </span>
          </div>

          <div className="grid sm:grid-cols-3 gap-4 text-sm font-light leading-relaxed">
            {essentials.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-white/5 rounded-xl border border-white/10">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span className="text-slate-200">{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Active Port Dossier */}
        <div className="grid lg:grid-cols-3 gap-8 items-start">
          {/* Main Port Overview */}
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-white border border-ink/8 p-8 rounded-xs shadow-xs">
              <div className="flex flex-wrap items-center justify-between gap-4 border-b border-ink/6 pb-6">
                <div>
                  <span className="text-xs font-mono uppercase tracking-widest text-gold font-medium">
                    {selectedPort.region}
                  </span>
                  <h2 className="font-display text-3xl sm:text-4xl text-ink mt-1 font-normal">
                    {selectedPort.shortName}
                  </h2>
                </div>
                <div className="text-right font-mono text-xs text-muted">
                  <span className="block font-semibold text-ink">UN/LOCODE: {selectedPort.unLocode ?? (isGerman ? 'unbekannt' : 'unknown')}</span>
                  <span>{selectedPort.country ?? (isGerman ? 'unbekannt' : 'unknown')}</span>
                </div>
              </div>

              <p className="text-ink/85 text-base sm:text-lg leading-relaxed mt-6 font-display italic">
                "{headline}"
              </p>

              <p className="text-[15px] text-slate-700 font-light leading-relaxed mt-4">
                {story}
              </p>

              {/* Verified Port Metrics Grid (Never render empty) */}
              <div className="grid sm:grid-cols-2 gap-4 mt-8">
                {selectedPort.gangwayDeck !== null && (
                  <div className="p-4 bg-paper rounded-xs border border-ink/6">
                    <div className="flex items-center gap-2 text-xs font-mono text-gold mb-1">
                      <Compass className="w-4 h-4" />
                      <span>{t.ports.gangwayAccess}</span>
                    </div>
                    <p className="text-sm font-medium text-ink">
                      {isGerman ? `Deck ${selectedPort.gangwayDeck} regulär` : `Deck ${selectedPort.gangwayDeck} (Regular)`}
                    </p>
                    {selectedPort.terminalPier && (
                      <p className="text-xs text-muted mt-1">{selectedPort.terminalPier}</p>
                    )}
                  </div>
                )}

                {selectedPort.distanceToCenterKm !== null && (
                  <div className="p-4 bg-paper rounded-xs border border-ink/6">
                    <div className="flex items-center gap-2 text-xs font-mono text-gold mb-1">
                      <Footprints className="w-4 h-4" />
                      <span>{t.ports.distanceToCity}</span>
                    </div>
                    <p className="text-sm font-medium text-ink">
                      {selectedPort.distanceToCenterKm} km
                    </p>
                    {/*
                      Three states, not two. `?? 0` previously collapsed null
                      into the same branch as 0 and answered both with
                      "Shuttle transfer or taxi recommended" -- turning "we do
                      not know how long the walk is" into operational advice.
                      An unknown walking time does not imply that walking is
                      impractical, that a shuttle exists, or that a taxi is
                      warranted.

                      0 is treated as unknown as well: it appears in the data
                      as an informal sentinel for "too far to walk", but that
                      meaning is documented nowhere and is indistinguishable
                      here from a missing value.
                    */}
                    <p className="text-xs text-muted mt-1">
                      {typeof selectedPort.walkingTimeMin === 'number' && selectedPort.walkingTimeMin > 0
                        ? (isGerman ? `ca. ${selectedPort.walkingTimeMin} Min. Gehzeit` : `approx. ${selectedPort.walkingTimeMin} min walk`)
                        : (isGerman ? 'Gehzeit unbekannt' : 'Walking time unknown')}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Strategic Advice & Logistics */}
            <div className="bg-white border border-ink/8 p-8 rounded-xs shadow-xs space-y-6">
              <h3 className="font-display text-2xl text-ink font-normal">{t.ports.localTransit}</h3>
              
              <div className="space-y-4">
                {transit && (
                  <div className="flex items-start gap-4 p-4 bg-paper rounded-xs border border-ink/6">
                    <Footprints className="w-5 h-5 text-gold shrink-0 mt-0.5" />
                    <div>
                      <span className="text-xs font-mono uppercase tracking-wider text-muted block">
                        {isGerman ? 'Öffentlicher Nahverkehr & Fußweg' : 'Local Transit & Walking Path'}
                      </span>
                      <p className="text-sm text-ink mt-0.5 font-light leading-relaxed">{transit}</p>
                    </div>
                  </div>
                )}

                {airport && (
                  <div className="flex items-start gap-4 p-4 bg-paper rounded-xs border border-ink/6">
                    <Plane className="w-5 h-5 text-gold shrink-0 mt-0.5" />
                    <div>
                      <span className="text-xs font-mono uppercase tracking-wider text-muted block">
                        {isGerman ? 'Flughafen-Transfer' : 'Airport Connection'}
                      </span>
                      <p className="text-sm text-ink mt-0.5 font-light leading-relaxed">{airport}</p>
                    </div>
                  </div>
                )}

                {/* No transit guidance without evidence. The heading promises
                    a recommendation, so say plainly that there isn't one
                    rather than leaving an empty panel that reads as a bug. */}
                {!transit && !airport && (
                  <p className="text-sm text-muted font-light leading-relaxed">
                    {isGerman
                      ? 'Keine gesicherten Transferinformationen für diesen Hafen hinterlegt.'
                      : 'No verified transit information on file for this port.'}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar: Calling Ships & Emergency */}
          <div className="space-y-6">
            <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
              <h3 className="font-display text-lg text-ink font-normal mb-4">
                {isGerman ? 'Schiffe in diesem Hafen' : 'Vessels Calling Here'}
              </h3>
              <div className="space-y-3">
                {selectedPort.callingShips.map((ship) => (
                  <button
                    key={ship.slug}
                    onClick={() => onSelectShip(ship.slug)}
                    className="w-full p-3.5 bg-paper hover:bg-gold/10 border border-ink/6 rounded-xs text-left transition-colors flex items-center justify-between group cursor-pointer"
                  >
                    <div>
                      <span className="text-xs font-medium text-ink block">{ship.name}</span>
                      <span className="text-[11px] font-mono text-muted">
                        {isGerman ? 'Aktives Referenzmodell' : 'Active reference model'}
                      </span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted group-hover:text-ink transition-transform group-hover:translate-x-0.5" />
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-[#0c1b2a] text-white p-6 rounded-xs shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-gold">
                <ShieldCheck className="w-4 h-4" />
                <span className="text-xs font-mono uppercase tracking-wider">{t.ports.emergencyNumbers}</span>
              </div>
              <p className="text-xs text-white/70 leading-relaxed font-light">
                {isGerman
                  ? 'Hinterlegte Notrufnummern der Hafenbehörden vor Ort:'
                  : 'Local port authority dispatch and emergency channels:'}
              </p>
              <div className="p-3 bg-white/10 rounded-xs border border-white/15 text-xs font-mono text-white space-y-1">
                {selectedPort.policePhone && (
                  <p>{isGerman ? 'Hafen / Polizei:' : 'Port / Police:'} {selectedPort.policePhone}</p>
                )}
                {selectedPort.emergencyPhone && (
                  <p>{isGerman ? 'Notarzt & Rettung:' : 'Medical & Emergency:'} {selectedPort.emergencyPhone}</p>
                )}
                {!selectedPort.policePhone && !selectedPort.emergencyPhone && (
                  <p className="text-white/60">
                    {isGerman
                      ? 'Keine gesicherten Notrufnummern hinterlegt.'
                      : 'No verified emergency numbers on file.'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
