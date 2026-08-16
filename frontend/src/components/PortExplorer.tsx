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
} from 'lucide-react';
import { PORTS_REGISTRY, type PortData } from '../ports';

interface PortExplorerProps {
  initialPortSlug?: string;
  onSelectShip: (slug: string) => void;
}

export function PortExplorer({ initialPortSlug, onSelectShip }: PortExplorerProps) {
  const [selectedPort, setSelectedPort] = useState<PortData>(
    PORTS_REGISTRY.find((p) => p.slug === initialPortSlug) ?? PORTS_REGISTRY[0]
  );

  return (
    <div className="section-space">
      <div className="page-shell">
        {/* Header */}
        <div className="max-w-2xl mb-12">
          <p className="eyebrow text-gold">Port Intelligence</p>
          <h1 className="font-display text-4xl sm:text-5xl md:text-6xl text-ink font-normal mt-1 leading-tight">
            Strategic Cruise Ports
          </h1>
          <p className="text-muted text-base sm:text-lg leading-relaxed mt-3 font-display italic">
            Verified terminal coordinates, step-free walking paths, gangway decks, and friction guards for major European turnarounds.
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

              {/* Fast Facts Strip */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-paper/60 p-4 rounded-xs border border-ink/6 mt-8 text-center">
                <div>
                  <span className="text-[10px] uppercase font-mono text-muted/70 block">City Distance</span>
                  <span className="font-display text-xl text-ink font-normal mt-0.5 block">
                    {selectedPort.distanceToCenterM === 0 ? '0 m (Downtown)' : `${selectedPort.distanceToCenterM} m`}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono text-muted/70 block">Walk Time</span>
                  <span className="font-display text-xl text-ink font-normal mt-0.5 block">
                    {selectedPort.walkingTimeMin} min
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono text-muted/70 block">Gangway Deck</span>
                  <span className="font-display text-xl text-ink font-normal mt-0.5 block">
                    Deck {String(selectedPort.gangwayDeckDefault).padStart(2, '0')}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono text-muted/70 block">Step-Free</span>
                  <span className="font-display text-xl text-emerald-700 font-normal mt-0.5 block">
                    {selectedPort.stepFreeAccess ? '✓ Yes' : 'No'}
                  </span>
                </div>
              </div>

              {/* Terminal Details & Transit */}
              <div className="grid sm:grid-cols-2 gap-6 mt-8">
                <div className="bg-paper/40 p-5 rounded-xs border border-ink/6">
                  <div className="flex items-center gap-2 text-xs font-mono uppercase text-ink font-semibold mb-2">
                    <Footprints className="w-4 h-4 text-gold" />
                    <span>Terminal & Walking Path</span>
                  </div>
                  <p className="text-[13px] text-muted leading-relaxed">
                    <strong>{selectedPort.terminalName}</strong>
                  </p>
                  <p className="text-[13px] text-ink/80 leading-relaxed mt-2">
                    {selectedPort.transitNote}
                  </p>
                </div>

                <div className="bg-paper/40 p-5 rounded-xs border border-ink/6">
                  <div className="flex items-center gap-2 text-xs font-mono uppercase text-ink font-semibold mb-2">
                    <Plane className="w-4 h-4 text-gold" />
                    <span>Airport Connection</span>
                  </div>
                  <p className="text-[13px] text-ink/80 leading-relaxed">
                    {selectedPort.airportTransit}
                  </p>
                </div>
              </div>
            </div>

            {/* Negative Intelligence (Decisions Avoided) */}
            <div className="bg-paper/70 border border-ink/8 p-8 rounded-xs shadow-xs">
              <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-ink font-semibold mb-4">
                <ShieldCheck className="w-4 h-4 text-emerald-700" />
                <span>Negative Intelligence · Friction Prevented in {selectedPort.name.split('(')[0].trim()}</span>
              </div>
              <div className="space-y-3">
                {selectedPort.negativeIntelligence.map((item, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 bg-white p-4 rounded-xs border border-ink/6 text-[13px] text-muted leading-relaxed">
                    <ChevronRight className="w-4 h-4 text-gold shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar: Practical Logistics & Calling Vessels */}
          <div className="space-y-6">
            {/* Practical Card */}
            <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
              <span className="text-xs font-mono uppercase tracking-widest text-muted/70 block mb-4">
                Local Essentials
              </span>
              <ul className="space-y-3 text-xs font-mono text-muted">
                <li className="flex items-center justify-between border-b border-ink/6 pb-2">
                  <span className="flex items-center gap-1.5"><CreditCard className="w-3.5 h-3.5 text-gold" /> Currency:</span>
                  <span className="text-ink font-medium">{selectedPort.currency}</span>
                </li>
                <li className="flex items-center justify-between border-b border-ink/6 pb-2">
                  <span>Card Acceptance:</span>
                  <span className="text-ink font-medium">{selectedPort.cardAcceptancePct}% Contactless</span>
                </li>
                <li className="flex items-center justify-between border-b border-ink/6 pb-2">
                  <span className="flex items-center gap-1.5"><PhoneCall className="w-3.5 h-3.5 text-emerald-600" /> Emergency:</span>
                  <span className="text-ink font-medium">{selectedPort.emergencyPhone}</span>
                </li>
              </ul>

              {/* Provenance & Authority Link */}
              <div className="mt-6 pt-4 border-t border-ink/6">
                <span className="text-[10px] font-mono uppercase tracking-wider text-muted/60 block mb-1">
                  Official Authority
                </span>
                <a
                  href={selectedPort.officialSource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-ink hover:text-gold transition-colors inline-flex items-center gap-1 font-medium"
                >
                  <span>{selectedPort.officialSource.authority}</span>
                  <ExternalLink className="w-3 h-3 text-muted" />
                </a>
                <span className="mt-1 inline-block text-[9px] font-mono px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded-xs">
                  🟢 OFFICIAL SOURCE
                </span>
              </div>
            </div>

            {/* Calling Ships */}
            <div className="bg-white border border-ink/8 p-6 rounded-xs shadow-xs">
              <span className="text-xs font-mono uppercase tracking-widest text-muted/70 block mb-4">
                Calling Fleet Twins
              </span>
              <div className="space-y-2">
                {selectedPort.callingShips.map((ship) => (
                  <button
                    key={ship.slug}
                    onClick={() => onSelectShip(ship.slug)}
                    className="w-full text-left p-3 rounded-xs border border-ink/6 hover:border-ink/20 hover:bg-paper/50 transition-all flex items-center justify-between group cursor-pointer"
                  >
                    <div>
                      <span className="font-display text-base text-ink block font-normal group-hover:text-gold transition-colors">
                        {ship.name}
                      </span>
                      <span className="text-[11px] text-muted font-mono">Explore staterooms →</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-muted group-hover:text-ink transition-transform group-hover:translate-x-1" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
