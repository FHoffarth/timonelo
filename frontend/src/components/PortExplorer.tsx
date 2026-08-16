import { useState } from 'react';
import {
  MapPin,
  Compass,
  ArrowRight,
  ShieldCheck,
  Plane,
  Footprints,
  CreditCard,
  PhoneCall,
  ExternalLink,
  ChevronRight,
  Clock,
  Navigation as NavIcon,
} from 'lucide-react';
import { PORTS_REGISTRY, type PortData } from '../ports';
import { useI18n } from '../i18n';

interface PortExplorerProps {
  initialPortSlug?: string;
  onSelectShip: (slug: string) => void;
}

export function PortExplorer({ initialPortSlug, onSelectShip }: PortExplorerProps) {
  const { t, locale } = useI18n();
  const [selectedPort, setSelectedPort] = useState<PortData>(
    PORTS_REGISTRY.find((p) => p.slug === initialPortSlug) ?? PORTS_REGISTRY[0]
  );

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
          <div className="mt-4 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xs text-xs text-slate-800 font-serif italic">
            {t.ports.officerObservation}
          </div>
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
              <span>{port.name.split('(')[0].trim()}</span>
              <span className="text-[10px] font-mono opacity-60">({port.unLocode})</span>
            </button>
          ))}
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
                    {selectedPort.name}
                  </h2>
                </div>
                <div className="text-right font-mono text-xs text-muted">
                  <span className="block font-semibold text-ink">UN/LOCODE: {selectedPort.unLocode}</span>
                  <span>{selectedPort.country}</span>
                </div>
              </div>

              <p className="text-ink/85 text-base sm:text-lg leading-relaxed mt-6 font-display italic">
                "{selectedPort.headline}"
              </p>

              {/* Verified Port Metrics Grid */}
              <div className="grid sm:grid-cols-2 gap-4 mt-8">
                <div className="p-4 bg-paper rounded-xs border border-ink/6">
                  <div className="flex items-center gap-2 text-xs font-mono text-gold mb-1">
                    <Compass className="w-4 h-4" />
                    <span>{t.ports.gangwayAccess}</span>
                  </div>
                  <p className="text-sm font-medium text-ink">Deck {selectedPort.gangwayDeck}</p>
                  <p className="text-xs text-muted mt-1">{selectedPort.terminalPier}</p>
                </div>

                <div className="p-4 bg-paper rounded-xs border border-ink/6">
                  <div className="flex items-center gap-2 text-xs font-mono text-gold mb-1">
                    <Footprints className="w-4 h-4" />
                    <span>{t.ports.distanceToCity}</span>
                  </div>
                  <p className="text-sm font-medium text-ink">{selectedPort.distanceToCenterKm} km</p>
                  <p className="text-xs text-muted mt-1">{selectedPort.walkingTimeMin} min walking time</p>
                </div>
              </div>
            </div>

            {/* Strategic Advice & Logistics */}
            <div className="bg-white border border-ink/8 p-8 rounded-xs shadow-xs space-y-6">
              <h3 className="font-display text-2xl text-ink font-normal">{t.ports.localTransit}</h3>
              
              <div className="space-y-4">
                <div className="flex items-start gap-4 p-4 bg-paper rounded-xs border border-ink/6">
                  <Plane className="w-5 h-5 text-gold shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-mono uppercase tracking-wider text-muted block">Airport Transfer</span>
                    <p className="text-sm text-ink mt-0.5">{selectedPort.airportTransfer}</p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 bg-paper rounded-xs border border-ink/6">
                  <CreditCard className="w-5 h-5 text-gold shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-mono uppercase tracking-wider text-muted block">Taxi & Payment</span>
                    <p className="text-sm text-ink mt-0.5">{selectedPort.taxiPricingAdvice}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar: Calling Ships & Emergency */}
          <div className="space-y-6">
            <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
              <h3 className="font-display text-lg text-ink font-normal mb-4">{t.ports.callingFleet}</h3>
              <div className="space-y-3">
                {selectedPort.callingShips.map((ship) => (
                  <button
                    key={ship.slug}
                    onClick={() => onSelectShip(ship.slug)}
                    className="w-full p-3 bg-paper hover:bg-gold/10 border border-ink/6 rounded-xs text-left transition-colors flex items-center justify-between group cursor-pointer"
                  >
                    <div>
                      <span className="text-xs font-medium text-ink block">{ship.name}</span>
                      <span className="text-[11px] font-mono text-muted">{ship.role}</span>
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
              <p className="text-xs text-white/70 leading-relaxed">
                Direct emergency port authority dispatch and medical coordination:
              </p>
              <div className="p-3 bg-white/10 rounded-xs border border-white/15 text-xs font-mono text-white">
                <p>Port Police: {selectedPort.emergencyPolice}</p>
                <p className="mt-1">Medical Duty: {selectedPort.emergencyMedical}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
