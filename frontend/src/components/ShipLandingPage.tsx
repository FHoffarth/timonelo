import { ArrowRight, ShieldCheck, MapPin, ArrowLeft } from 'lucide-react';
import type { FleetVessel } from '../fleet';
import { FLEET_REGISTRY } from '../fleet';
import { PORTS_REGISTRY } from '../ports';
import { useI18n } from '../i18n';

interface ShipLandingPageProps {
  vessel: FleetVessel;
  onExploreCabins: (cabinNum?: string) => void;
  onSelectShip: (slug: string) => void;
  onBackToFleet: () => void;
}

export function ShipLandingPage({
  vessel,
  onExploreCabins,
  onSelectShip,
  onBackToFleet,
}: ShipLandingPageProps) {
  const { t, locale } = useI18n();
  const relatedShips = FLEET_REGISTRY.filter((v) => v.slug !== vessel.slug);
  const callingPorts = PORTS_REGISTRY.filter((p) =>
    p.callingShips.some((cs) => cs.slug === vessel.slug)
  );

  return (
    <div className="min-h-screen bg-paper">
      {/* Hero Section */}
      <header className="relative ground-navy text-white overflow-hidden">
        <img
          src={vessel.heroImageUrl}
          alt={vessel.name}
          className="absolute inset-0 h-full w-full object-cover opacity-35"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0c1b2a] via-[#0c1b2a]/60 to-transparent" />

        <div className="relative page-shell pt-10 pb-16">
          {/* Breadcrumb */}
          <div className="mb-6">
            <button
              onClick={onBackToFleet}
              className="inline-flex items-center gap-1.5 text-xs text-white/65 hover:text-white transition font-mono uppercase tracking-wider cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>{t.navigation.ships}</span>
              <span className="text-white/30">/</span>
              <span className="text-gold font-medium">{vessel.name}</span>
            </button>
          </div>

          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
            <div className="max-w-3xl">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-mono bg-white/10 px-2.5 py-0.5 rounded-xs text-gold uppercase tracking-wider">
                  {vessel.roleTitle}
                </span>
                <span className="text-white/30">·</span>
                <span className="text-xs font-mono text-white/70">{vessel.shipClass}</span>
                <span className="text-white/30">·</span>
                <span className="text-xs font-mono text-white/70">{vessel.imo}</span>
              </div>

              <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-normal text-white leading-tight">
                {vessel.name}
              </h1>

              <p className="text-white/85 text-lg sm:text-xl mt-4 font-display italic max-w-2xl leading-relaxed">
                "{vessel.tagline}"
              </p>

              <div className="mt-5 p-3.5 bg-white/10 border border-white/15 rounded-xs text-xs text-amber-200 font-serif italic max-w-xl">
                {locale === 'de'
                  ? `Bridge Officer Tim: "Die Deckgeometrie für ${vessel.name} basiert auf Werftplänen. Für nicht einzeln kartierte Kabinen greift das bewährte Klassen-Referenzmodell."`
                  : `Bridge Officer Tim: "Deck geometry for ${vessel.name} is anchored in shipyard general arrangements. Staterooms without individual scans inherit proven class reference geometry."`}
              </div>
            </div>

            {/* Direct Cabin CTA */}
            <div className="bg-white/10 backdrop-blur-md p-6 rounded-xs border border-white/15 max-w-sm">
              <span className="text-xs font-mono uppercase text-gold block mb-1">
                {locale === 'de' ? 'Kabinen-Intelligenz' : 'Stateroom Intelligence'}
              </span>
              <p className="text-xs text-white/80 leading-relaxed mb-4">
                {locale === 'de'
                  ? 'Erkunden Sie berechnete Gehdistanzen, vertikale Lärmquellen und Sichtachsen.'
                  : 'Inspect estimated walking distances, vertical noise surroundings, and sightlines.'}
              </p>
              <button
                onClick={() => onExploreCabins(vessel.defaultCabin)}
                className="w-full px-5 py-3 bg-white text-ink hover:bg-gold transition-colors font-medium text-xs rounded-xs flex items-center justify-center gap-2 cursor-pointer shadow-md"
              >
                <span>{locale === 'de' ? `Kabinen-Explorer öffnen (${vessel.defaultCabin})` : `Enter Cabin Explorer (e.g. ${vessel.defaultCabin})`}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Stats Strip */}
          <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-px bg-white/15 border border-white/15 rounded-xs overflow-hidden">
            <div className="bg-[#0c1b2a]/80 p-4 text-center">
              <span className="text-[10px] uppercase font-mono text-white/50 block">{locale === 'de' ? 'Decks' : 'Decks'}</span>
              <span className="font-display text-2xl text-white mt-1 block">{vessel.totalDecks}</span>
            </div>
            <div className="bg-[#0c1b2a]/80 p-4 text-center">
              <span className="text-[10px] uppercase font-mono text-white/50 block">{locale === 'de' ? 'Kabinen' : 'Staterooms'}</span>
              <span className="font-display text-2xl text-white mt-1 block">{vessel.cabinCount}</span>
            </div>
            <div className="bg-[#0c1b2a]/80 p-4 text-center">
              <span className="text-[10px] uppercase font-mono text-white/50 block">{locale === 'de' ? 'Länge · Breite' : 'Length · Beam'}</span>
              <span className="font-display text-2xl text-white mt-1 block">{vessel.lengthM}m · {vessel.beamM}m</span>
            </div>
            <div className="bg-[#0c1b2a]/80 p-4 text-center">
              <span className="text-[10px] uppercase font-mono text-white/50 block">{locale === 'de' ? 'Max. Passagiere' : 'Max Guests'}</span>
              <span className="font-display text-2xl text-white mt-1 block">{vessel.passengerCapacity}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="page-shell py-16 space-y-16">
        {/* Architectural Story */}
        <section className="bg-white border border-ink/8 p-8 sm:p-10 rounded-xs shadow-xs">
          <p className="eyebrow text-gold">{locale === 'de' ? 'Schiffsarchitektur & Profil' : 'Naval Architecture & Profile'}</p>
          <h2 className="font-display text-3xl text-ink font-normal mt-1 mb-4">
            {locale === 'de' ? 'Schiffscharakter & Bereiche' : 'Vessel Character & Spaces'}
          </h2>
          <p className="text-[15px] text-ink/85 leading-relaxed max-w-3xl">
            {vessel.description} {locale === 'de' ? `Ausgeliefert ${vessel.buildYear} von` : 'Delivered in ' + vessel.buildYear + ' by'} <strong>{vessel.builder}</strong>, {locale === 'de' ? 'im Einsatz in' : 'operating in'} {vessel.region}.
          </p>

          {/* Signature Spaces */}
          <div className="mt-8">
            <span className="text-xs font-mono uppercase text-muted tracking-wider block mb-3">
              {locale === 'de' ? 'Wichtige öffentliche Bereiche' : 'Key Public Spaces & Venues'}
            </span>
            <div className="flex flex-wrap gap-2">
              {vessel.highlights.map((h) => (
                <span
                  key={h}
                  className="text-xs bg-paper px-3.5 py-1.5 rounded-xs border border-ink/6 text-ink/85 font-medium"
                >
                  {h}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* Strategic Calling Ports */}
        {callingPorts.length > 0 && (
          <section className="bg-white border border-ink/8 p-8 sm:p-10 rounded-xs shadow-xs">
            <p className="eyebrow text-gold">{locale === 'de' ? 'Routen-Verbindungen' : 'Itinerary Connections'}</p>
            <h2 className="font-display text-3xl text-ink font-normal mt-1 mb-6">
              {t.ports.title}
            </h2>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              {callingPorts.map((port) => (
                <div key={port.slug} className="bg-paper/50 p-4 rounded-xs border border-ink/6">
                  <div className="flex items-center gap-1.5 text-xs font-mono text-gold font-medium mb-1">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{port.unLocode}</span>
                  </div>
                  <h3 className="font-display text-lg text-ink">{port.name.split('(')[0].trim()}</h3>
                  <p className="text-xs text-muted mt-1">{port.terminalPier}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Provenance & Sources */}
        <section className="bg-paper/60 border border-ink/8 p-8 rounded-xs">
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-ink font-semibold mb-2">
            <ShieldCheck className="w-4 h-4 text-emerald-700" />
            <span>{locale === 'de' ? 'Rückverfolgbare maritime Provenienz' : 'Traceable Maritime Provenance'}</span>
          </div>
          <p className="text-xs text-muted leading-relaxed">
            {locale === 'de'
              ? `Alle Abmessungen, Deckpläne und Kabinengrenzen für ${vessel.name} basieren auf offiziellen Werft-Dossiers von ${vessel.builder} und dem IMO-Register ${vessel.imo}.`
              : `All dimensions, deck counts, and stateroom bounds for ${vessel.name} are anchored in official shipyard delivery technical dossiers from ${vessel.builder} and IMO Registry ${vessel.imo}.`}
          </p>
          <div className="mt-4 flex items-center gap-3">
            <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-xs font-medium">
              🟢 {locale === 'de' ? 'OFFIZIELLES REGISTER' : 'OFFICIAL REGISTRY'}
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 bg-sky-100 text-sky-800 rounded-xs font-medium">
              🔵 {locale === 'de' ? 'KLASSEN-MODELL' : 'REFERENCE MODEL'}
            </span>
          </div>
        </section>

        {/* Related Fleet Twins */}
        <section>
          <div className="text-xs font-mono uppercase tracking-widest text-muted/70 mb-6 pb-2 border-b border-ink/6">
            <span>{locale === 'de' ? 'Weitere Referenzmodelle' : 'Explore Other Reference Models'}</span>
          </div>
          <div className="grid sm:grid-cols-3 gap-6">
            {relatedShips.map((other) => (
              <button
                key={other.slug}
                onClick={() => onSelectShip(other.slug)}
                className="text-left bg-white p-5 rounded-xs border border-ink/8 hover:border-ink/20 transition-all group cursor-pointer shadow-xs"
              >
                <span className="text-[10px] font-mono text-gold uppercase">{other.roleTitle}</span>
                <h4 className="font-display text-xl text-ink mt-1 group-hover:text-gold transition-colors">
                  {other.name}
                </h4>
                <p className="text-xs text-muted mt-1">{other.shipClass}</p>
                <div className="mt-4 text-xs font-mono text-ink flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  <span>{locale === 'de' ? 'Schiff ansehen' : 'View ship'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </button>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
